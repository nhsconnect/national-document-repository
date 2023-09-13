import requests

from utils.exceptions import OrganisationNotFoundException, OdsErrorException


class OdsApiService:
    # A service to fetch info from NHS Organisation Data Service (ODS) Organisation Reference Data (ORD) API
    ORD_API_URL = "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"
    @classmethod
    def fetch_organisation_data(cls, ods_code: str):
        response = requests.get(f"{cls.ORD_API_URL}/{ods_code}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise OrganisationNotFoundException("Organisation does not exist for given ODS code")
        else:
            raise OdsErrorException('Failed to fetch organisation data from ODS')

