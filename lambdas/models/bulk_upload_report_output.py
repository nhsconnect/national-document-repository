from enums.metadata_report import MetadataReport
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from enums.upload_status import UploadStatus
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

    def get_total_successful_nhs_numbers(self):
        if self.total_successful:
            return [s[0] for s in self.total_successful]
        return []

    def get_total_successful(self) -> list:
        if self.total_successful:
            return sorted(self.total_successful, key=lambda x: x[0])
        return []

    def get_total_successful_count(self):
        return len(self.get_total_successful_nhs_numbers())

    def get_total_registered_elsewhere_nhs_numbers(self):
        if self.total_successful:
            return [s[0] for s in self.total_registered_elsewhere]
        return []

    def get_total_registered_elsewhere(self):
        return len(self.get_total_registered_elsewhere_nhs_numbers())

    def get_total_suspended(self):
        unique_nhs_nums = [ts[0] for ts in self.total_suspended]
        return len(unique_nhs_nums)

    def get_total_deceased(self):
        unique_nhs_nums = [td[0] for td in self.total_deceased]
        return len(unique_nhs_nums)

    def get_total_restricted(self):
        unique_nhs_nums = [tr[0] for tr in self.total_restricted]
        return len(unique_nhs_nums)


class OdsReport(ReportBase):
    def __init__(
        self,
        generated_at: str,
        uploader_ods_code: str = "",
        report_items: list[BulkUploadReport] = None,
    ):
        super().__init__(generated_at)
        if report_items is None:
            report_items = []

        self.report_items = report_items
        self.uploader_ods_code = uploader_ods_code
        self.failures_per_patient = {}
        self.unique_failures = {}
        self.unsuccessful_reasons = []

        self.populate_report()

    def populate_report(self):
        logger.info(f"Generating ODS report file for {self.uploader_ods_code}")

        for item in self.report_items:
            if item.upload_status == UploadStatus.COMPLETE:
                self.process_successful_report_item(item)
            elif item.upload_status == UploadStatus.FAILED:
                self.process_failed_report_item(item)

        self.set_unique_failures()
        self.set_unsuccessful_reasons()

    def process_successful_report_item(self, item: BulkUploadReport):
        self.total_successful.add((item.nhs_number, item.date))

        if item.pds_ods_code == PatientOdsInactiveStatus.SUSPENDED:
            self.total_suspended.add((item.nhs_number, item.date))

        if item.pds_ods_code == PatientOdsInactiveStatus.DECEASED:
            self.total_deceased.add((item.nhs_number, item.date, item.failure_reason))

        if item.pds_ods_code == PatientOdsInactiveStatus.RESTRICTED:
            self.total_restricted.add((item.nhs_number, item.date))

        elif (
            item.uploader_ods_code != item.pds_ods_code
            and item.pds_ods_code not in PatientOdsInactiveStatus.str_list()
        ):
            self.total_registered_elsewhere.add((item.nhs_number, item.date))

    def process_failed_report_item(self, item: BulkUploadReport):
        failure_reason = item.failure_reason
        if (
            failure_reason and item.nhs_number not in self.failures_per_patient
        ) or self.failures_per_patient[item.nhs_number].get(
            MetadataReport.Timestamp
        ) < item.timestamp:
            self.failures_per_patient.update(
                {
                    item.nhs_number: {
                        MetadataReport.FailureReason: failure_reason,
                        MetadataReport.Timestamp: item.timestamp,
                    }
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
            reason = patient_data.get(MetadataReport.FailureReason)
            self.unique_failures[reason] = self.unique_failures.get(reason, 0) + 1

    def set_unsuccessful_reasons(self):
        self.unsuccessful_reasons = [
            [str(MetadataReport.FailureReason), failure_reason, count]
            for failure_reason, count in self.unique_failures.items()
        ]


class SummaryReport(ReportBase):
    def __init__(self, generated_at: str, ods_reports: list[OdsReport] = None):
        super().__init__(generated_at)

        if ods_reports is None:
            ods_reports = []

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
                        f"{MetadataReport.FailureReason} for {report.uploader_ods_code}",
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
