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
from utils.exceptions import FileUploadInProgress, NoAvailableDocument
from utils.lambda_exceptions import LGStitchServiceException
from utils.lloyd_george_validator import LGInvalidFilesException

logger = LoggingService(__name__)


class LloydGeorgeStitchJobService:
    def __init__(self):
        get_document_presign_url_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(
            custom_aws_role=get_document_presign_url_aws_role_arn
        )
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()
        self.stitch_trace_table = os.environ["STITCH_METADATA_DYNAMODB_NAME"]
        self.lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]

        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")
        self.lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]

    def create_stitch_job(self, nhs_number: str) -> TraceStatus:
        try:
            self.check_lloyd_george_record_for_patient(nhs_number)
            stitch_trace_result = self.query_stitch_trace_with_nhs_number(nhs_number)
            if stitch_trace_result:
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

    def process_stitch_trace_response(self, stitch_trace: StitchTrace):
        match stitch_trace.job_status:
            case TraceStatus.FAILED:
                raise LGStitchServiceException(500, LambdaError.StitchNoService)
            case TraceStatus.PENDING:
                return DocumentStitchJob(jobStatus=TraceStatus.PENDING, presignedUrl="")

            case TraceStatus.PROCESSING:
                return DocumentStitchJob(
                    jobStatus=TraceStatus.PROCESSING, presignedUrl=""
                )
            case TraceStatus.COMPLETED:
                presigned_url = self.create_document_stitch_presigned_url(
                    stitch_trace.stitched_file_location
                )
                logger.audit_splunk_info(
                    "User has viewed Lloyd George records",
                    {"Result": "Successful Stitching"},
                )

                return DocumentStitchJob(
                    jobStatus=TraceStatus.COMPLETED,
                    presignedUrl=presigned_url,
                    numberofFiles=stitch_trace.number_of_files,
                    lastUpdated=stitch_trace.file_last_updated,
                    totalFileSizeInByte=stitch_trace.total_file_size_in_byte,
                )

    def validate_latest_stitch_trace(self, response: dict) -> StitchTrace | None:
        try:
            stitch_trace_dynamo_response = response.get("Items", [])
            if not stitch_trace_dynamo_response:
                return None
            latest_stitch_trace = StitchTrace.model_validate(
                stitch_trace_dynamo_response[0]
            )
            for stitch_trace_response in stitch_trace_dynamo_response:
                stitch_trace = StitchTrace.model_validate(stitch_trace_response)
                if stitch_trace.created > latest_stitch_trace.created:
                    latest_stitch_trace = stitch_trace
            return latest_stitch_trace
        except (KeyError, IndexError, ValidationError) as e:
            logger.error(
                f"{LambdaError.ManifestMissingJob.to_str()}: {str(e)}",
                {"Result": "Failed to create document manifest job"},
            )
            raise LGStitchServiceException(404, LambdaError.ManifestMissingJob)

    def query_stitch_trace_with_nhs_number(self, nhs_number: str) -> StitchTrace:
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
        return self.validate_latest_stitch_trace(response)

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

    def check_lloyd_george_record_for_patient(self, nhs_number) -> None:
        try:
            self.document_service.get_available_lloyd_george_record_for_patient(
                nhs_number
            )
        except ClientError as e:
            logger.error(
                f"{LambdaError.StitchDB.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(500, LambdaError.StitchDB)
        except FileUploadInProgress as e:
            logger.error(
                f"{LambdaError.UploadInProgressError.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(
                status_code=423, error=LambdaError.UploadInProgressError
            )
        except NoAvailableDocument as e:
            logger.error(
                f"{LambdaError.StitchNotFound.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(
                status_code=404, error=LambdaError.StitchNotFound
            )
        except LGInvalidFilesException as e:
            logger.error(
                f"{LambdaError.IncompleteRecordError.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(
                status_code=400, error=LambdaError.IncompleteRecordError
            )
