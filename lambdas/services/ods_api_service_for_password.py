import logging
from typing import Dict, List

from services.ods_api_service import OdsApiService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class OdsApiServiceForPassword(OdsApiService):
    def fetch_organisation_with_permitted_role(
        self, ods_code_list: list[str]
    ) -> List[Dict]:
        valid_orgs = []
        for ods_code in ods_code_list:
            response = self.fetch_organisation_data(ods_code)
            organisation_info = self.parse_ods_response(response)
            if organisation_info is not None:
                valid_orgs.append(organisation_info._asdict())

        return valid_orgs
