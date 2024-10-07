import os
import shutil
import tempfile
from urllib import parse

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.trace_status import TraceStatus
from models.document_reference import DocumentReference
from models.stitch_trace import StitchTrace
from pypdf.errors import PyPdfError
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from services.pdf_stitch_service import stitch_pdf
from utils.audit_logging_setup import LoggingService
from utils.filename_utils import extract_page_number
from utils.lambda_exceptions import LGStitchServiceException
from utils.utilities import create_reference_id, get_file_key_from_s3_url

logger = LoggingService(__name__)


class LloydGeorgeStitchService:
    def __init__(self, stitch_trace: StitchTrace):
        self.lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        self.lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        self.lifecycle_policy_tag = os.environ.get(
            "STITCHED_FILE_LIFECYCLE_POLICY_TAG", "autodelete"
        )
        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")

        self.s3_service = S3Service()
        self.document_service = DocumentService()
        self.temp_folder = tempfile.mkdtemp()
        self.stitch_trace_object = stitch_trace
        self.stitch_trace_table = os.environ["STITCH_STORE_DYNAMODB_NAME"]
        self.stitch_file_name = f"patient-record-{stitch_trace.job_id}.pdf"
        self.stitch_file_path = os.path.join(self.temp_folder, self.stitch_file_name)

    def handle_stitch_request(self):
        self.update_processing_status()
        self.stitch_lloyd_george_record()
        self.update_dynamo_with_fields()

    def stitch_lloyd_george_record(self):
        try:
            all_lg_parts = self.download_lloyd_george_files(
                self.stitch_trace_object.documents_to_stitch
            )
        except ClientError as e:
            logger.error(
                f"{LambdaError.StitchNoService.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(
                500,
                LambdaError.StitchNoService,
            )

        try:
            stitched_lg_record = stitch_pdf(all_lg_parts, self.temp_folder)
            filename_for_stitched_file = os.path.basename(stitched_lg_record)
            self.stitch_trace_object.number_of_files = len(all_lg_parts)
            self.stitch_trace_object.file_last_updated = (
                self.get_most_recent_created_date(
                    self.stitch_trace_object.documents_to_stitch
                )
            )
            self.stitch_trace_object.total_file_size_in_byte = (
                self.get_total_file_size_in_bytes(all_lg_parts)
            )

            self.upload_stitched_lg_record(
                stitched_lg_record=stitched_lg_record,
                filename_on_bucket=f"combined_files/{filename_for_stitched_file}",
            )
            logger.audit_splunk_info(
                "User has viewed Lloyd George records",
                {"Result": "Successful viewing LG"},
            )

        except (ClientError, PyPdfError, FileNotFoundError) as e:
            logger.error(
                f"{LambdaError.StitchClient.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(500, LambdaError.StitchClient)
        finally:
            shutil.rmtree(self.temp_folder)

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

    def download_lloyd_george_files(
        self,
        ordered_lg_records: list[DocumentReference],
    ) -> list[str]:
        all_lg_parts = []

        for lg_part in ordered_lg_records:
            file_location_on_s3 = lg_part.file_location
            s3_file_path = get_file_key_from_s3_url(file_location_on_s3)
            local_file_name = os.path.join(self.temp_folder, create_reference_id())
            self.s3_service.download_file(
                self.lloyd_george_bucket_name, s3_file_path, local_file_name
            )
            all_lg_parts.append(local_file_name)

        return all_lg_parts

    def upload_stitched_lg_record(
        self, stitched_lg_record: str, filename_on_bucket: str
    ):
        try:
            extra_args = {
                "Tagging": parse.urlencode({self.lifecycle_policy_tag: "true"}),
                "ContentDisposition": "inline",
                "ContentType": "application/pdf",
            }
            self.s3_service.upload_file_with_extra_args(
                file_name=stitched_lg_record,
                s3_bucket_name=self.lloyd_george_bucket_name,
                file_key=filename_on_bucket,
                extra_args=extra_args,
            )

        except ValueError as e:
            logger.error(
                f"{LambdaError.StitchCloudFront.to_str()}: {str(e)}",
                {"Result": "Failed to format CloudFront URL due to invalid input."},
            )
            raise LGStitchServiceException(500, LambdaError.StitchCloudFront)

    @staticmethod
    def get_most_recent_created_date(documents: list[DocumentReference]) -> str:
        return max(doc.created for doc in documents)

    @staticmethod
    def get_total_file_size_in_bytes(filepaths: list[str]) -> int:
        return sum(os.path.getsize(filepath) for filepath in filepaths)

    def update_dynamo_with_fields(self):
        logger.info("Writing stitch trace to db")
        self.document_service.dynamo_service.update_item(
            self.stitch_trace_table,
            self.stitch_trace_object.id,
            self.stitch_trace_object.model_dump(by_alias=True),
        )

    def update_failed_status(self):
        self.stitch_trace_object.job_status = TraceStatus.FAILED
        self.update_dynamo_with_fields()

    def update_processing_status(self):
        self.stitch_trace_object.job_status = TraceStatus.PROCESSING
        self.update_dynamo_with_fields()
