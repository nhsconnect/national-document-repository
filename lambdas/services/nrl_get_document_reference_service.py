import os

import requests
from enums.lambda_error import LambdaError
from models.document_reference import DocumentReference
from models.fhir.R4.nrl_fhir_document_reference import Attachment, DocumentReferenceInfo
from requests.exceptions import HTTPError
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.constants.ssm import GP_ADMIN_USER_ROLE_CODES, GP_CLINICAL_USER_ROLE_CODE
from utils.lambda_exceptions import NRLGetDocumentReferenceException
from utils.ods_utils import extract_ods_role_code_with_r_prefix_from_role_codes_string
from utils.request_context import request_context
from utils.utilities import format_cloudfront_url, get_pds_service

logger = LoggingService(__name__)


class NRLGetDocumentReferenceService:
    def __init__(self):
        self.table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.ssm_prefix = getattr(request_context, "auth_ssm_prefix", "")
        get_document_presign_url_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")
        self.s3_service = S3Service(
            custom_aws_role=get_document_presign_url_aws_role_arn
        )
        self.ssm_service = SSMService()
        self.pds_service = get_pds_service()
        self.document_service = DocumentService()

    def handle_get_document_reference_request(self, document_id, bearer_token):
        document_reference = self.get_document_references(document_id)
        user_details = self.fetch_user_info(bearer_token)

        if not self.is_user_allowed_to_see_file(user_details, document_reference):
            raise NRLGetDocumentReferenceException(
                403, LambdaError.DocumentReferenceUnauthorised
            )

        presign_url = self.create_document_presigned_url(document_reference)
        response = self.create_document_reference_fhir_response(
            document_reference, presign_url
        )
        return response

    def get_document_references(self, document_id: str) -> DocumentReference:
        documents = self.document_service.fetch_documents_from_table(
            table=self.table,
            search_condition=document_id,
            search_key="ID",
        )
        if len(documents) > 0:
            return documents[0]
        else:
            raise NRLGetDocumentReferenceException(
                404, LambdaError.DocumentReferenceNotFound
            )

    def fetch_user_info(self, bearer_token) -> dict:
        logger.info(f"Fetching user info with bearer token: {bearer_token[-4:]}")
        request_url = self.ssm_service.get_ssm_parameter(
            self.ssm_prefix + "OIDC_USER_INFO_URL"
        )

        try:
            response = requests.get(
                url=request_url, headers={"Authorization": f"Bearer {bearer_token}"}
            )
            response.raise_for_status()
            return response.json()

        except HTTPError as error:
            logger.error(f"HTTP error {error.response.content}")
            raise NRLGetDocumentReferenceException(
                400, LambdaError.DocumentReferenceGeneralError
            )

    def is_user_allowed_to_see_file(self, user_details, document_reference):
        user_ods_codes_and_roles = self.get_user_roles_and_ods_codes(user_details)
        patient_details = self.pds_service.fetch_patient_details(
            document_reference.nhs_number
        )

        patient_current_gp_ods_code = patient_details.general_practice_ods
        if not patient_details.active:
            return False

        if patient_current_gp_ods_code in user_ods_codes_and_roles:
            accepted_roles = self.get_ndr_accepted_role_codes()
            return any(
                role in accepted_roles
                for role in user_ods_codes_and_roles[patient_current_gp_ods_code]
            )

    def get_user_roles_and_ods_codes(self, user_info) -> dict[str, list[str]]:
        ods_codes_and_roles = {}
        nrbac_roles = user_info.get("nhsid_nrbac_roles", [])

        for role in nrbac_roles:
            ods_code: str = role["org_code"]
            role_code = extract_ods_role_code_with_r_prefix_from_role_codes_string(
                role["role_code"]
            )
            ods_codes_and_roles.setdefault(ods_code, []).append(role_code)
        return ods_codes_and_roles

    def get_ndr_accepted_role_codes(self) -> list[str]:
        ssm_parameters = self.ssm_service.get_ssm_parameters(
            parameters_keys=[
                GP_ADMIN_USER_ROLE_CODES,
                GP_CLINICAL_USER_ROLE_CODE,
            ]
        )
        return [role for roles in ssm_parameters.values() for role in roles.split(",")]

    def create_document_presigned_url(self, document_reference: DocumentReference):
        bucket_name = document_reference.get_file_bucket()
        file_location = document_reference.get_file_key()
        presign_url_response = self.s3_service.create_download_presigned_url(
            s3_bucket_name=bucket_name,
            file_key=file_location,
        )
        return format_cloudfront_url(presign_url_response, self.cloudfront_url)

    def create_document_reference_fhir_response(
        self, document_reference: DocumentReference, presign_url: str
    ) -> str:
        document_details = Attachment(
            url=presign_url,
            title=document_reference.file_name,
            creation=document_reference.created,
        )
        fhir_document_reference = (
            DocumentReferenceInfo(
                nhsNumber=document_reference.nhs_number,
                custodian=document_reference.current_gp_ods,
                attachment=document_details,
            )
            .create_fhir_document_reference_object()
            .model_dump_json(exclude_none=True)
        )
        return fhir_document_reference
