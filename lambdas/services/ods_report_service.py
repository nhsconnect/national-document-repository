import os
import tempfile
from datetime import datetime

from enums.dynamo_filter import AttributeOperator
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from enums.repository_role import RepositoryRole
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder
from utils.lambda_exceptions import OdsReportException
from utils.request_context import request_context

logger = LoggingService(__name__)


class OdsReportService:
    def __init__(self):
        download_report_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(custom_aws_role=download_report_aws_role_arn)
        self.dynamo_service = DynamoDBService()
        self.table_name = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.reports_bucket = os.environ["STATISTICAL_REPORTS_BUCKET"]
        self.output_file_suffix = ".csv"
        self.temp_output_dir = tempfile.mkdtemp()

    def get_nhs_numbers_by_ods(self, ods_code: str, is_pre_signed_need: bool = False):
        results = self.scan_table_with_filter(ods_code)
        nhs_numbers = {
            item.get(DocumentReferenceMetadataFields.NHS_NUMBER.value)
            for item in results
            if item.get(DocumentReferenceMetadataFields.NHS_NUMBER.value)
        }
        return self.create_and_save_ods_report(
            ods_code, nhs_numbers, is_pre_signed_need
        )

    def scan_table_with_filter(self, ods_code):
        ods_codes = [ods_code]
        if (
            request_context.authorization
            and request_context.authorization.get("repository_role")
            == RepositoryRole.PCSE
        ):
            ods_codes = [
                PatientOdsInactiveStatus.SUSPENDED,
                PatientOdsInactiveStatus.DECEASED,
            ]
        ods_filter_expression = self.build_filter_expression(ods_codes)
        results = []

        response = self.dynamo_service.scan_table(
            table_name=self.table_name,
            filter_expression=ods_filter_expression,
        )
        results += response["Items"]

        while "LastEvaluatedKey" in response:
            response = self.dynamo_service.scan_table(
                exclusive_start_key=response["LastEvaluatedKey"],
                table_name=self.table_name,
                filter_expression=ods_filter_expression,
            )
            results.extend(response.get("Items", []))
        if not results:
            logger.info("No records found for ODS code {}".format(ods_code))
            raise OdsReportException(404, LambdaError.NoDataFound)

        return results

    def build_filter_expression(self, ods_codes):
        filter_builder = DynamoQueryFilterBuilder()
        return filter_builder.add_condition(
            attribute=DocumentReferenceMetadataFields.CURRENT_GP_ODS.value,
            attr_operator=AttributeOperator.IN,
            filter_value=ods_codes,
        ).build()

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
            logger.info("No records found for ODS code {}".format(ods_code))
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

    def create_and_save_ods_report(
        self, ods_code, nhs_numbers, create_pre_signed_url: bool = False
    ):
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d_%H-%M")
        file_name = (
            "NDR_"
            + ods_code
            + f"_{len(nhs_numbers)}_"
            + formatted_time
            + self.output_file_suffix
        )
        temp_file_path = os.path.join(self.temp_output_dir, file_name)
        self.create_report(temp_file_path, nhs_numbers, ods_code)
        self.save_report_to_s3(ods_code, file_name, temp_file_path)
        logger.info(
            f"Query completed. {len(nhs_numbers)} items written to {file_name}."
        )
        if create_pre_signed_url:
            return self.get_pre_signed_url(ods_code, file_name)

    def create_report(self, file_name, nhs_numbers, ods_code):
        with open(file_name, "w") as f:
            f.write(
                f"Total number of patients for ODS code {ods_code}: {len(nhs_numbers)}\n"
            )
            f.write("NHS Numbers:\n")
            f.writelines(f"{nhs_number}\n" for nhs_number in nhs_numbers)

    def save_report_to_s3(self, ods_code, file_name, temp_file_path):
        logger.info("Uploading the csv report to S3 bucket...")
        self.s3_service.upload_file(
            s3_bucket_name=self.reports_bucket,
            file_key=f"ods-reports/{ods_code}/{file_name}",
            file_name=temp_file_path,
        )

    def get_pre_signed_url(self, ods_code, file_name):
        return self.s3_service.create_download_presigned_url(
            s3_bucket_name=self.reports_bucket,
            file_key=f"ods-reports/{ods_code}/{file_name}",
        )
