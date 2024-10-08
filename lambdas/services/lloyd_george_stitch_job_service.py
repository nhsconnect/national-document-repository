import os
from datetime import datetime, timedelta

from botocore.exceptions import ClientError
from enums.dynamo_filter import AttributeOperator
from enums.lambda_error import LambdaError
from enums.trace_status import TraceStatus
from models.stitch_trace import DocumentStitchJob, StitchTrace
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder
from utils.lambda_exceptions import LGStitchServiceException

logger = LoggingService(__name__)


class LloydGeorgeStitchJobService:
    def __init__(self):
        get_document_presign_url_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(
            custom_aws_role=get_document_presign_url_aws_role_arn
        )
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()
        self.stitch_trace_table = os.environ["STITCH_STORE_DYNAMODB_NAME"]
        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")
        self.lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]

    def create_stitch_job(self, nhs_number: str) -> TraceStatus:
        try:
            stitch_trace_result = self.query_stitch_trace_with_nhs_number(nhs_number)
            if (
                stitch_trace_result
                and stitch_trace_result.job_status != TraceStatus.NO_DOCUMENTS
            ):
                return stitch_trace_result.job_status
            else:
                return self.write_stitch_trace(nhs_number)
        except ClientError as e:
            logger.error(
                f"{LambdaError.StitchNoService.to_str()}: {str(e)}",
                {"Result": "Creating Lloyd George stitching job failed"},
            )
            raise LGStitchServiceException(
                500,
                LambdaError.StitchNoService,
            )

    def write_stitch_trace(
        self,
        nhs_number: str,
    ) -> TraceStatus:
        logger.info("Writing Document Stitch trace to db")

        expiration_time = self.get_expiration_time()

        stitch_trace = StitchTrace(nhs_number=nhs_number, expire_at=expiration_time)
        self.dynamo_service.create_item(
            self.stitch_trace_table, stitch_trace.model_dump(by_alias=True)
        )
        return stitch_trace.job_status

    def get_expiration_time(self):
        current_time = datetime.now()
        tomorrow = current_time + timedelta(days=1)
        tomorrow_1am = tomorrow.replace(hour=1, minute=0, second=0, microsecond=0)
        return int(tomorrow_1am.timestamp())

    def query_document_stitch_job(self, nhs_number: str):
        stitch_trace = self.query_stitch_trace_with_nhs_number(nhs_number=nhs_number)
        return self.process_stitch_trace_response(stitch_trace)

    def process_stitch_trace_response(self, stitch_trace: list[StitchTrace]):
        latest_stitch_trace = stitch_trace[0]
        for stitch_trace in stitch_trace:
            if stitch_trace.created > latest_stitch_trace.created:
                latest_stitch_trace = stitch_trace

        match latest_stitch_trace.job_status:
            case TraceStatus.FAILED:
                raise LGStitchServiceException(500, LambdaError.StitchNoService)
            case TraceStatus.PENDING:
                return DocumentStitchJob(jobStatus=TraceStatus.PENDING, presignedUrl="")
            case TraceStatus.NO_DOCUMENTS:
                raise LGStitchServiceException(
                    404,
                    LambdaError.StitchNotFound,
                )
            case TraceStatus.PROCESSING:
                return DocumentStitchJob(
                    jobStatus=TraceStatus.PROCESSING, presignedUrl=""
                )
            case TraceStatus.COMPLETED:
                presigned_url = self.create_document_stitch_presigned_url(
                    latest_stitch_trace.stitched_file_location
                )
                logger.audit_splunk_info(
                    "User has viewed Lloyd George records",
                    {"Result": "Successful Stitching"},
                )

                return DocumentStitchJob(
                    jobStatus=TraceStatus.COMPLETED,
                    presignedUrl=presigned_url,
                    numberofFiles=latest_stitch_trace.number_of_files,
                    lastUpdated=latest_stitch_trace.file_last_updated,
                    totalFileSizeInByte=latest_stitch_trace.total_file_size_in_byte,
                )

    def validate_stitch_trace(self, response: dict) -> list[StitchTrace] | None:
        try:
            stitch_trace_records = []
            stitch_trace_dynamo_response = response.get("Items", [])
            if not stitch_trace_dynamo_response:
                return None
            for stitch_trace in stitch_trace_dynamo_response:
                stitch_trace_records.append(StitchTrace.model_validate(stitch_trace))
            return stitch_trace_records
        except (KeyError, IndexError, ValidationError) as e:
            logger.error(
                f"{LambdaError.ManifestMissingJob.to_str()}: {str(e)}",
                {"Result": "Failed to create document manifest job"},
            )
            raise LGStitchServiceException(404, LambdaError.ManifestMissingJob)

    def query_stitch_trace_with_nhs_number(self, nhs_number: str) -> list[StitchTrace]:
        filter_builder = DynamoQueryFilterBuilder()
        delete_filter_expression = filter_builder.add_condition(
            attribute="Deleted",
            attr_operator=AttributeOperator.EQUAL,
            filter_value=False,
        ).build()
        response = self.dynamo_service.query_with_requested_fields(
            table_name=self.stitch_trace_table,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=nhs_number,
            query_filter=delete_filter_expression,
        )
        return self.validate_stitch_trace(response)

    def create_document_stitch_presigned_url(self, stitched_file_location):
        presign_url_response = self.s3_service.create_download_presigned_url(
            s3_bucket_name=self.lloyd_george_bucket_name,
            file_key=stitched_file_location,
        )
        return self.format_cloudfront_url(presign_url_response, self.cloudfront_url)

    def format_cloudfront_url(self, presign_url: str, cloudfront_domain: str) -> str:
        url_parts = presign_url.split("/")
        if len(url_parts) < 4:
            raise ValueError("Invalid presigned URL format")

        path_parts = url_parts[3:]
        formatted_url = f"https://{cloudfront_domain}/{'/'.join(path_parts)}"
        return formatted_url
