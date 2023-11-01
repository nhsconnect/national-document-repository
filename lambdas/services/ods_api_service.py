import logging
from typing import Dict, List, NamedTuple, Optional

import requests
from lambdas.services.token_handler_ssm_service import TokenHandlerSSMService
from utils.exceptions import OdsErrorException, OrganisationNotFoundException, TooManyOrgsException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

token_handler_ssm_service = TokenHandlerSSMService()
class Organisation(NamedTuple):
    org_name: str
    ods_code: str
    role: str


class OdsApiService:
    # A service to fetch info from NHS Organisation Data Service (ODS) Organisation Reference Data (ORD) API
    ORD_API_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"

    def fetch_organisation_data(self, ods_code: str):
        response = requests.get(f"{self.ORD_API_URL}/{ods_code}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise OrganisationNotFoundException(
                "Organisation does not exist for given ODS code"
            )
        else:
            logger.info(
                f"Got error response from ODS API with ods code {ods_code}: {response}"
            )
            raise OdsErrorException("Failed to fetch organisation data from ODS")
    
    def parse_ods_response(self, org_data, role_code) -> dict:

        org_name = org_data["Organisation"]["Name"]
        logger.info(f"Organisation Name: {org_name}")

        org_ods_code = org_data["Organisation"]["OrgId"]["extension"]
        logger.info(f"Organisation Org Code: {org_ods_code}")

        logger.info(f"Role code: {role_code}")
        response_dictionary = { "name" : org_name, 
                 "org_ods_code" : org_ods_code,
                 "role_code" : role_code }
        
        return response_dictionary


    def fetch_organisation_with_permitted_role(
        self, ods_code_list: list[str]
    ) -> Dict:
        logger.info(f"ODS code list for smartcard login: {ods_code_list}")

        logger.info(f"length: {len(ods_code_list)} ")
        if len(ods_code_list) != 1:
            raise TooManyOrgsException("No single organisation found for identified ods codes")

        ods_code = ods_code_list[0]
        logger.info(f"ods_code selected: {ods_code}")

        org_data = self.fetch_organisation_data(ods_code)

        logger.info(f"Org Data: {org_data}")

        pcse_ods = find_and_get_pcse_ods(ods_code)
        gpp_ods = find_and_get_gpp_org(org_data)

        if pcse_ods is not None: 
            logger.info(f"ODS code {ods_code} is a PCSE, returning org data")
            response = self.parse_ods_response(org_data, pcse_ods)
            return response

        if gpp_ods is not None: 
            logger.info(f"ODS code {ods_code} is a GPP, returning org data")
            response = self.parse_ods_response(org_data, gpp_ods)
            return response
        
        logger.info(
            f"ODS code {ods_code} is not a GPP or PCSE, returning empty list"
        )
        return {}


def find_and_get_gpp_org(org_details):
    logger.info("Checking GPP Roles")
    json_roles: List[Dict] = org_details["Organisation"]["Roles"]["Role"]

    org_role_codes= token_handler_ssm_service.get_org_role_codes()
    for json_role in json_roles:
        if json_role["id"] in org_role_codes:
            return json_role["id"]
    return None

def find_and_get_pcse_ods(ods_code):
    logger.info("Checking PCSE Roles")
    if ods_code == token_handler_ssm_service.get_org_ods_codes()[0]: 
        return ods_code
    return None

