from typing import Dict, List, NamedTuple

import requests
from enums.repository_role import OrganisationRelationship
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (
    OdsErrorException,
    OrganisationNotFoundException,
    TooManyOrgsException,
)

logger = LoggingService(__name__)

token_handler_ssm_service = TokenHandlerSSMService()


class Organisation(NamedTuple):
    org_name: str
    ods_code: str
    role: str


class OdsApiService:
    # A service to fetch info from NHS Organisation Data Service (ODS) Organisation Reference Data (ORD) API
    ORD_API_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations"

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

    def fetch_organisation_with_permitted_role(self, ods_code: str) -> Dict:

        if ods_code == "":
            raise TooManyOrgsException(
                "No single organisation found for identified ods codes"
            )

        logger.info(f"ods_code selected: {ods_code}")

        org_data = self.fetch_organisation_data(ods_code)

        logger.info(f"Org Data: {org_data}")

        pcse_ods = find_and_get_pcse_ods(ods_code)

        if pcse_ods is not None:
            logger.info(f"ODS code {ods_code} is PCSE, returning org data")
            response = parse_ods_response(org_data, "", "PCSE")
            return response

        gpp_org = find_and_get_gpp_org_code(org_data)

        if gpp_org is not None:
            logger.info(f"ODS code {ods_code} is a GPP, returning org data")
            icb_ods_code = find_icb_for_user(org_data["Organisation"])
            response = parse_ods_response(org_data, gpp_org, icb_ods_code)
            return response

        logger.info(f"ODS code {ods_code} is not a GPP or PCSE, returning empty list")
        return {}


def parse_ods_response(org_data, role_code, icb_ods_code) -> dict:
    org_name = org_data["Organisation"]["Name"]
    org_ods_code = org_data["Organisation"]["OrgId"]["extension"]

    response_dictionary = {
        "name": org_name,
        "org_ods_code": org_ods_code,
        "role_code": role_code,
        "icb_ods_code": icb_ods_code,
    }
    logger.info(f"Response: {response_dictionary}")

    return response_dictionary


def find_and_get_gpp_org_code(org_details):
    logger.info("Checking GPP Roles")
    json_roles: List[Dict] = org_details["Organisation"]["Roles"]["Role"]

    org_role_codes = token_handler_ssm_service.get_org_role_codes()
    for json_role in json_roles:
        if json_role["id"] in org_role_codes:
            return json_role["id"]
    return None


def find_and_get_pcse_ods(ods_code):
    logger.info("Checking PCSE Roles")
    if ods_code == token_handler_ssm_service.get_org_ods_codes()[0]:
        return ods_code
    return None


def find_icb_for_user(org_data):
    logger.info("Checking relationships")
    try:
        relationships: List[Dict] = org_data["Rels"]["Rel"]
        for rel in relationships:
            if (
                rel["Status"] == "Active"
                and rel["id"] == OrganisationRelationship.COMMISSIONED_BY
                and rel["Target"]["PrimaryRoleId"]["id"]
                == OrganisationRelationship.CLINICAL_COMMISSIONING_GROUP
            ):
                icb_ods_code = rel["Target"]["OrgId"]["extension"]
                logger.info(f"Found ICB code for user: {icb_ods_code}")
                return icb_ods_code
    except (KeyError, TypeError):
        logger.info("Failure fetching relationships")
    return "No ICB code found"
