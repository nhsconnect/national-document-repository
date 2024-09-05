import json
import os
import shutil
import tempfile
from urllib import parse

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from pypdf.errors import PyPdfError
from services.base.s3_service import S3Service
from services.document_service import DocumentService
from services.pdf_stitch_service import stitch_pdf
from utils.audit_logging_setup import LoggingService
from utils.dynamo_utils import filter_uploaded_docs_and_recently_uploading_docs
from utils.exceptions import FileUploadInProgress
from utils.filename_utils import extract_page_number
from utils.lambda_exceptions import LGStitchServiceException
from utils.lloyd_george_validator import (
    LGInvalidFilesException,
    check_for_number_of_files_match_expected,
)
from utils.utilities import create_reference_id, get_file_key_from_s3_url

logger = LoggingService(__name__)


class LloydGeorgeStitchService:
    def __init__(self):
        self.lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        self.lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        self.lifecycle_policy_tag = os.environ.get(
            "STITCHED_FILE_LIFECYCLE_POLICY_TAG", "autodelete"
        )
        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")

        get_document_presign_url_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(
            custom_aws_role=get_document_presign_url_aws_role_arn
        )
        self.document_service = DocumentService()
        self.temp_folder = tempfile.mkdtemp()

    def stitch_lloyd_george_record(self, nhs_number: str) -> str:
        try:
            lg_records = self.get_lloyd_george_record_for_patient(nhs_number)
            ordered_lg_records = self.sort_documents_by_filenames(lg_records)
            all_lg_parts = self.download_lloyd_george_files(ordered_lg_records)
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
            number_of_files = len(all_lg_parts)
            last_updated = self.get_most_recent_created_date(lg_records)
            total_file_size_in_byte = self.get_total_file_size_in_bytes(all_lg_parts)

            presign_url = self.upload_stitched_lg_record_and_retrieve_presign_url(
                stitched_lg_record=stitched_lg_record,
                filename_on_bucket=f"combined_files/{filename_for_stitched_file}",
                cloudfront_url=self.cloudfront_url,
            )
            response = {
                "number_of_files": number_of_files,
                "last_updated": last_updated,
                "presign_url": presign_url,
                "total_file_size_in_byte": total_file_size_in_byte,
            }
            logger.audit_splunk_info(
                "User has viewed Lloyd George records",
                {"Result": "Successful viewing LG"},
            )

            return json.dumps(response)
        except (ClientError, PyPdfError, FileNotFoundError) as e:
            logger.error(
                f"{LambdaError.StitchClient.to_str()}: {str(e)}",
                {"Result": "Lloyd George stitching failed"},
            )
            raise LGStitchServiceException(500, LambdaError.StitchClient)
        finally:
            shutil.rmtree(self.temp_folder)

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
                {"Result": "Failed to create document manifest"},
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

    def upload_stitched_lg_record_and_retrieve_presign_url(
        self, stitched_lg_record: str, filename_on_bucket: str, cloudfront_url: str
    ) -> str:
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

            presign_url_response = self.s3_service.create_download_presigned_url(
                s3_bucket_name=self.lloyd_george_bucket_name,
                file_key=filename_on_bucket,
            )
            return self.format_cloudfront_url(presign_url_response, cloudfront_url)

        except ValueError as e:
            logger.error(
                f"{LambdaError.StitchCloudFront.to_str()}: {str(e)}",
                {"Result": "Failed to format CloudFront URL due to invalid input."},
            )
            raise LGStitchServiceException(500, LambdaError.StitchCloudFront)


def format_cloudfront_url(self, presign_url: str, cloudfront_domain: str) -> str:
    url_parts = presign_url.split("/")
    if len(url_parts) < 4:
        raise ValueError("Invalid presigned URL format")

    path_parts = url_parts[3:]
    formatted_url = f"https://{cloudfront_domain}/{'/'.join(path_parts)}"
    return formatted_url

    @staticmethod
    def get_most_recent_created_date(documents: list[DocumentReference]) -> str:
        return max(doc.created for doc in documents)

    @staticmethod
    def get_total_file_size_in_bytes(filepaths: list[str]) -> int:
        return sum(os.path.getsize(filepath) for filepath in filepaths)
