from enums.virus_scan_result import VirusScanResult
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class MockVirusScanService:
    def __init__(self):
        logger.info("Virus scan service is set to mock virus scan service")

    def scan_file(self, file_ref: str):
        if file_ref.endswith("1"):
            logger.info("Virus scan file is marked as infected")
            return VirusScanResult.INFECTED
        return VirusScanResult.CLEAN
