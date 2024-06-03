import hashlib
import itertools
import os
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from typing import TypedDict
from urllib.parse import urlparse

import boto3
import polars as pl
from boto3.dynamodb.conditions import Attr
from enums.supported_document_types import SupportedDocumentTypes
from models.cloudwatch_logs_query import (
    CloudwatchLogsQueryParams,
    LloydGeorgeRecordsDeleted,
    LloydGeorgeRecordsDownloaded,
    LloydGeorgeRecordsStored,
    LloydGeorgeRecordsViewed,
    UniqueActiveUserIds,
)
from models.statistics import (
    ApplicationData,
    OrganisationData,
    RecordStoreData,
    StatisticData,
)
from services.logs_query_service import CloudwatchLogsQueryService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class S3ListObjectsResult(TypedDict):
    Key: str
    Size: int


class DataCollectionService:
    def __init__(self):
        self.workspace = os.environ["WORKSPACE"]

        self.logs_query_service = CloudwatchLogsQueryService()

        # TODO: integrate with existing services
        self.dynamodb = boto3.resource("dynamodb")
        self.s3_client = boto3.client("s3")

        statistic_table_name = os.environ["STATISTICS_TABLE"]
        self.output_table = self.dynamodb.Table(statistic_table_name)

        self.lloyd_george_dynamodb_name = (
            SupportedDocumentTypes.LG.get_dynamodb_table_name()
        )
        self.lloyd_george_bucket_name = SupportedDocumentTypes.LG.get_s3_bucket_name()
        self.arf_dynamodb_name = SupportedDocumentTypes.ARF.get_dynamodb_table_name()
        self.arf_bucket_name = SupportedDocumentTypes.ARF.get_s3_bucket_name()

        one_day = 60 * 60 * 24
        time_now = int(datetime.now().timestamp())

        self.collection_start_time = time_now - one_day
        self.collection_end_time = time_now
        self.date = datetime.today().strftime("%Y%m%d")

    def collect_all_data_and_write_to_dynamodb(self):
        all_statistic_data = self.collect_all_data()
        logger.info("Statistic data collected:")
        logger.info(all_statistic_data)

        self.write_to_local_dynamodb_table(all_statistic_data)

    def collect_all_data(self) -> list[StatisticData]:
        dynamodb_scan_result = self.scan_dynamodb_tables()
        s3_list_objects_result = self.get_all_s3_files_info()

        record_store_data = self.get_record_store_data(
            dynamodb_scan_result, s3_list_objects_result
        )
        organisation_data = self.get_organisation_data(dynamodb_scan_result)
        application_data = self.get_application_data()

        return record_store_data + organisation_data + application_data

    def write_to_local_dynamodb_table(self, all_statistic_data: list[StatisticData]):
        logger.info("Writing statistic data to dynamodb table")

        for entry in all_statistic_data:
            dynamodb_item = entry.model_dump(by_alias=True)
            logger.info(f"writing item: {dynamodb_item}")
            self.output_table.put_item(Item=dynamodb_item)

        logger.info("Finish writing all data to dynamodb table")

    def scan_dynamodb_tables(self) -> list[dict]:
        all_results = []
        for doc_type in SupportedDocumentTypes.list():
            table_name = doc_type.get_dynamodb_table_name()
            result = self.scan_dynamodb_table(table_name)
            all_results += result

        return all_results

    def get_all_s3_files_info(self) -> list[dict]:
        all_results = []
        for doc_type in SupportedDocumentTypes.list():
            bucket_name = doc_type.get_s3_bucket_name()
            result = self.get_s3_files_info(bucket_name)
            all_results += result

        return all_results

    def scan_dynamodb_table(self, table_name: str) -> list[dict]:
        table = self.dynamodb.Table(table_name)
        project_expression = "CurrentGpOds,NhsNumber,FileLocation,ContentType"
        filter_expression = Attr("Uploaded").eq(True) & Attr("Deleted").eq("")

        paginated_result = table.scan(
            ProjectionExpression=project_expression,
            FilterExpression=filter_expression,
        )
        dynamodb_scan_result = paginated_result["Items"]
        while "LastEvaluatedKey" in paginated_result:
            start_key_for_next_page = paginated_result["LastEvaluatedKey"]
            paginated_result = table.scan(
                ProjectionExpression=project_expression,
                FilterExpression=filter_expression,
                ExclusiveStartKey=start_key_for_next_page,
            )
            dynamodb_scan_result += paginated_result["Items"]
        return dynamodb_scan_result

    def get_record_store_data(
        self,
        dynamodb_scan_result: list[dict],
        s3_list_objects_result: list[S3ListObjectsResult],
    ) -> list[RecordStoreData]:
        total_number_of_records_by_ods_code = (
            self.get_total_number_of_records_by_ods_code(dynamodb_scan_result)
        )

        total_and_average_file_sizes = (
            self.get_metrics_for_total_and_average_file_sizes(
                dynamodb_scan_result, s3_list_objects_result
            )
        )

        number_of_document_types = self.get_number_of_document_types(
            dynamodb_scan_result
        )

        joined_query_result = self.join_results_by_ods_code(
            [
                total_number_of_records_by_ods_code,
                total_and_average_file_sizes,
                number_of_document_types,
            ]
        )

        record_store_data_for_all_ods_code = [
            RecordStoreData(
                date=self.date,
                **record_store_data_properties,
            )
            for record_store_data_properties in joined_query_result
        ]

        return record_store_data_for_all_ods_code

    def get_organisation_data(self, dynamodb_scan_result) -> list[OrganisationData]:
        number_of_patients = self.get_number_of_patients(dynamodb_scan_result)
        average_records_per_patient = self.get_average_number_of_file_per_patient(
            dynamodb_scan_result
        )
        daily_count_viewed = self.get_cloud_watch_query_result(LloydGeorgeRecordsViewed)
        daily_count_downloaded = self.get_cloud_watch_query_result(
            LloydGeorgeRecordsDownloaded
        )
        daily_count_deleted = self.get_cloud_watch_query_result(
            LloydGeorgeRecordsDeleted
        )
        daily_count_stored = self.get_cloud_watch_query_result(LloydGeorgeRecordsStored)

        joined_query_result = self.join_results_by_ods_code(
            [
                number_of_patients,
                average_records_per_patient,
                daily_count_viewed,
                daily_count_downloaded,
                daily_count_deleted,
                daily_count_stored,
            ]
        )

        organisation_data_for_all_ods_code = [
            OrganisationData(date=self.date, **organisation_data_properties)
            for organisation_data_properties in joined_query_result
        ]

        return organisation_data_for_all_ods_code

    def get_application_data(self) -> list[ApplicationData]:
        user_id_per_ods_code = self.get_active_user_list()
        application_data_for_all_ods_code = [
            ApplicationData(
                date=self.date,
                active_user_ids_hashed=active_user_ids_hashed,
                ods_code=ods_code,
            )
            for ods_code, active_user_ids_hashed in user_id_per_ods_code.items()
        ]
        return application_data_for_all_ods_code

    def get_active_user_list(self) -> dict[str, list]:
        query_result = self.get_cloud_watch_query_result(
            query_params=UniqueActiveUserIds
        )
        user_ids_per_ods_code = defaultdict(list)
        for entry in query_result:
            ods_code = entry.get("ods_code")
            user_id = entry.get("user_id")
            hashed_user_id = hashlib.md5(bytes(user_id, "utf8")).hexdigest()
            user_ids_per_ods_code[ods_code].append(hashed_user_id)

        return user_ids_per_ods_code

    def get_cloud_watch_query_result(
        self, query_params: CloudwatchLogsQueryParams
    ) -> list[dict]:
        return self.logs_query_service.query_logs(
            query_params=query_params,
            start_time=self.collection_start_time,
            end_time=self.collection_end_time,
        )

    def get_s3_files_info(self, bucket_name: str) -> list[S3ListObjectsResult]:
        # TODO: move this to s3 service
        s3_paginator = self.s3_client.get_paginator("list_objects_v2")
        s3_list_objects_result = []
        for paginated_result in s3_paginator.paginate(Bucket=bucket_name):
            s3_list_objects_result += paginated_result["Contents"]
        return s3_list_objects_result

    def get_total_number_of_records_by_ods_code(
        self, dynamodb_scan_result: list[dict]
    ) -> list[dict]:
        ods_code_for_every_document = [
            item["CurrentGpOds"] for item in dynamodb_scan_result
        ]
        counted_by_ods_code = Counter(ods_code_for_every_document)
        count_result_in_list_of_dict = [
            {"ods_code": key, "total_number_of_records": value}
            for key, value in counted_by_ods_code.items()
        ]
        return count_result_in_list_of_dict

    def get_number_of_patients(self, dynamodb_scan_result: list[dict]) -> list[dict]:
        patients_grouped_by_ods_code = defaultdict(set)
        for item in dynamodb_scan_result:
            ods_code = item["CurrentGpOds"]
            patients_grouped_by_ods_code[ods_code].add(item["NhsNumber"])

        return [
            {"ods_code": ods_code, "number_of_patients": len(patients)}
            for ods_code, patients in patients_grouped_by_ods_code.items()
        ]

    @staticmethod
    def get_file_key(file_location: str) -> str:
        return str(urlparse(file_location).path.lstrip("/"))

    def get_metrics_for_total_and_average_file_sizes(
        self,
        dynamodb_scan_result: list[dict],
        s3_list_objects_result: list[S3ListObjectsResult],
    ) -> list[dict]:
        dynamodb_df = pl.DataFrame(dynamodb_scan_result)
        s3_df = pl.DataFrame(s3_list_objects_result)

        dynamodb_df_with_file_key = dynamodb_df.with_columns(
            pl.col("FileLocation")
            .map_elements(self.get_file_key, return_dtype=pl.String)
            .alias("FileKey")
        )

        joined_df = dynamodb_df_with_file_key.join(
            s3_df, how="left", left_on="FileKey", right_on="Key"
        )
        get_total_size = (pl.col("Size").sum() / 1024 / 1024).alias(
            "TotalFileSizeForPatientInMegabytes"
        )
        df_with_total_file_size_per_patient = joined_df.group_by(
            "CurrentGpOds", "NhsNumber"
        ).agg(get_total_size)

        get_average_file_size_per_patient = (
            pl.col("TotalFileSizeForPatientInMegabytes")
            .mean()
            .alias("average_size_of_documents_per_patient_in_megabytes")
        )

        get_total_file_size_for_ods_code = (
            pl.col("TotalFileSizeForPatientInMegabytes")
            .sum()
            .alias("total_size_of_records_in_megabytes")
        )

        result = (
            df_with_total_file_size_per_patient.group_by("CurrentGpOds")
            .agg(get_average_file_size_per_patient, get_total_file_size_for_ods_code)
            .rename({"CurrentGpOds": "ods_code"})
        )

        return result.to_dicts()

    def get_number_of_document_types(
        self, dynamodb_scan_result: list[dict]
    ) -> list[dict]:
        file_types_grouped_by_ods_code = defaultdict(set)
        for item in dynamodb_scan_result:
            ods_code = item["CurrentGpOds"]
            file_type = item["ContentType"]
            file_types_grouped_by_ods_code[ods_code].add(file_type)

        return [
            {"ods_code": ods_code, "number_of_document_types": len(file_types)}
            for ods_code, file_types in file_types_grouped_by_ods_code.items()
        ]

    def get_average_number_of_file_per_patient(
        self,
        dynamodb_scan_result: list[dict],
    ) -> list[dict]:
        # we should consider to use pandas / polars for this kind of aggregation
        ods_code_and_patient_number_tuple_for_every_document = [
            (item["CurrentGpOds"], item["NhsNumber"]) for item in dynamodb_scan_result
        ]
        counter_dict = Counter(ods_code_and_patient_number_tuple_for_every_document)
        counter_dict_by_ods_code = defaultdict(list)

        for (
            ods_code,
            _nhs_number,
        ), number_of_file_of_single_patient in counter_dict.items():
            counter_dict_by_ods_code[ods_code].append(number_of_file_of_single_patient)

        average_by_ods_code = [
            {
                "ods_code": ods_code,
                "average_records_per_patient": self.take_average(
                    list_of_number_of_files_of_each_patient
                ),
            }
            for ods_code, list_of_number_of_files_of_each_patient in counter_dict_by_ods_code.items()
        ]
        return average_by_ods_code

    # def get_average_document_size_per_patient(
    #     self,
    #     dynamodb_scan_result: list[dict],
    #     s3_list_objects_result: list[S3ListObjectsResult]
    # ) -> list[dict]:
    #     # we should consider to use pandas / polars for this kind of aggregation
    #     ods_code_and_patient_number_tuple_for_every_document = [
    #         (item.current_gp_ods, item.nhs_number) for item in dynamodb_scan_result
    #     ]
    #     counter_dict = Counter(ods_code_and_patient_number_tuple_for_every_document)
    #     counter_dict_by_ods_code = defaultdict(list)
    #
    #     for (
    #         ods_code,
    #         _nhs_number,
    #     ), number_of_file_of_single_patient in counter_dict.items():
    #         counter_dict_by_ods_code[ods_code].append(number_of_file_of_single_patient)
    #
    #     average_by_ods_code = [
    #         {
    #             "ods_code": ods_code,
    #             "average_records_per_patient": self.take_average(
    #                 list_of_number_of_files_of_each_patient
    #             ),
    #         }
    #         for ods_code, list_of_number_of_files_of_each_patient in counter_dict_by_ods_code.items()
    #     ]
    #     return average_by_ods_cod

    @staticmethod
    def join_results_by_ods_code(results: list[list[dict]]) -> list[dict]:
        # take a nested list of [[{ods_code: xxxxx, property_a: yyyyy}], [{ods_code: xxxxx, property_b: zzzzz}]]
        # join by ods code and return as a flat list of [{ods_code: xxxxx, property_a: yyyyy, property_b: zzzzz}]
        all_result_flatten = itertools.chain(*results)

        joined_by_ods_code = defaultdict(dict)
        for entry in all_result_flatten:
            ods_code = entry["ods_code"]
            joined_by_ods_code[ods_code].update(entry)

        return list(joined_by_ods_code.values())

    @staticmethod
    def to_megabyte(file_size_in_byte: int) -> Decimal:
        return file_size_in_byte / Decimal(1024) / Decimal(1024)

    @staticmethod
    def take_average(list_of_number: list[int]) -> Decimal:
        if list_of_number:
            return sum(list_of_number) / Decimal(len(list_of_number))
        return Decimal(0)
