from services.ods_api_service import OdsApiService
from typing_extensions import override
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class MockOdsApiService(OdsApiService):
    def __init__(self):
        super().__init__()

    @override
    def fetch_organisation_data(self, org_ods_codes: list[str]) -> dict:
        # TODO - Mock ODS api call and return supplemented org data dict
        # Make real call to ODS api to capture JSON response and use as template
        # for our mocked responses to match the fake CIS2 patient's ODS code
        response = {}
        logger.info(f"Response: {response}")
        return response
