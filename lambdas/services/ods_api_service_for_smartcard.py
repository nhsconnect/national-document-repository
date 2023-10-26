import logging
from abc import ABC
from typing import Dict, List, NamedTuple, Optional

import requests
from enums.permitted_role import PermittedRole
from services.ods_api_service import OdsApiService
from utils.exceptions import OdsErrorException, OrganisationNotFoundException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class OdsApiServiceForSmartcard(OdsApiService):

    @classmethod
    def is_gpp_org(cls, ods_code: str):
        org_details = cls.fetch_organisation_data(ods_code)

        json_roles: List[Dict] = org_details["Organisation"]["Roles"]["Role"]

        for json_role in json_roles:
            if json_role["id"] in PermittedRole.list():
                return True
            else:
                return False
