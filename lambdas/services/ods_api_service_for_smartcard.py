import logging
from abc import ABC
from typing import Dict, List, NamedTuple, Optional

import requests
from enums.permitted_role import PermittedRole
from services.ods_api_service import OdsApiService, Organisation
from utils.exceptions import OdsErrorException, OrganisationNotFoundException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class OdsApiServiceForSmartcard(OdsApiService):

    def parse_ods_response(self, response_json) -> Optional[Organisation]:
        pass

    def fetch_organisation_with_permitted_role(self, ods_code_list: list[str]) -> List[Dict]:
        pass

    def token_request(self, oidc_service, event):
        pass

    def is_gpp_org(self, ods_code: str):
        org_details = self.fetch_organisation_data(ods_code)

        json_roles: List[Dict] = org_details["Organisation"]["Roles"]["Role"]

        for json_role in json_roles:
            if json_role["id"] in PermittedRole.list():
                return True
            else:
                return False
