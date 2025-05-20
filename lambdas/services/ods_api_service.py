from typing import Any, Dict, List, NamedTuple, Optional

import requests
from enums.lambda_error import LambdaError
from enums.repository_role import OrganisationRelationship
from services.base.ssm_service import SSMService
from services.token_handler_ssm_service import TokenHandlerSSMService
from utils.audit_logging_setup import LoggingService
from utils.constants.ssm import GP_ORG_ROLE_CODE
from utils.exceptions import (
    OdsErrorException,
    OrganisationNotFoundException,
    TooManyOrgsException,
)
from utils.lambda_exceptions import LoginException

logger = LoggingService(__name__)

token_handler_ssm_service = TokenHandlerSSMService()
ssm_service = SSMService()


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

    def fetch_organisation_with_permitted_role(self, ods_code_list: list[str]) -> Dict:
        logger.info(f"ODS code list for smartcard login: {ods_code_list}")

        logger.info(f"length: {len(ods_code_list)} ")
        if len(ods_code_list) != 1:
            raise TooManyOrgsException(
                "No single organisation found for identified ods codes"
            )

        ods_code = ods_code_list[0]
        logger.info(f"ods_code selected: {ods_code}")

        itoc_ods_codes = token_handler_ssm_service.get_itoc_ods_codes()

        if ods_code in itoc_ods_codes:
            logger.info(f"ODS code {ods_code} is ITOC, returning org data")
            itoc_org_data = {"Organisation": {"OrgId": {"extension": ods_code}}}
            return parse_ods_response(itoc_org_data, "", "ITOC")

        org_data = self.fetch_organisation_data(ods_code)

        logger.info(f"Org Data: {org_data}")

        gp_org_role_code = get_user_gp_org_role_code(org_data)

        if gp_org_role_code is not None:
            logger.info(f"ODS code {ods_code} is a GP, returning org data")
            icb_ods_code = find_icb_for_user(org_data["Organisation"])
            response = parse_ods_response(org_data, gp_org_role_code, icb_ods_code)
            return response

        pcse_ods_code = token_handler_ssm_service.get_pcse_ods_code()

        if ods_code == pcse_ods_code:
            logger.info(f"ODS code {ods_code} is PCSE, returning org data")
            response = parse_ods_response(org_data, "", "PCSE")
            return response

        allowed_ods_code_list = (
            token_handler_ssm_service.get_allowed_list_of_ods_codes()
        )

        if ods_code in allowed_ods_code_list:
            logger.info(f"ODS code {ods_code} is in allowed list, returning org data")
            icb_ods_code = find_icb_for_user(org_data["Organisation"])
            primary_org_role_code = get_user_primary_org_role_code(org_data)
            response = parse_ods_response(org_data, primary_org_role_code, icb_ods_code)
            return response

        logger.info(
            f"ODS code {ods_code} is not a GP, PCSE, ITOC nor in allowed list, returning empty list"
        )
        return {}


def parse_ods_response(org_data, role_code, icb_ods_code) -> dict:
    org_name = org_data.get("Organisation", {}).get("Name", "")
    org_ods_code = (
        org_data.get("Organisation", {}).get("OrgId", {}).get("extension", "")
    )

    response_dictionary = {
        "name": org_name,
        "org_ods_code": org_ods_code,
        "role_code": role_code,
        "icb_ods_code": icb_ods_code,
    }
    logger.info(f"Response: {response_dictionary}")

    return response_dictionary


def get_user_gp_org_role_code(org_data: Dict[str, Any]) -> Optional[str]:
    logger.info("starting ssm request to retrieve GP organisation role code")
    gp_org_role_code = ssm_service.get_ssm_parameter(GP_ORG_ROLE_CODE)

    if gp_org_role_code:
        logger.info("Checking if GP organisation role is present")
        json_roles: List[Dict] = org_data["Organisation"]["Roles"]["Role"]
        for json_role in json_roles:
            if json_role["id"] == gp_org_role_code:
                return json_role["id"]
        return None

    logger.error(
        LambdaError.LoginGpOrgRoleCode.to_str(),
        {"Result": "Unsuccessful login"},
    )
    raise LoginException(500, LambdaError.LoginGpOrgRoleCode)


def get_user_primary_org_role_code(org_data: Dict[str, Any]) -> str:
    logger.info("Checking if a primary organisation role is present")
    json_roles: List[Dict] = org_data["Organisation"]["Roles"]["Role"]

    for json_role in json_roles:
        if "primaryRole" in json_role:
            return json_role["id"]
    return ""


def find_icb_for_user(org_data: Dict[str, Any]) -> str:
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
