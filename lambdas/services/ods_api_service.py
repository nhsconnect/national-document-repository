import logging
from typing import Optional, List, Dict, Tuple, TypeAlias

import requests

from enums.permitted_role import PermittedRole
from utils.exceptions import OrganisationNotFoundException, OdsErrorException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

OdsCode: TypeAlias = str
OrganisationName: TypeAlias = str
Organisation: TypeAlias = Tuple[OdsCode, OrganisationName, PermittedRole]


class OdsApiService:
    # A service to fetch info from NHS Organisation Data Service (ODS) Organisation Reference Data (ORD) API
    ORD_API_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"

    @classmethod
    def fetch_organisation_data(cls, ods_code: str):
        response = requests.get(f"{cls.ORD_API_URL}/{ods_code}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise OrganisationNotFoundException(
                "Organisation does not exist for given ODS code"
            )
        else:
            raise OdsErrorException("Failed to fetch organisation data from ODS")

    @classmethod
    def parse_ods_response(cls, response_json) -> Optional[Organisation]:
        try:
            org_name = response_json["Organisation"]["Name"]
            org_ods_code = response_json["Organisation"]["OrgId"]["extension"]

            json_roles: List[Dict] = response_json["Organisation"]["Roles"]["Role"]

            for json_role in json_roles:
                if json_role["id"] in PermittedRole.list():
                    # early return with the first permitted role found
                    return org_name, org_ods_code, PermittedRole(json_role["id"])

            logger.info("No permitted role was found for given ods code")
            return None

        except KeyError:
            logger.info("Got response from ODS in unexpected format")
            return None

    @classmethod
    def fetch_permitted_organisation_and_role_data(
        cls, ods_code_list: list[OdsCode]
    ) -> List[Organisation]:
        ods_response_list = [
            cls.fetch_organisation_data(ods_code) for ods_code in ods_code_list
        ]

        return [
            valid_org := cls.parse_ods_response(res)
            for res in ods_response_list
            if valid_org
        ]
