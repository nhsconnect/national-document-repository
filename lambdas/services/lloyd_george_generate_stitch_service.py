import os
import uuid
from io import BytesIO
from urllib import parse

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.trace_status import TraceStatus
from models.document_reference import DocumentReference
from models.stitch_trace import StitchTrace
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PyPdfError
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import NoAvailableDocument
from utils.filename_utils import extract_page_number
from utils.lambda_exceptions import LGStitchServiceException
from utils.lloyd_george_validator import check_for_number_of_files_match_expected
from utils.utilities import get_file_key_from_s3_url

logger = LoggingService(__name__)


class LloydGeorgeStitchService:
    def __init__(self, stitch_trace: StitchTrace):
        self.lloyd_george_table_name = os.environ.get("LLOYD_GEORGE_DYNAMODB_NAME")
        self.lloyd_george_bucket_name = os.environ.get("LLOYD_GEORGE_BUCKET_NAME")
        self.lifecycle_policy_tag = os.environ.get(
            "STITCHED_FILE_LIFECYCLE_POLICY_TAG", "autodelete"
        )

        self.s3_service = S3Service()
        self.document_service = DocumentService()
        self.stitch_trace_object = stitch_trace
        self.stitch_trace_table = os.environ.get("STITCH_METADATA_DYNAMODB_NAME")
        self.stitch_file_name = f"patient-record-{str(uuid.uuid4())}"
        self.combined_file_folder = "combined_files"

    def handle_stitch_request(self):
        self.stitch_lloyd_george_record()
        self.update_stitch_job_complete()

    def stitch_lloyd_george_record(self):
        try:
            documents_for_stitching = self.get_lloyd_george_record_for_patient()
            if not documents_for_stitching:
                raise LGStitchServiceException(404, LambdaError.StitchNotFound)

            filename_for_stitched_file = f"{self.stitch_file_name}.pdf"
            destination_key = (
                f"{self.combined_file_folder}/{filename_for_stitched_file}"
            )
            ordered_documents = self.prepare_documents_for_stitching(
                documents_for_stitching
            )
            stitched_lg_stream = self.stream_and_stitch_documents(ordered_documents)
            self.stitch_trace_object.total_file_size_in_bytes = (
                stitched_lg_stream.getbuffer().nbytes
            )
            self.upload_stitched_lg_record(
                stitched_lg_stream=stitched_lg_stream,
                filename_on_bucket=destination_key,
            )
            self.stitch_trace_object.stitched_file_location = destination_key

            logger.audit_splunk_info(
                "User has viewed Lloyd George records",
                {"Result": "Successful viewing LG"},
            )

        except (ClientError, PyPdfError, FileNotFoundError, NoAvailableDocument) as e:
            logger.error(
                f"{LambdaError.StitchClient.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(500, LambdaError.StitchClient)

    def stream_and_stitch_documents(
        self, documents: list[DocumentReference]
    ) -> BytesIO:
        writer = PdfWriter()

        for doc in documents:
            s3_key = get_file_key_from_s3_url(doc.file_location)
            memory_stream = self.s3_service.stream_s3_object_to_memory(
                bucket=self.lloyd_george_bucket_name,
                key=s3_key,
            )

            reader = PdfReader(memory_stream)
            for page in reader.pages:
                writer.add_page(page)

        output_stream = BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream

    def prepare_documents_for_stitching(
        self, documents: list[DocumentReference]
    ) -> list[DocumentReference]:
        self.update_trace_status(TraceStatus.PROCESSING)

        sorted_docs = self.sort_documents_by_filenames(documents)
        self.stitch_trace_object.number_of_files = len(sorted_docs)
        self.stitch_trace_object.file_last_updated = self.get_most_recent_created_date(
            sorted_docs
        )

        return sorted_docs

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

    def upload_stitched_lg_record(
        self, stitched_lg_stream: BytesIO, filename_on_bucket: str
    ):
        try:
            extra_args = {
                "Tagging": parse.urlencode({self.lifecycle_policy_tag: "true"}),
                "ContentDisposition": "inline",
                "ContentType": "application/pdf",
            }
            self.s3_service.upload_file_obj(
                file_obj=stitched_lg_stream,
                s3_bucket_name=self.lloyd_george_bucket_name,
                file_key=filename_on_bucket,
                extra_args=extra_args,
            )
            logger.info(
                f"Uploaded stitched file to {self.lloyd_george_bucket_name} with key {filename_on_bucket}"
            )
        except ValueError as e:
            logger.error(
                f"{LambdaError.StitchCloudFront.to_str()}: {str(e)}",
                {"Result": "Failed to format CloudFront URL."},
            )
            raise LGStitchServiceException(500, LambdaError.StitchCloudFront)

    @staticmethod
    def get_most_recent_created_date(documents: list[DocumentReference]) -> str:
        return max(doc.created for doc in documents)

    @staticmethod
    def get_total_file_size_in_bytes(file_streams: list[BytesIO]) -> int:
        return sum(len(f.getbuffer()) for f in file_streams)

    def update_stitch_job_complete(self):
        logger.info("Writing stitch trace to db")
        self.stitch_trace_object.job_status = TraceStatus.COMPLETED
        self.document_service.dynamo_service.update_item(
            table_name=self.stitch_trace_table,
            key_pair={"ID": self.stitch_trace_object.id},
            updated_fields=self.stitch_trace_object.model_dump(
                by_alias=True, exclude={"id"}
            ),
        )

    def update_trace_status(self, trace_status: TraceStatus):
        self.stitch_trace_object.job_status = trace_status
        self.document_service.dynamo_service.update_item(
            table_name=self.stitch_trace_table,
            key_pair={"ID": self.stitch_trace_object.id},
            updated_fields=self.stitch_trace_object.model_dump(
                by_alias=True, include={"job_status"}
            ),
        )

    def get_lloyd_george_record_for_patient(
        self,
    ) -> list[DocumentReference]:

        available_docs = (
            self.document_service.get_available_lloyd_george_record_for_patient(
                self.stitch_trace_object.nhs_number
            )
        )
        check_for_number_of_files_match_expected(
            available_docs[0].file_name, len(available_docs)
        )
        return available_docs
