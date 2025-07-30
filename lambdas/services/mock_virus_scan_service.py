import os

from enums.virus_scan_result import VirusScanResult
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)

NHS_NUMBERS_INFECTED_FILES = [
    "9000000114",
    "9000000084",
    "9000000122",
    "9730153973",
    "9730154341",
    "9730154066",
    "9730154708",
    "9730154260",
]


class MockVirusScanService:
    def __init__(self):
        logger.info("Virus scan service is set to mock virus scan service")

        infected_nhs_numbers_str = os.getenv("INFECTED_NHS_NUMBERS")
        self.infected_nhs_numbers = (
            infected_nhs_numbers_str.split(",")
            if infected_nhs_numbers_str
            else NHS_NUMBERS_INFECTED_FILES
        )
        if self.infected_nhs_numbers:
            logger.info(f"Infected NHS numbers are set to: {self.infected_nhs_numbers}")

    def scan_file(self, file_ref: str, *args, **kwargs) -> VirusScanResult:
        nhs_number = kwargs.get("nhs_number")
        if nhs_number and nhs_number in self.infected_nhs_numbers:
            logger.info(
                f"File for NHS number '{nhs_number}' is marked as infected by mock service."
            )
            return VirusScanResult.INFECTED
        logger.info(f"File '{file_ref}' is marked as clean by mock service.")
        return VirusScanResult.CLEAN
