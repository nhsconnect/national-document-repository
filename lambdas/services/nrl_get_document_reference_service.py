import os
from urllib.error import HTTPError

import requests
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from models.document_reference import DocumentReference
from services.base.dynamo_service import DynamoDBService
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import NRLGetDocumentReferenceException
from utils.request_context import request_context
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class NRLGetDocumentReferenceService:

    # Needs PDS now, so oauth and ssm, may need declaring the handler

    def __init__(self):
        self.ssm_service = SSMService()
        self.pds_service = get_pds_service()
        # question about ssm_service as above function calls one...
        self.dynamo_service = DynamoDBService()
        self.table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        # document_service? not using NHS_numbers, using table ids
        self.ssm_prefix = getattr(request_context, "auth_ssm_prefix", "")

    def user_allowed_to_see_file(self, bearer_token, id):

        user = self.fetch_user_info(bearer_token)
        user_ods_codes_and_roles = self.get_user_roles_and_ods_codes(user)

        document_reference = self.get_document_references(id)
        patient_current_gp_ods_code = self.get_patient_current_gp_ods(
            document_reference.nhs_number
        )

        if self.patient_is_inactive(patient_current_gp_ods_code):
            return False

        for ods_code, roles in user_ods_codes_and_roles.items():
            if ods_code == patient_current_gp_ods_code:
                for role in roles:
                    return role in self.get_ndr_accepted_role_codes()

    #   first check user has a role with correct ods code
    #   second check that the role id associated with this ods is in our accepted roles

    def fetch_user_info(self, bearer_token) -> dict:
        logger.info(f"Fetching user info with bearer token: {bearer_token}")
        request_url = self.ssm_prefix + self.ssm_service.get_ssm_parameter(
            "OIDC_USER_INFO_URL"
        )

        try:
            response = requests.get(
                url=request_url, headers={"Authorization": f"Bearer {bearer_token}"}
            )
            response.raise_for_status()

            return response.json()

        except HTTPError as error:
            print(error)
            # Check status code, and raise?
            pass

    def get_ndr_accepted_role_codes(self) -> list[str]:
        roles = []
        ssm_parameters = self.ssm_service.get_ssm_parameters(
            parameters_keys=[
                "/auth/smartcard/role/gp_admin",
                "/auth/smartcard/role/gp_clinical",
            ]
        )

        for key, value in ssm_parameters.items():
            for role in value:
                roles.append(role)
        return roles

    def get_user_roles_and_ods_codes(self, user_info) -> list[dict[str, str]]:

        ods_codes_and_roles = {}

        nrbac_roles = user_info.get("nhsid_nrbac_roles", [])

        for role in nrbac_roles:
            ods_code = role["org_code"]
            role_code = self.process_role_code(role["role_code"])
            if ods_code in ods_codes_and_roles:
                ods_codes_and_roles[ods_code].append(role_code)
            else:
                ods_codes_and_roles[ods_code] = [role_code]

        return ods_codes_and_roles

    def process_role_code(self, role_codes) -> str:
        role_codes_split = role_codes.split(":")
        for role_code in role_codes_split:
            if role_code[0].upper() == "R":
                return role_code

    def get_dynamo_table_to_search_for_patient(self, snomed_code):
        pass

    def patient_is_inactive(self, current_gp_ods_code):
        return current_gp_ods_code in PatientOdsInactiveStatus

    def get_document_references(self, id: str) -> DocumentReference:

        table_item = self.dynamo_service.query_table_by_index(
            table_name=self.table,
            index_name=DocumentReferenceMetadataFields.ID,
            search_key=DocumentReferenceMetadataFields.ID,
            search_condition=id,
        )
        if len(table_item["Items"]) > 0:
            return DocumentReference.model_validate(table_item["Items"][0])
        else:
            raise NRLGetDocumentReferenceException(
                message="No document references found",
                status_code=404,
            )

    #   otherwise we don't have the patient, and want to return what status code? do that here?
    # or raise/throw an error that the handler catches and returns the api gateway.

    def get_patient_current_gp_ods(self, nhs_number):
        patient_details = self.pds_service.fetch_patient_details(nhs_number)
        return patient_details.general_practice_ods

    #     seeing as we're calling pds here, do we want to update our table at the same time?

    def generate_cloud_front_url(self):
        pass
