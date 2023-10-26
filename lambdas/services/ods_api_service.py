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
            )   # TODO AKH Uncaught
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
        raise NotImplementedError
