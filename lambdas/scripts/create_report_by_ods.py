import os

from services.ods_report_service import OdsReportService

if __name__ == "__main__":
    ods_code = "_"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "_LloydGeorgeReferenceMetadata"
    print("Starting process for ods code: %s", ods_code)
    service = OdsReportService()
    service.get_nhs_numbers_by_ods(ods_code)


