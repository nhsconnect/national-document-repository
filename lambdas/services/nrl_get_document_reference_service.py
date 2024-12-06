from urllib.error import HTTPError

import requests
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.request_context import request_context
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class NRLGetDocumentReferenceService:

    # Needs PDS now, so oauth and ssm, may need declaring the handler

    def __init__(self):
        self.ssm_service = SSMService()
        self.pds_service = get_pds_service()
        # question about ssm_service as above function calls one...
        # dynamo_service
        # dynamo_table
        # document_service? not using NHS_numbers, using table ids
        self.ssm_prefix = getattr(request_context, "auth_ssm_prefix", "")

    def user_allowed_to_see_file(self, bearer_token):

        user = self.fetch_user_info(bearer_token)
        self.get_user_role_and_ods(user)

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

    def get_ndr_accepted_role_codes(self):
        pass

    def get_user_roles_and_ods_codes(self, user_info) -> list[dict[str, str]]:

        # ods_codes_and_roles = []
        #
        # nrbac_roles = user_info.get("nhsid_nrbac_roles", []);
        #
        # for role in nrbac_roles:
        #     ods_code = role["org_code"]
        #     role_code = self.process_role_code(role["role_code"])

        # get all roles, loop through, get ods and role code,
        # check these against doc ref ods and role codes stored in ssm of both clinical and admin
        pass

    def process_role_code(self, role_codes) -> str:
        role_codes_split = role_codes.split(":")
        for role_code in role_codes_split:
            if role_code[0].upper() == "R":
                return role_code

    def get_dynamo_table_to_search_for_patient(self, snomed_code):
        pass

    def patient_is_active(self, current_gp_ods_code):
        pass

    def get_document_reference(self, table, id):
        pass

    def get_patient_current_gp(self, nhs_number):
        pass

    def generate_cloud_front_url(self):
        pass
