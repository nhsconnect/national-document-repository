import os

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from enums.trace_status import TraceStatus
from models.document_reference import DocumentReference
from models.stitch_trace import DocumentStitchJob, StitchTrace
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.dynamo_utils import filter_uploaded_docs_and_recently_uploading_docs
from utils.exceptions import FileUploadInProgress
from utils.filename_utils import extract_page_number
from utils.lambda_exceptions import LGStitchServiceException
from utils.lloyd_george_validator import (
    LGInvalidFilesException,
    check_for_number_of_files_match_expected,
)

logger = LoggingService(__name__)


class LloydGeorgeStitchJobService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()
        self.stitch_trace_table = os.environ["STITCH_STORE_DYNAMODB_NAME"]
        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")
        get_document_presign_url_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(
            custom_aws_role=get_document_presign_url_aws_role_arn
        )
        self.lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]

    def create_stitch_job(self, nhs_number: str) -> str:
        try:
            lg_records = self.get_lloyd_george_record_for_patient(nhs_number)
            ordered_lg_records = self.sort_documents_by_filenames(lg_records)
            job_id = self.write_stitch_trace(ordered_lg_records)
        except ClientError as e:
            logger.error(
                f"{LambdaError.StitchNoService.to_str()}: {str(e)}",
                {"Result": "Creating Lloyd George stitching job failed"},
            )
            raise LGStitchServiceException(
                500,
                LambdaError.StitchNoService,
            )

        return job_id

    def write_stitch_trace(
        self,
        ordered_lg_records: list[DocumentReference],
    ) -> str:
        logger.info("Writing Document Stitch trace to db")

        stitch_trace = StitchTrace(documents_to_stitch=ordered_lg_records)
        self.dynamo_service.create_item(
            self.stitch_trace_table, stitch_trace.model_dump(by_alias=True)
        )

        return str(stitch_trace.job_id)

    def get_lloyd_george_record_for_patient(
        self, nhs_number: str
    ) -> list[DocumentReference]:
        try:
            filter_expression = filter_uploaded_docs_and_recently_uploading_docs()
            available_docs = (
                self.document_service.fetch_available_document_references_by_type(
                    nhs_number,
                    SupportedDocumentTypes.LG,
                    query_filter=filter_expression,
                )
            )

            file_in_progress_message = (
                "The patients Lloyd George record is in the process of being uploaded"
            )
            if not available_docs:
                logger.error(
                    f"{LambdaError.StitchNotFound.to_str()}",
                    {"Result": "Lloyd George stitching failed"},
                )
                raise LGStitchServiceException(
                    404,
                    LambdaError.StitchNotFound,
                )
            for document in available_docs:
                if document.uploading and not document.uploaded:
                    raise FileUploadInProgress(file_in_progress_message)

            check_for_number_of_files_match_expected(
                available_docs[0].file_name, len(available_docs)
            )

            return available_docs
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
        except LGInvalidFilesException as e:
            logger.error(
                f"{LambdaError.IncompleteRecordError.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(
                status_code=400, error=LambdaError.IncompleteRecordError
            )

    @staticmethod
    def sort_documents_by_filenames(
        documents: list[DocumentReference],
    ) -> list[DocumentReference]:
        try:
            return sorted(documents, key=lambda doc: extract_page_number(doc.file_name))
        except (KeyError, ValueError) as e:
            logger.error(
                f"{LambdaError.StitchValidation.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(500, LambdaError.StitchValidation)

    def query_document_stitch_job(self, job_id: str):
        stitch_trace = self.query_stitch_trace(job_id=job_id)

        match stitch_trace.job_status:
            case TraceStatus.FAILED:
                raise LGStitchServiceException(500, LambdaError.StitchNoService)
            case TraceStatus.PENDING:
                return DocumentStitchJob(jobStatus=TraceStatus.PENDING, url="")
            case TraceStatus.PROCESSING:
                return DocumentStitchJob(jobStatus=TraceStatus.PROCESSING, url="")
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
                    url=presigned_url,
                    number_of_files=stitch_trace.number_of_files,
                    last_updated=stitch_trace.file_last_updated,
                    total_file_size_in_byte=stitch_trace.total_file_size_in_byte,
                )

    def query_stitch_trace(self, job_id: str) -> StitchTrace:
        response = self.dynamo_service.query_with_requested_fields(
            table_name=self.stitch_trace_table,
            index_name="JobIdIndex",
            search_key="JobId",
            search_condition=job_id,
        )

        try:
            stitch_trace = StitchTrace.model_validate(response["Items"][0])
            return stitch_trace
        except (KeyError, IndexError, ValidationError) as e:
            logger.error(
                f"{LambdaError.ManifestMissingJob.to_str()}: {str(e)}",
                {"Result": "Failed to create document manifest job"},
            )
            raise LGStitchServiceException(404, LambdaError.ManifestMissingJob)

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
