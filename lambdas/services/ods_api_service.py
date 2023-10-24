import logging
from typing import Dict, List, NamedTuple, Optional

import requests
from enums.permitted_role import PermittedRole
from utils.exceptions import OdsErrorException, OrganisationNotFoundException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Organisation(NamedTuple):
    org_name: str
    ods_code: str
    role: str


class OdsApiService:
    # A service to fetch info from NHS Organisation Data Service (ODS) Organisation Reference Data (ORD) API
    ORD_API_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"
    
    @classmethod
    def is_gpp_org(cls, ods_code: str):
        org_details = cls.fetch_organisation_data(ods_code)

        try:
            json_roles: List[Dict] = org_details["Organisation"]["Roles"]["Role"]

            for json_role in json_roles:
                if json_role["id"] in PermittedRole.list():
                    return True
            return False

        except KeyError:
            logger.info(f"Got response from ODS in unexpected format: {response_json}")
            return False
        
        
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
            logger.info(
                f"Got error response from ODS API with ods code {ods_code}: {response}"
            )
            raise OdsErrorException("Failed to fetch organisation data from ODS")

