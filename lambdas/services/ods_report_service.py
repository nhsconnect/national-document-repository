import os
from datetime import datetime

from enums.dynamo_filter import AttributeOperator
from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder

logger = LoggingService(__name__)

class OdsReportService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.table_name = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        # self.s3_service = S3Service()
        # self.reports_bucket = os.environ["STATISTICAL_REPORTS_BUCKET"]
        self.output_file_suffix = "_ods_report.csv"

    def get_nhs_numbers_by_ods(self, ods_code):
        results = self.scan_table_with_filter(ods_code)
        nhs_numbers = set()
        for item in results:
            nhs_number = item.get(DocumentReferenceMetadataFields.NHS_NUMBER.value)
            if nhs_number:
                nhs_numbers.add(nhs_number)
        self.create_and_save_ods_report(ods_code, nhs_numbers)

    def scan_table_with_filter(self, ods_code):
        filter_builder = DynamoQueryFilterBuilder()
        ods_filter_expression = filter_builder.add_condition(
            attribute=DocumentReferenceMetadataFields.CURRENT_GP_ODS.value,
            attr_operator=AttributeOperator.EQUAL,
            filter_value=ods_code,
        ).build()
        results = []

        response = self.dynamo_service.scan_table(
            table_name=self.table_name,
            filter_expression=ods_filter_expression,
        )
        results += response["Items"]

        if not response["Items"]:
            print("No records found for ODS code {}".format(ods_code))

        while "LastEvaluatedKey" in response:
            response = self.dynamo_service.scan_table(
                exclusive_start_key=response["LastEvaluatedKey"],
                table_name=self.table_name,
                filter_expression=ods_filter_expression,
            )
            results += response["Items"]
        return results

    def query_table_by_index(self, ods_code):
        results = []

        response = self.dynamo_service.query_table_by_index(
            table_name=self.table_name,
            index_name="OdsCodeIndex",
            search_key=DocumentReferenceMetadataFields.CURRENT_GP_ODS.value,
            search_condition=ods_code,
        )
        results += response["Items"]

        if not response["Items"]:
            print("No records found for ODS code {}".format(ods_code))
        while "LastEvaluatedKey" in response:
            response = self.dynamo_service.query_table_by_index(
                table_name=self.table_name,
                index_name="OdsCodeIndex",
                exclusive_start_key=response["LastEvaluatedKey"],
                search_key=DocumentReferenceMetadataFields.CURRENT_GP_ODS.value,
                search_condition=ods_code,
            )
            results += response["Items"]
        return results

    def create_and_save_ods_report(self, ods_code, nhs_numbers):
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d_%H:%M")

        file_name = ods_code + "_" + formatted_time + self.output_file_suffix
        with open(file_name, "w") as f:
            f.write(
                f"Total number of patients for ODS code {ods_code}: {len(nhs_numbers)} at {formatted_time}\n"
            )
            f.writelines(f"{nhs_number}\n" for nhs_number in nhs_numbers)
        logger.info("Uploading the csv report to S3 bucket...")
        # self.s3_service.upload_file(
        #     s3_bucket_name=self.reports_bucket,
        #     file_key=f"ods-reports/{ods_code}/{file_name}",
        #     file_name=file_name,
        # )
        print(f"Query completed. {len(nhs_numbers)} items written to {file_name}.")




