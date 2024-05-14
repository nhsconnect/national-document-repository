import csv
import itertools
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

import polars as pl
import polars.selectors as column_select
from boto3.dynamodb.conditions import Key
from models.statistics import (
    ApplicationData,
    LoadedStatisticData,
    OrganisationData,
    RecordStoreData,
    StatisticData,
    load_from_dynamodb_items,
)
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class StatisticalReportService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.statistic_table = os.environ["STATISTICS_TABLE"]

        self.s3_service = S3Service()
        self.reports_bucket = os.environ["STATISTICAL_REPORTS_BUCKET"]

        last_seven_days = [
            datetime.today() - timedelta(days=i) for i in range(1, 7 + 1)
        ]
        self.report_period: list[str] = [
            date.strftime("%Y%m%d") for date in last_seven_days
        ]
        self.most_recent_date = self.report_period[0]

    def make_weekly_summary_and_output_to_bucket(self):
        weekly_summary = self.make_weekly_summary()
        self.store_report_to_s3(weekly_summary)

    def make_weekly_summary(self) -> list[dict]:
        (record_store_data, organisation_data, application_data) = (
            self.get_statistic_data()
        )

        logger.info("Aggregating the data...")
        weekly_record_store_data = self.process_data_by_ods_code(
            record_store_data, self.summarise_record_store_data
        )
        weekly_organisation_data = self.process_data_by_ods_code(
            organisation_data, self.summarise_organisation_data
        )
        weekly_application_data = self.process_data_by_ods_code(
            application_data, self.summarise_application_data
        )

        logger.info("Data summarised by week:")
        logger.info(f"Record store data: {weekly_record_store_data}")
        logger.info(f"Organisation data: {weekly_organisation_data}")
        logger.info(f"Application data: {weekly_application_data}")

        weekly_summary_combined = self.join_data_by_ods_code_and_add_date(
            [
                weekly_record_store_data,
                weekly_organisation_data,
                weekly_application_data,
            ]
        )
        logger.info(f"Weekly summary by ODS code: {weekly_summary_combined}")
        return weekly_summary_combined

    def get_statistic_data(self) -> LoadedStatisticData:
        logger.info("Loading statistic data of previous week from dynamodb...")
        dynamodb_items = []
        for date in self.report_period:
            response = self.dynamo_service.simple_query(
                table_name=self.statistic_table,
                key_condition_expression=Key("Date").eq(date),
            )
            dynamodb_items.extend(response["Items"])

        return load_from_dynamodb_items(dynamodb_items)

    def process_data_by_ods_code(
        self, loaded_data: list[StatisticData], summarising_function
    ) -> list[dict]:
        grouped_by_ods_code = self.group_data_by_ods_code(loaded_data)

        all_results = []
        for ods_code, data in grouped_by_ods_code.items():
            summarised_result = summarising_function(data)
            summarised_result["Ods Code"] = ods_code
            all_results.append(summarised_result)

        return all_results

    @staticmethod
    def load_data_to_polars(data: list[StatisticData]) -> pl.DataFrame:
        return pl.DataFrame(data).with_columns(
            column_select.by_dtype(pl.datatypes.Decimal).cast(pl.Float64)
        )

    def summarise_record_store_data_polars(
        self, record_store_data: list[RecordStoreData]
    ) -> pl.DataFrame:
        df = self.load_data_to_polars(record_store_data)

        get_most_recent_records = pl.all().sort_by("date").last()
        summarised_data = df.group_by("ods_code").agg(get_most_recent_records)

        return summarised_data

    @staticmethod
    def summarise_record_store_data(record_store_data: list[RecordStoreData]) -> dict:
        latest_record = max(record_store_data, key=lambda record: record.date)
        return {
            "Total number of records": latest_record.total_number_of_records,
            "Number of document types": latest_record.total_number_of_records,
            "Total size of records (in MB)": latest_record.total_size_of_records_in_megabytes,
        }

    def summarise_organisation_data_polars(
        self, organisation_data: list[RecordStoreData]
    ) -> pl.DataFrame:
        df = self.load_data_to_polars(organisation_data)

        sum_daily_count_to_weekly = (
            column_select.matches("daily")
            .sum()
            .name.map(lambda column_name: column_name.replace("daily", "weekly"))
        )
        take_average_for_patient_record = pl.col("average_records_per_patient").mean()
        get_most_recent_number_of_patients = (
            pl.col("number_of_patients").sort_by("date").last()
        )
        summarised_data = df.group_by("ods_code").agg(
            sum_daily_count_to_weekly,
            take_average_for_patient_record,
            get_most_recent_number_of_patients,
        )
        return summarised_data

    @staticmethod
    def summarise_organisation_data(organisation_data: list[OrganisationData]) -> dict:
        aggregated_data = {
            "Weekly documents stored": sum(
                data.daily_count_stored for data in organisation_data
            ),
            "Weekly documents viewed": sum(
                data.daily_count_viewed for data in organisation_data
            ),
            "Weekly documents downloaded": sum(
                data.daily_count_downloaded for data in organisation_data
            ),
            "Weekly documents deleted": sum(
                data.daily_count_deleted for data in organisation_data
            ),
            "Average record per patient": take_average(
                [data.average_records_per_patient for data in organisation_data]
            ),
            # TODO: replace this with a unique count when we change this data to a list of hashed id
            "Number of patients": next(
                data.number_of_patients for data in organisation_data
            ),
        }

        return aggregated_data

    def summarise_application_data_polars(
        self, application_data: list[ApplicationData]
    ) -> pl.DataFrame:
        df = self.load_data_to_polars(application_data)
        count_unique_ids = (
            pl.concat_list("active_user_ids_hashed")
            .flatten()
            .unique()
            .len()
            .alias("Active users count")
        )
        summarised_data = df.group_by("ods_code").agg(count_unique_ids)
        return summarised_data

    @staticmethod
    def summarise_application_data(application_data: list[ApplicationData]) -> dict:
        all_hashed_ids_in_week = itertools.chain(
            *(data.active_user_ids_hashed for data in application_data)
        )
        all_unique_ids = set(all_hashed_ids_in_week)

        return {"Active users count": len(all_unique_ids)}

    @staticmethod
    def group_data_by_ods_code(
        data: list[StatisticData],
    ) -> dict[str, list[StatisticData]]:
        result = defaultdict(list)
        for item in data:
            ods_code = item.ods_code
            result[ods_code].append(item)

        return result

    def join_data_by_ods_code_and_add_date(
        self, results: list[list[dict]]
    ) -> list[dict]:
        joined_data = self.join_data_by_ods_code(results)
        with_date_column_added = self.add_date_column_to_results(joined_data)

        return with_date_column_added

    @staticmethod
    def join_data_by_ods_code(results: list[list[dict]]) -> list[dict]:
        all_data_flatten = itertools.chain(*results)

        joined_by_ods_code = defaultdict(dict)
        for entry in all_data_flatten:
            ods_code = entry["Ods Code"]
            joined_by_ods_code[ods_code].update(entry)

        return list(joined_by_ods_code.values())

    def add_date_column_to_results(self, joined_data: list[dict]) -> list[dict]:
        for data in joined_data:
            data["Date"] = self.most_recent_date
        return joined_data

    def store_report_to_s3(self, weekly_summary: list[dict]):
        logger.info("Saving the report in S3 bucket...")

        file_name = f"statistical_report_{self.most_recent_date}.csv"
        local_file_path = f"{tempfile.mkdtemp()}/{file_name}"
        all_field_names = {field for row in weekly_summary for field in row.keys()}
        field_names_in_order = [
            "Date",
            "Ods Code",
            *sorted(all_field_names - {"Date", "Ods Code"}),
        ]

        with open(local_file_path, "w") as output_file:
            dict_writer_object = csv.DictWriter(
                output_file, fieldnames=field_names_in_order
            )
            dict_writer_object.writeheader()
            for item in weekly_summary:
                dict_writer_object.writerow(item)

        self.s3_service.upload_file(local_file_path, self.reports_bucket, file_name)

        logger.info("The weekly report is stored in s3 bucket")


def take_average(list_of_number: list[Decimal]) -> float:
    if list_of_number:
        return sum(list_of_number) / (len(list_of_number))
    return 0
