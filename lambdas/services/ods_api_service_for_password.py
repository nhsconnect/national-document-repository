import logging
from typing import Dict, List, Optional

from enums.permitted_role import PermittedRole
from services.ods_api_service import OdsApiService, Organisation

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

    def parse_ods_response(self, response_json) -> Optional[Organisation]:
        try:
            org_name = response_json["Organisation"]["Name"]
            ods_code = response_json["Organisation"]["OrgId"]["extension"]

            json_roles: List[Dict] = response_json["Organisation"]["Roles"]["Role"]

            for json_role in json_roles:
                if json_role["id"] in PermittedRole.list():
                    # early return with the first permitted role found. convert role code to role name as well.
                    return Organisation(
                        org_name=org_name,
                        ods_code=ods_code,
                        role=PermittedRole(json_role["id"]).name,
                    )

            return None

        except KeyError:
            logger.info(f"Got response from ODS in unexpected format: {response_json}")
            return None
