import logging
from typing import Dict, List, Optional

from enums.permitted_role import PermittedRole
from services.ods_api_service import OdsApiService, Organisation
from utils.exceptions import TooManyOrgsException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# TODO Move this to SSM
PCSE_ODS_CODE_TO_BE_PUT_IN_PARAM_STORE = "X4S4L"


class OdsApiServiceForSmartcard(OdsApiService):
    def parse_ods_response(self, org_data, role_code) -> Optional[Organisation]:
        return { "name" : org_data["Organisation"]["Name"], 
                 "org_ods_code" : ["Organisation"]["OrgId"]["extension"],
                 "role_code" : role_code}


    def fetch_organisation_with_permitted_role(
        self, ods_code_list: list[str]
    ) -> Dict:
        logger.info(f"ODS code list for smartcard login: {ods_code_list}")

        logger.info(f"length: {len(ods_code_list)} ")
        if len(ods_code_list) != 1:
            raise TooManyOrgsException

        ods_code = ods_code_list[0]
        logger.info(f"ods_code selected: {ods_code}")

        org_data = self.fetch_organisation_data(ods_code)

        logger.info(f"Org Data: {org_data}")
        if is_pcse_ods(org_data) or is_gpp_org(org_data):
            logger.info(f"ODS code {ods_code} is a GPP or PCSE, returning org data")
            return self.parse_ods_response(org_data, ods_code)
        else:
            logger.info(
                f"ODS code {ods_code} is not a GPP or PCSE, returning empty list"
            )
            return {}


def is_gpp_org(org_details):
    json_roles: List[Dict] = org_details["Organisation"]["Roles"]["Role"]

    for json_role in json_roles:
        # TODO use gp role from ssm
        if json_role["id"] in PermittedRole.list():
            return True
    return False

def is_pcse_ods(org_details):
    json_roles: List[Dict] = org_details["Organisation"]["Roles"]["Role"]

    for json_role in json_roles:
        # TODO use gp role from ssm
        if json_role["id"] == PCSE_ODS_CODE_TO_BE_PUT_IN_PARAM_STORE:
            return True
    return False
