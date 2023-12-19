import json
import os
import shutil
import tempfile
from urllib import parse
from urllib.parse import urlparse

from botocore.exceptions import ClientError
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from pypdf.errors import PyPdfError
from services.document_service import DocumentService
from services.pdf_stitch_service import stitch_pdf
from services.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.exceptions import LGStitchServiceException
from utils.filename_utils import extract_page_number
from utils.utilities import create_reference_id

logger = LoggingService(__name__)


class LloydGeorgeStitchService:
    def __init__(self):
        self.lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        self.lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        self.lifecycle_policy_tag = os.environ.get(
            "STITCHED_FILE_LIFECYCLE_POLICY_TAG", "autodelete"
        )

        self.s3_service = S3Service()
        self.document_service = DocumentService()
        self.temp_folder = tempfile.mkdtemp()

    def stitch_lloyd_george_record(self, nhs_number: str) -> str:
        try:
            lg_records = self.get_lloyd_george_record_for_patient(nhs_number)
            if len(lg_records) == 0:
                raise LGStitchServiceException(
                    404, f"Lloyd george record not found for patient {nhs_number}"
                )

            ordered_lg_records = self.sort_documents_by_filenames(lg_records)
            all_lg_parts = self.download_lloyd_george_files(ordered_lg_records)
        except ClientError as e:
            logger.error(e, {"Result": f"Unsuccessful viewing LG due to {str(e)}"})
            raise LGStitchServiceException(
                500, f"Unable to retrieve documents for patient {nhs_number}"
            )

        try:
            filename_for_stitched_file = self.make_filename_for_stitched_file(
                lg_records
            )
            stitched_lg_record = stitch_pdf(all_lg_parts, self.temp_folder)
            number_of_files = len(all_lg_parts)
            last_updated = self.get_most_recent_created_date(lg_records)
            total_file_size = self.get_total_file_size(all_lg_parts)

            presign_url = self.upload_stitched_lg_record_and_retrieve_presign_url(
                stitched_lg_record=stitched_lg_record,
                filename_on_bucket=f"{nhs_number}/{filename_for_stitched_file}",
            )
            response = {
                "number_of_files": number_of_files,
                "last_updated": last_updated,
                "presign_url": presign_url,
                "total_file_size_in_byte": total_file_size,
            }
            logger.audit_splunk_info(
                "User has viewed Lloyd George records",
                {"Result": "Successful viewing LG"},
            )

            return json.dumps(response)
        except (ClientError, PyPdfError, FileNotFoundError) as e:
            logger.error(e, {"Result": f"Unsuccessful viewing LG due to {str(e)}"})
            raise LGStitchServiceException(
                500, "Unable to return stitched pdf file due to internal error"
            )
        finally:
            shutil.rmtree(self.temp_folder)

    def get_lloyd_george_record_for_patient(
        self, nhs_number: str
    ) -> list[DocumentReference]:
        try:
            return self.document_service.fetch_available_document_references_by_type(
                nhs_number, SupportedDocumentTypes.LG.value
            )
        except ClientError as e:
            logger.error(e, {"Result": f"Unsuccessful viewing LG due to {str(e)}"})
            raise LGStitchServiceException(
                500, f"Unable to retrieve documents for patient {nhs_number}"
            )

    @staticmethod
    def sort_documents_by_filenames(
        documents: list[DocumentReference],
    ) -> list[DocumentReference]:
        try:
            return sorted(documents, key=lambda doc: extract_page_number(doc.file_name))
        except (KeyError, ValueError) as e:
            nhs_number = documents[0].nhs_number
            logger.error(
                e,
                {
                    "Result": "Unsuccessful viewing LG due to some filenames not following naming convention"
                },
            )
            raise LGStitchServiceException(
                500, f"Unable to stitch documents for patient {nhs_number}"
            )

    def download_lloyd_george_files(
        self,
        ordered_lg_records: list[DocumentReference],
    ) -> list[str]:
        all_lg_parts = []

        for lg_part in ordered_lg_records:
            file_location_on_s3 = lg_part.file_location
            s3_file_path = urlparse(file_location_on_s3).path.lstrip("/")
            local_file_name = os.path.join(self.temp_folder, create_reference_id())
            self.s3_service.download_file(
                self.lloyd_george_bucket_name, s3_file_path, local_file_name
            )
            all_lg_parts.append(local_file_name)

        return all_lg_parts

    @staticmethod
    def make_filename_for_stitched_file(documents: list[DocumentReference]) -> str:
        sample_doc = documents[0]
        base_filename = sample_doc.file_name
        end_of_total_page_numbers = base_filename.index("_")

        return "Combined" + base_filename[end_of_total_page_numbers:]

    def upload_stitched_lg_record_and_retrieve_presign_url(
        self,
        stitched_lg_record: str,
        filename_on_bucket: str,
    ) -> str:
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
            s3_bucket_name=self.lloyd_george_bucket_name, file_key=filename_on_bucket
        )
        return presign_url_response

    @staticmethod
    def get_most_recent_created_date(documents: list[DocumentReference]) -> str:
        return max(doc.created for doc in documents)

    @staticmethod
    def get_total_file_size(filepaths: list[str]) -> int:
        # Return the sum of a list of files (unit: byte)
        return sum(os.path.getsize(filepath) for filepath in filepaths)
