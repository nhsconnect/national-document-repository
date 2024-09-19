import csv
import datetime
import os
from typing import Optional

from boto3.dynamodb.conditions import Attr
from enums.report_types import ReportType
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class BulkUploadReportService:
    def __init__(self):
        self.db_service = DynamoDBService()
        self.s3_service = S3Service()
        self.reports_bucket = os.getenv("STATISTICAL_REPORTS_BUCKET_NAME")

    def report_handler(self, report_type: str):
        start_time, end_time = self.get_times_for_scan()
        report_data = self.get_dynamodb_report_items(
            int(start_time.timestamp()), int(end_time.timestamp())
        )

        if report_data:
            if report_type == ReportType.DAILY.value:
                self.generate_daily_report(report_data, start_time, end_time)
            elif report_type == ReportType.ODS.value:
                self.generate_ods_reports(report_data, start_time, end_time)
        else:
            logger.info("No data found, no new report file to upload")

    def generate_daily_report(self, report_data, start_time, end_time):
        formatted_date = end_time.strftime("%Y%m%d")
        file_name = f"daily_statistical_report_bulk_upload_summary_{formatted_date}.csv"
        file_key = f"daily-reports/{file_name}"

        total_successful = 0
        total_registered_elsewhere = 0
        total_suspended = 0
        ods_code_totals = {}
        failure_reason_counts = {}

        for item in report_data:
            upload_status = item.get("UploadStatus", "")
            pds_ods_code = item.get("PdsOdsCode", "")
            uploader_ods_code = item.get("UploaderOdsCode", "")

            if upload_status == "complete":
                total_successful += 1

                if uploader_ods_code not in ods_code_totals:
                    ods_code_totals[uploader_ods_code] = 0
                ods_code_totals[uploader_ods_code] += 1

                if uploader_ods_code != pds_ods_code:
                    total_registered_elsewhere += 1

            elif upload_status == "suspended":
                total_suspended += 1

            if upload_status == "failed":
                failure_reason = item.get("FailureReason", "Unknown")
                if failure_reason not in failure_reason_counts:
                    failure_reason_counts[failure_reason] = 0
                failure_reason_counts[failure_reason] += 1

        with open(f"/tmp/{file_name}", "w") as output_file:
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
            writer.writerow(["Total", "Suspended", total_suspended])
            if ods_code_totals:
                for ods_code, count in ods_code_totals.items():
                    writer.writerow(["Success by ODS", ods_code, count])
            else:
                writer.writerow(["Success by ODS", "No ODS codes found", 0])

            for failure_reason, count in failure_reason_counts.items():
                writer.writerow(["FailureReason", failure_reason, count])

        logger.info("Uploading daily report file to S3")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=file_key,
            file_name=f"/tmp/{file_name}",
        )

    def generate_ods_reports(self, report_data, start_time, end_time):
        ods_reports = self.group_data_by_ods_code(report_data)
        formatted_date = end_time.strftime("%Y%m%d")

        for ods_code, ods_data in ods_reports.items():
            file_key = f"daily_statistical_report_bulk_upload_summary_{formatted_date}_uploaded_by_{ods_code}.csv"

            total_successful = 0
            total_registered_elsewhere = 0
            total_suspended = 0
            failure_reason_counts = {}

            for item in ods_data:
                upload_status = item.get("UploadStatus", "")
                pds_ods_code = item.get("PdsOdsCode", "")
                uploader_ods_code = item.get("UploaderOdsCode", "")

                if upload_status == "complete":
                    total_successful += 1

                    if uploader_ods_code != pds_ods_code:
                        total_registered_elsewhere += 1

                elif upload_status == "suspended":
                    total_suspended += 1

                if upload_status == "failed":
                    failure_reason = item.get("FailureReason", "Unknown")
                    if failure_reason not in failure_reason_counts:
                        failure_reason_counts[failure_reason] = 0
                    failure_reason_counts[failure_reason] += 1

            with open(f"/tmp/{file_key}", "w") as output_file:
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
                writer.writerow(["Total", "Suspended", total_suspended])
                for failure_reason, count in failure_reason_counts.items():
                    writer.writerow(["FailureReason", failure_reason, count])

            logger.info(f"Uploading ODS report file for {ods_code} to S3")
            self.s3_service.upload_file(
                s3_bucket_name=self.reports_bucket,
                file_key=file_key,
                file_name=f"/tmp/{file_key}",
            )

    def group_data_by_ods_code(self, report_data):
        ods_reports = {}
        for item in report_data:
            ods_code = item.get("UploaderOdsCode", "Unknown")
            if ods_code not in ods_reports:
                ods_reports[ods_code] = []
            ods_reports[ods_code].append(item)
        return ods_reports

    def get_dynamodb_report_items(
        self, start_timestamp: int, end_timestamp: int
    ) -> Optional[list]:
        logger.info("Starting Scan on DynamoDB table")
        bulk_upload_table_name = os.getenv("BULK_UPLOAD_DYNAMODB_NAME")
        filter_time = Attr("Timestamp").gt(start_timestamp) & Attr("Timestamp").lt(
            end_timestamp
        )
        db_response = self.db_service.scan_table(
            bulk_upload_table_name, filter_expression=filter_time
        )

        if "Items" not in db_response:
            return None
        items = db_response["Items"]
        while "LastEvaluatedKey" in db_response:
            db_response = self.db_service.scan_table(
                bulk_upload_table_name,
                exclusive_start_key=db_response["LastEvaluatedKey"],
                filter_expression=filter_time,
            )
            if db_response["Items"]:
                items.extend(db_response["Items"])
        return items

    @staticmethod
    def get_times_for_scan() -> tuple[datetime, datetime]:
        # current_time = datetime.datetime.now()
        # today_date = datetime.datetime.today()
        # start_timestamp = today_date - datetime.timedelta(days=30)
        # start_timestamp = datetime.datetime.combine(start_timestamp, datetime.time.min)
        # end_timestamp = current_time
        # return start_timestamp, end_timestamp

        current_time = datetime.datetime.now()
        end_report_time = datetime.time(7, 00, 00, 0)
        today_date = datetime.datetime.today()
        end_timestamp = datetime.datetime.combine(today_date, end_report_time)
        if current_time < end_timestamp:
            end_timestamp -= datetime.timedelta(days=1)
        start_timestamp = end_timestamp - datetime.timedelta(days=1)
        return start_timestamp, end_timestamp
