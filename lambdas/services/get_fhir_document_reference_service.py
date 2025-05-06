import os

from enums.lambda_error import LambdaError
from enums.snomed_codes import SnomedCodes
from models.document_reference import DocumentReference
from models.fhir.R4.fhir_document_reference import Attachment, DocumentReferenceInfo
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from services.document_service import DocumentService
from services.search_patient_details_service import SearchPatientDetailsService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import (
    GetFhirDocumentReferenceException,
    SearchPatientException,
)
from utils.request_context import request_context
from utils.utilities import format_cloudfront_url

logger = LoggingService(__name__)


class GetFhirDocumentReferenceService:
    def __init__(self, user_role, user_ods_code):
        self.tables = {
            SnomedCodes.LLOYD_GEORGE.value.code: os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        }
        self.ssm_prefix = getattr(request_context, "auth_ssm_prefix", "")
        get_document_presign_url_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")
        self.s3_service = S3Service(
            custom_aws_role=get_document_presign_url_aws_role_arn
        )
        self.ssm_service = SSMService()
        self.document_service = DocumentService()
        self.search_patient_service = SearchPatientDetailsService(
            user_role, user_ods_code
        )

    def handle_get_document_reference_request(self, snomed_code, document_id):
        table = self.tables.get(snomed_code, None)
        if not table:
            raise GetFhirDocumentReferenceException(
                404, LambdaError.DocumentReferenceNotFound
            )
        document_reference = self.get_document_references(document_id, table)
        try:
            self.search_patient_service.handle_search_patient_request(
                document_reference.nhs_number, True
            )
        except SearchPatientException:
            raise GetFhirDocumentReferenceException(
                403, LambdaError.DocumentReferenceForbidden
            )

        presign_url = self.create_document_presigned_url(document_reference)
        response = self.create_document_reference_fhir_response(
            document_reference, presign_url
        )
        return response

    def get_document_references(self, document_id: str, table) -> DocumentReference:
        documents = self.document_service.fetch_documents_from_table(
            table=table,
            search_condition=document_id,
            search_key="ID",
        )
        if len(documents) > 0:
            return documents[0]
        else:
            raise GetFhirDocumentReferenceException(
                404, LambdaError.DocumentReferenceNotFound
            )

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
