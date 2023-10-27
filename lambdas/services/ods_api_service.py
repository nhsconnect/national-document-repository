import logging
from typing import Dict, List, NamedTuple, Optional

import requests
from enums.permitted_role import PermittedRole
from models.oidc_models import AccessToken
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

    def fetch_organisation_with_permitted_role(
            self, ods_code_list: list[str]
    ) -> List[Dict]:
        raise NotImplementedError

    def parse_ods_response(self, response_json) -> Optional[Organisation]:
        logger.info(response_json);
        try:
            org_name = response_json["Organisation"]["Name"]
            ods_code = response_json["Organisation"]["OrgId"]["extension"]

            json_roles: List[Dict] = response_json["Organisation"]["Roles"]["Role"]

            for json_role in json_roles:
                if json_role["id"] in PermittedRole.list():
                    # early return with the first permitted organistation type found. Convert organisation role code to role type as well e.g. RO76 -> GP.
                    return Organisation(
                        org_name=org_name,
                        ods_code=ods_code,
                        role=PermittedRole(json_role["id"]).name,
                    )

            return None

        except KeyError:
            logger.info(f"Got response from ODS in unexpected format: {response_json}")
            return None
