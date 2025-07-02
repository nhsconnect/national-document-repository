from enums.virus_scan_result import VirusScanResult


class MockVirusScanService:
    def __init__(self):
        pass

    def scan_file(self, file_ref: str):
        if file_ref.endswith("1"):
            return VirusScanResult.INFECTED
        return VirusScanResult.CLEAN
