import os
import shutil
import tempfile
from datetime import datetime, timedelta

import polars as pl
import polars.selectors as column_select
from boto3.dynamodb.conditions import Key
from inflection import humanize
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
from utils.polars_utils import CastDecimalToFloat

logger = LoggingService(__name__)


class StatisticalReportService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.statistic_table = os.environ["STATISTICS_TABLE"]

        self.s3_service = S3Service()
        self.reports_bucket = os.environ["STATISTICAL_REPORTS_BUCKET"]

        last_seven_days = [
            datetime.today() - timedelta(days=i) for i in range(7, 0, -1)
        ]
        self.report_period: list[str] = [
            date.strftime("%Y%m%d") for date in last_seven_days
        ]
        self.date_period_in_output_filename = (
            f"{self.report_period[0]}-{self.report_period[-1]}"
        )

    def make_weekly_summary_and_output_to_bucket(self) -> None:
        weekly_summary = self.make_weekly_summary()
        self.store_report_to_s3(weekly_summary)

    def make_weekly_summary(self) -> pl.DataFrame:
        (record_store_data, organisation_data, application_data) = (
            self.get_statistic_data()
        )

        weekly_record_store_data = self.summarise_record_store_data(record_store_data)
        weekly_organisation_data = self.summarise_organisation_data(organisation_data)
        weekly_application_data = self.summarise_application_data(application_data)

        combined_data = self.join_dataframes_by_ods_code(
            [
                weekly_record_store_data,
                weekly_organisation_data,
                weekly_application_data,
            ]
        )
        weekly_summary = self.tidy_up_data(combined_data)

        return weekly_summary

    def get_statistic_data(self) -> LoadedStatisticData:
        logger.info("Loading statistic data of previous week from dynamodb...")
        logger.info(f"The period to report: {self.report_period}")
        dynamodb_items = []
        for date in self.report_period:
            response = self.dynamo_service.query_all_fields(
                table_name=self.statistic_table,
                key_condition_expression=Key("Date").eq(date),
            )
            dynamodb_items.extend(response["Items"])

        return load_from_dynamodb_items(dynamodb_items)

    @staticmethod
    def load_data_to_polars(data: list[StatisticData]) -> pl.DataFrame:
        loaded_data = pl.DataFrame(data).with_columns(CastDecimalToFloat)
        return loaded_data

    def summarise_record_store_data(
        self, record_store_data: list[RecordStoreData]
    ) -> pl.DataFrame:
        logger.info("Summarising RecordStoreData...")
        if not record_store_data:
            logger.info("RecordStoreData for this period was empty.")
            return pl.DataFrame()

        df = self.load_data_to_polars(record_store_data)

        select_most_recent_records = pl.all().sort_by("date").last()
        summarised_data = (
            df.group_by("ods_code")
            .agg(select_most_recent_records)
            .drop("date", "statistic_id")
        )

        return summarised_data

    def summarise_organisation_data(
        self, organisation_data: list[OrganisationData]
    ) -> pl.DataFrame:
        logger.info("Summarising OrganisationData...")
        if not organisation_data:
            logger.info("OrganisationData for this period was empty.")
            return pl.DataFrame()

        df = self.load_data_to_polars(organisation_data)

        sum_daily_count_to_weekly = (
            column_select.matches("daily")
            .sum()
            .name.map(lambda column_name: column_name.replace("daily", "weekly"))
        )
        take_average_for_patient_record = (
            pl.col("average_records_per_patient").mean().round(3)
        )
        select_most_recent_number_of_patients = (
            pl.col("number_of_patients").sort_by("date").last()
        )
        summarised_data = df.group_by("ods_code").agg(
            sum_daily_count_to_weekly,
            take_average_for_patient_record,
            select_most_recent_number_of_patients,
        )
        return summarised_data

    def summarise_application_data(
        self, application_data: list[ApplicationData]
    ) -> pl.DataFrame:
        logger.info("Summarising ApplicationData...")
        if not application_data:
            logger.info("ApplicationData for this period was empty.")
            return pl.DataFrame()

        df = self.load_data_to_polars(application_data)

        count_unique_ids = (
            pl.concat_list("active_user_ids_hashed")
            .flatten()
            .unique()
            .len()
            .alias("active_users_count")
        )
        summarised_data = df.group_by("ods_code").agg(count_unique_ids)
        return summarised_data

    def join_dataframes_by_ods_code(
        self, summarised_data: list[pl.DataFrame]
    ) -> pl.DataFrame:
        non_empty_data = [df for df in summarised_data if not df.is_empty()]
        joined_data = non_empty_data[0]
        for other_df in non_empty_data[1:]:
            joined_data = joined_data.join(
                other_df, on="ods_code", how="outer_coalesce"
            )

        return joined_data

    def tidy_up_data(self, joined_data: pl.DataFrame) -> pl.DataFrame:
        with_date_column_updated = self.update_date_column(joined_data)
        with_columns_reordered = self.reorder_columns(with_date_column_updated)
        with_columns_renamed = with_columns_reordered.rename(
            self.rename_snakecase_columns
        )

        return with_columns_renamed

    def update_date_column(self, joined_data: pl.DataFrame) -> pl.DataFrame:
        date_column_filled_with_report_period = joined_data.with_columns(
            pl.lit(self.date_period_in_output_filename).alias("date")
        )
        return date_column_filled_with_report_period

    def reorder_columns(self, joined_data: pl.DataFrame) -> pl.DataFrame:
        all_columns_names = joined_data.columns
        columns_to_go_first = ["date", "ods_code"]
        other_columns = sorted(set(all_columns_names) - set(columns_to_go_first))
        with_columns_reordered = joined_data.select(
            *columns_to_go_first, *other_columns
        )
        return with_columns_reordered

    @staticmethod
    def rename_snakecase_columns(column_name: str) -> str:
        if column_name == "ods_code":
            return "ODS code"
        else:
            return humanize(column_name)

    def store_report_to_s3(self, weekly_summary: pl.DataFrame) -> None:
        logger.info("Saving the weekly report as .csv")
        file_name = f"statistical_report_{self.date_period_in_output_filename}.csv"
        local_file_path = os.path.join(tempfile.mkdtemp(), file_name)
        try:
            weekly_summary.write_csv(local_file_path)

            logger.info("Uploading the csv report to S3 bucket...")
            self.s3_service.upload_file(local_file_path, self.reports_bucket, file_name)

            logger.info("The weekly report is stored in s3 bucket.")
            logger.info(f"File name: {file_name}")
        finally:
            shutil.rmtree(local_file_path)
