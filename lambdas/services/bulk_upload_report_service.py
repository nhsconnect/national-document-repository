import csv
import datetime
import os

from boto3.dynamodb.conditions import Attr
from enums.metadata_report import MetadataReport
from models.bulk_upload_report import BulkUploadReport
from models.bulk_upload_report_output import OdsReport, SummaryReport
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class BulkUploadReportService:
    def __init__(self):
        self.db_service = DynamoDBService()
        self.s3_service = S3Service()
        self.reports_bucket = os.getenv("STATISTICAL_REPORTS_BUCKET")

    def report_handler(self):
        start_time, end_time = self.get_times_for_scan()
        report_data = self.get_dynamodb_report_items(
            int(start_time.timestamp()), int(end_time.timestamp())
        )

        if report_data:
            logger.info(
                f"Bulk upload reports for {str(start_time)} to {str(end_time)}.csv"
            )

            generated_at = start_time.strftime("%Y%m%d")

            ods_reports: list[OdsReport] = self.generate_ods_reports(
                report_data, generated_at
            )
            logger.info("Successfully processed daily ODS reports")
            self.generate_summary_report(ods_reports, generated_at)
            logger.info("Successfully processed daily summary report")
            self.generate_daily_report(report_data, start_time, end_time)
            logger.info("Successfully processed daily report")
            self.generate_success_report(ods_reports, generated_at)
            logger.info("Successfully processed success report")
            self.generate_suspended_report(ods_reports, generated_at)
            logger.info("Successfully processed suspended report")
            self.generate_deceased_report(ods_reports, generated_at)
            logger.info("Successfully processed deceased report")
            self.generate_restricted_report(ods_reports, generated_at)
            logger.info("Successfully processed restricted report")
            self.generate_rejected_report(ods_reports, generated_at)
            logger.info("Successfully processed rejected report")
        else:
            logger.info("No data found, no new report file to upload")

    def generate_ods_reports(
        self, report_data: list[BulkUploadReport], generated_at: str
    ) -> list[OdsReport]:
        ods_reports: list[OdsReport] = []

        grouped_ods_data = {}
        for item in report_data:
            uploader_ods_code = item.uploader_ods_code

            if uploader_ods_code is not None and item is not None:
                grouped_ods_data.setdefault(uploader_ods_code, []).append(item)

        for uploader_ods_code, ods_report_items in grouped_ods_data.items():
            ods_report = self.generate_individual_ods_report(
                uploader_ods_code, ods_report_items, generated_at
            )
            ods_reports.append(ods_report)

        return ods_reports

    def generate_individual_ods_report(
        self,
        uploader_ods_code: str,
        ods_report_items: list[BulkUploadReport],
        generated_at: str,
    ) -> OdsReport:
        ods_report = OdsReport(
            generated_at=generated_at,
            report_items=ods_report_items,
            uploader_ods_code=uploader_ods_code,
        )

        file_key = f"daily_statistical_report_bulk_upload_summary_{generated_at}_uploaded_by_{uploader_ods_code}.csv"

        self.write_summary_data_to_csv(
            file_name=file_key,
            total_successful=ods_report.get_total_successful_count(),
            total_registered_elsewhere=ods_report.get_total_registered_elsewhere(),
            total_suspended=ods_report.get_total_suspended(),
            extra_rows=ods_report.unsuccessful_reasons,
        )

        logger.info(f"Uploading ODS report file for {uploader_ods_code} to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_key}",
        )

        return ods_report

    def generate_summary_report(self, ods_reports: list[OdsReport], generated_at: str):
        summary_report = SummaryReport(
            generated_at=generated_at, ods_reports=ods_reports
        )

        file_name = f"daily_statistical_report_bulk_upload_summary_{generated_at}.csv"
        file_key = f"daily-reports/{file_name}"

        self.write_summary_data_to_csv(
            file_name=file_name,
            total_successful=summary_report.get_total_successful_count(),
            total_registered_elsewhere=summary_report.get_total_registered_elsewhere(),
            total_suspended=summary_report.get_total_suspended(),
            total_deceased=summary_report.get_total_deceased(),
            total_restricted=summary_report.get_total_restricted(),
            extra_rows=summary_report.success_summary + summary_report.reason_summary,
        )

        logger.info("Uploading daily summary report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_name}",
        )

    def generate_daily_report(
        self, report_data: list[BulkUploadReport], start_time: str, end_time: str
    ):
        file_name = f"Bulk upload report for {str(start_time)} to {str(end_time)}.csv"

        self.write_items_to_csv(report_data, f"/tmp/{file_name}")

        logger.info("Uploading daily report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=f"daily-reports/{file_name}",
            file_name=f"/tmp/{file_name}",
        )

    def generate_success_report(self, ods_reports: list[OdsReport], generated_at: str):
        file_name = f"daily_statistical_report_bulk_upload_success_{generated_at}.csv"
        file_key = f"daily-reports/{file_name}"

        headers = [
            MetadataReport.NhsNumber,
            MetadataReport.UploaderOdsCode,
            MetadataReport.Date,
        ]
        data_rows = []
        for report in ods_reports:
            successful_patients = sorted(report.total_successful, key=lambda x: x[0])
            for patient in successful_patients:
                data_rows.append(
                    [str(patient[0]), str(report.uploader_ods_code), str(patient[1])]
                )

        self.write_additional_report_items_to_csv(
            file_name=file_name, headers=headers, rows_to_write=data_rows
        )

        logger.info("Uploading daily success report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_name}",
        )

    def generate_suspended_report(
        self, ods_reports: list[OdsReport], generated_at: str
    ):
        file_name = f"daily_statistical_report_bulk_upload_suspended_{generated_at}.csv"
        file_key = f"daily-reports/{file_name}"

        headers = [
            MetadataReport.NhsNumber,
            MetadataReport.UploaderOdsCode,
            MetadataReport.Date,
        ]
        data_rows = []
        for report in ods_reports:
            suspended_patients = sorted(report.total_suspended, key=lambda x: x[0])
            for patient in suspended_patients:
                data_rows.append(
                    [str(patient[0]), str(report.uploader_ods_code), str(patient[1])]
                )

        self.write_additional_report_items_to_csv(
            file_name=file_name, headers=headers, rows_to_write=data_rows
        )

        logger.info("Uploading daily success report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_name}",
        )

    def generate_deceased_report(self, ods_reports: list[OdsReport], generated_at: str):
        file_name = f"daily_statistical_report_bulk_upload_deceased_{generated_at}.csv"
        file_key = f"daily-reports/{file_name}"

        headers = [
            MetadataReport.NhsNumber,
            MetadataReport.UploaderOdsCode,
            MetadataReport.Date,
            MetadataReport.FailureReason,
        ]
        data_rows = []
        for report in ods_reports:
            deceased_patients = sorted(report.total_deceased, key=lambda x: x[0])
            for patient in deceased_patients:
                data_rows.append(
                    [
                        str(patient[0]),
                        str(report.uploader_ods_code),
                        str(patient[1]),
                        str(patient[2]),
                    ]
                )

        self.write_additional_report_items_to_csv(
            file_name=file_name, headers=headers, rows_to_write=data_rows
        )

        logger.info("Uploading daily success report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_name}",
        )

    def generate_restricted_report(
        self, ods_reports: list[OdsReport], generated_at: str
    ):
        file_name = (
            f"daily_statistical_report_bulk_upload_restricted_{generated_at}.csv"
        )
        file_key = f"daily-reports/{file_name}"

        headers = [
            MetadataReport.NhsNumber,
            MetadataReport.UploaderOdsCode,
            MetadataReport.Date,
        ]
        data_rows = []
        for report in ods_reports:
            restricted_patients = sorted(report.total_restricted, key=lambda x: x[0])
            for patient in restricted_patients:
                data_rows.append(
                    [str(patient[0]), str(report.uploader_ods_code), str(patient[1])]
                )

        self.write_additional_report_items_to_csv(
            file_name=file_name, headers=headers, rows_to_write=data_rows
        )

        logger.info("Uploading daily success report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_name}",
        )

    def generate_rejected_report(self, ods_reports: list[OdsReport], generated_at: str):
        file_name = f"daily_statistical_report_bulk_upload_rejected_{generated_at}.csv"
        file_key = f"daily-reports/{file_name}"

        headers = [
            MetadataReport.NhsNumber,
            MetadataReport.UploaderOdsCode,
            MetadataReport.Date,
            MetadataReport.FailureReason,
        ]

        data_rows = []
        for report in ods_reports:
            for nhs_number, report_item in report.failures_per_patient.items():
                data_rows.append(
                    [
                        nhs_number,
                        report_item[MetadataReport.UploaderOdsCode],
                        report_item[MetadataReport.Date],
                        report_item[MetadataReport.FailureReason],
                    ]
                )

        self.write_additional_report_items_to_csv(
            file_name=file_name, headers=headers, rows_to_write=data_rows
        )

        logger.info("Uploading daily success report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_name}",
        )

    @staticmethod
    def write_items_to_csv(items: list[BulkUploadReport], csv_file_path: str):
        logger.info("Writing scan results to csv file")
        with open(csv_file_path, "w") as output_file:
            field_names = MetadataReport.list()
            dict_writer_object = csv.DictWriter(output_file, fieldnames=field_names)
            dict_writer_object.writeheader()
            for item in items:
                dict_writer_object.writerow(
                    item.dict(exclude={str(MetadataReport.ID).lower()}, by_alias=True)
                )

    @staticmethod
    def write_summary_data_to_csv(
        file_name: str,
        total_successful: int,
        total_registered_elsewhere: int,
        total_suspended: int,
        total_deceased: int = None,
        total_restricted: int = None,
        extra_rows: list = [],
    ):
        with open(f"/tmp/{file_name}", "w", newline="") as output_file:
            writer = csv.writer(output_file)

            writer.writerow(["Type", "Description", "Count"])
            writer.writerow(["Total", "Total Successful", total_successful])
            writer.writerow(
                [
                    "Total",
                    "Successful - Registered Elsewhere",
                    total_registered_elsewhere,
                ]
            )
            writer.writerow(["Total", "Successful - Suspended", total_suspended])

            if total_deceased:
                writer.writerow(["Total", "Successful - Deceased", total_deceased])

            if total_restricted:
                writer.writerow(["Total", "Successful - Restricted", total_restricted])

            for row in extra_rows:
                writer.writerow(row)

    @staticmethod
    def write_additional_report_items_to_csv(
        file_name: str,
        headers: list[str] = [],
        rows_to_write: list[list[str]] = [],
    ):
        with open(f"/tmp/{file_name}", "w", newline="") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(headers)
            for row in rows_to_write:
                writer.writerow(row)

    def get_dynamodb_report_items(
        self, start_timestamp: int, end_timestamp: int
    ) -> list[BulkUploadReport]:
        logger.info("Starting Scan on DynamoDB table")
        bulk_upload_table_name = os.getenv("BULK_UPLOAD_DYNAMODB_NAME")
        filter_time = Attr("Timestamp").gt(start_timestamp) & Attr("Timestamp").lt(
            end_timestamp
        )
        db_response = self.db_service.scan_table(
            bulk_upload_table_name, filter_expression=filter_time
        )

        if "Items" not in db_response:
            return []
        items = db_response["Items"]
        while "LastEvaluatedKey" in db_response:
            db_response = self.db_service.scan_table(
                bulk_upload_table_name,
                exclusive_start_key=db_response["LastEvaluatedKey"],
                filter_expression=filter_time,
            )
            if db_response["Items"]:
                items.extend(db_response["Items"])

        validated_items = []
        for item in items:
            try:
                validated_items.append(BulkUploadReport.model_validate(item))
            except ValidationError as e:
                logger.error(f"Failed to parse bulk update report dynamo item: {e}")

        return validated_items

    @staticmethod
    def get_times_for_scan() -> tuple[datetime, datetime]:
        current_time = datetime.datetime.now()
        end_report_time = datetime.time(7, 00, 00, 0)
        today_date = datetime.datetime.today()
        end_timestamp = datetime.datetime.combine(today_date, end_report_time)
        if current_time < end_timestamp:
            end_timestamp -= datetime.timedelta(days=1)
        start_timestamp = end_timestamp - datetime.timedelta(days=1)
        return start_timestamp, end_timestamp
