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
        self.reports_bucket = os.getenv("STAGING_STORE_BUCKET_NAME")

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

        summary_data = self.prepare_daily_report_data(report_data)

        self.write_items_to_csv(summary_data, f"/tmp/{file_name}")

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
            file_name = f"daily_statistical_report_bulk_upload_summary_{formatted_date}_{ods_code}.csv"
            file_key = f"daily-reports/{file_name}"

            ods_summary_data = self.prepare_ods_report_data(ods_data)

            self.write_items_to_csv(ods_summary_data, f"/tmp/{file_name}")
            logger.info(f"Uploading ODS report file for {ods_code} to S3")
            self.s3_service.upload_file(
                s3_bucket_name=self.reports_bucket,
                file_key=file_key,
                file_name=f"/tmp/{file_name}",
            )

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
    def write_items_to_csv(items: list, csv_file_path: str):
        logger.info("Writing scan results to csv file")
        with open(csv_file_path, "w") as output_file:
            field_names = items[0].keys()  # Extract field names from the first item
            dict_writer_object = csv.DictWriter(output_file, fieldnames=field_names)
            dict_writer_object.writeheader()
            for item in items:
                dict_writer_object.writerow(item)

    @staticmethod
    def get_times_for_scan() -> tuple[datetime, datetime]:
        current_time = datetime.datetime.now()
        today_date = datetime.datetime.today()
        start_timestamp = today_date - datetime.timedelta(days=30)
        start_timestamp = datetime.datetime.combine(start_timestamp, datetime.time.min)
        end_timestamp = current_time
        return start_timestamp, end_timestamp

        # current_time = datetime.datetime.now()
        # end_report_time = datetime.time(7, 00, 00, 0)
        # today_date = datetime.datetime.today()
        # end_timestamp = datetime.datetime.combine(today_date, end_report_time)
        # if current_time < end_timestamp:
        #     end_timestamp -= datetime.timedelta(days=1)
        # start_timestamp = end_timestamp - datetime.timedelta(days=1)
        # return start_timestamp, end_timestamp

    def group_data_by_ods_code(self, report_data: list):
        ods_reports = {}
        for item in report_data:
            ods_code = item.get("UploaderOdsCode")
            if ods_code not in ods_reports:
                ods_reports[ods_code] = []
            ods_reports[ods_code].append(item)
        return ods_reports

    def prepare_daily_report_data(self, report_data):
        total_successful = sum(
            1 for item in report_data if item["UploadStatus"] == "complete"
        )
        registered_elsewhere = sum(
            1 for item in report_data if item["PdsOdsCode"] != item["UploaderOdsCode"]
        )
        suspended = sum(
            1 for item in report_data if item["UploadStatus"] == "suspended"
        )

        failure_reasons = {}
        for item in report_data:
            if item["UploadStatus"] == "failed":
                reason = item["FailureReason"]
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        return [
            {
                "Type": "Total",
                "Delimiter": "Total Successful",
                "Count": total_successful,
            },
            {
                "Type": "Total",
                "Delimiter": "Successful – Registered Elsewhere",
                "Count": registered_elsewhere,
            },
            {"Type": "Total", "Delimiter": "Suspended", "Count": suspended},
            *[
                {"Type": "FailureReason", "Delimiter": reason, "Count": count}
                for reason, count in failure_reasons.items()
            ],
        ]

    def prepare_ods_report_data(self, report_data):
        total_successful = sum(
            1 for item in report_data if item["UploadStatus"] == "complete"
        )
        registered_elsewhere = sum(
            1 for item in report_data if item["PdsOdsCode"] != item["UploaderOdsCode"]
        )
        suspended = sum(
            1 for item in report_data if item["UploadStatus"] == "suspended"
        )

        failure_reasons = {}
        for item in report_data:
            if item["UploadStatus"] == "failed":
                reason = item["FailureReason"]
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

        return [
            {
                "Type": "Total",
                "Delimiter": "Total Successful",
                "Count": total_successful,
            },
            {
                "Type": "Total",
                "Delimiter": "Successful – Registered Elsewhere",
                "Count": registered_elsewhere,
            },
            {"Type": "Total", "Delimiter": "Suspended", "Count": suspended},
            *[
                {"Type": "FailureReason", "Delimiter": reason, "Count": count}
                for reason, count in failure_reasons.items()
            ],
        ]
