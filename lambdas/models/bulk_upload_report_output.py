from enums.metadata_report import MetadataReport
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from enums.upload_status import UploadStatus
from inflection import underscore
from models.bulk_upload_report import BulkUploadReport
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class ReportBase:
    def __init__(
        self,
        generated_at: str,
    ):
        self.generated_at = generated_at
        self.total_successful = set()
        self.total_registered_elsewhere = set()
        self.total_suspended = set()
        self.total_deceased = set()
        self.total_restricted = set()

    def get_total_successful_nhs_numbers(self) -> list:
        if self.total_successful:
            return [patient[0] for patient in self.total_successful]
        return []

    def get_total_successful_count(self) -> int:
        return len(self.total_successful)

    def get_total_registered_elsewhere_count(self) -> int:
        return len(self.total_registered_elsewhere)

    def get_total_suspended_count(self) -> int:
        return len(self.total_suspended)

    def get_total_deceased_count(self) -> int:
        return len(self.total_deceased)

    def get_total_restricted_count(self) -> int:
        return len(self.total_restricted)

    @staticmethod
    def get_sorted(to_sort: set) -> list:
        return sorted(to_sort, key=lambda x: x[0]) if to_sort else []


class OdsReport(ReportBase):
    def __init__(
        self,
        generated_at: str,
        uploader_ods_code: str = "",
        report_items: list[BulkUploadReport] = [],
    ):
        super().__init__(generated_at)
        self.report_items = report_items
        self.uploader_ods_code = uploader_ods_code
        self.failures_per_patient = {}
        self.unique_failures = {}

        self.populate_report()

    def populate_report(self):
        logger.info(f"Generating ODS report file for {self.uploader_ods_code}")

        for item in self.report_items:
            if item.upload_status == UploadStatus.COMPLETE:
                self.process_successful_report_item(item)
            elif item.upload_status == UploadStatus.FAILED:
                self.process_failed_report_item(item)

        self.set_unique_failures()

    def process_successful_report_item(self, item: BulkUploadReport):
        registered_at_uploader_practice = "True"

        if item.pds_ods_code == PatientOdsInactiveStatus.SUSPENDED:
            self.total_suspended.add((item.nhs_number, item.date))
            registered_at_uploader_practice = "SUSPENDED"
        elif item.pds_ods_code == PatientOdsInactiveStatus.DECEASED:
            registered_at_uploader_practice = "DECEASED"
            self.total_deceased.add((item.nhs_number, item.date, item.reason))
        elif item.pds_ods_code == PatientOdsInactiveStatus.RESTRICTED:
            registered_at_uploader_practice = "RESTRICTED"
            self.total_restricted.add((item.nhs_number, item.date))
        elif (
            item.uploader_ods_code != item.pds_ods_code
            and item.pds_ods_code not in PatientOdsInactiveStatus.list()
        ):
            self.total_registered_elsewhere.add((item.nhs_number, item.date))
            registered_at_uploader_practice = "False"

        self.total_successful.add(
            (item.nhs_number, item.date, registered_at_uploader_practice)
        )

    def process_failed_report_item(self, item: BulkUploadReport):
        is_new_failure = item.nhs_number not in self.failures_per_patient

        is_timestamp_newer = (
            item.nhs_number in self.failures_per_patient
            and self.failures_per_patient[item.nhs_number].get(MetadataReport.Timestamp)
            < item.timestamp
        )

        if (item.reason and is_new_failure) or is_timestamp_newer:
            self.failures_per_patient.update(
                {
                    item.nhs_number: item.model_dump(
                        include={
                            underscore(str(MetadataReport.Date)),
                            underscore(str(MetadataReport.Timestamp)),
                            underscore(str(MetadataReport.UploaderOdsCode)),
                            underscore(str(MetadataReport.Reason)),
                        },
                        by_alias=True,
                    )
                }
            )

    def set_unique_failures(self):
        patients_to_remove = {
            patient
            for patient in self.failures_per_patient
            if patient in self.get_total_successful_nhs_numbers()
        }
        for patient in patients_to_remove:
            self.failures_per_patient.pop(patient)

        for patient_data in self.failures_per_patient.values():
            reason = patient_data.get(MetadataReport.Reason)
            self.unique_failures[reason] = self.unique_failures.get(reason, 0) + 1

    def get_unsuccessful_reasons_data_rows(self):
        return [
            [MetadataReport.Reason, reason, count]
            for reason, count in self.unique_failures.items()
        ]


class SummaryReport(ReportBase):
    def __init__(self, generated_at: str, ods_reports: list[OdsReport] = []):
        super().__init__(generated_at)
        self.ods_reports = ods_reports
        self.success_summary = []
        self.reason_summary = []

        self.populate_report()

    def populate_report(self):
        ods_code_success_total = {}

        for report in self.ods_reports:
            self.total_successful.update(report.total_successful)
            self.total_registered_elsewhere.update(report.total_registered_elsewhere)
            self.total_suspended.update(report.total_suspended)
            self.total_deceased.update(report.total_deceased)
            self.total_restricted.update(report.total_restricted)
            ods_code_success_total[report.uploader_ods_code] = report.total_successful

            for reason, count in report.unique_failures.items():
                self.reason_summary.append(
                    [
                        f"{MetadataReport.Reason} for {report.uploader_ods_code}",
                        reason,
                        count,
                    ]
                )

        if ods_code_success_total:
            for uploader_ods_code, nhs_numbers in ods_code_success_total.items():
                self.success_summary.append(
                    ["Success by ODS", uploader_ods_code, len(nhs_numbers)]
                )
        else:
            self.success_summary.append(["Success by ODS", "No ODS codes found", 0])
