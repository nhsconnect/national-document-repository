import os

from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException
from utils.filename_utils import (
    assemble_lg_valid_file_name_full_path,
    extract_date_from_bulk_upload_file_name,
    extract_document_number_bulk_upload_file_name,
    extract_document_path,
    extract_nhs_number_from_bulk_upload_file_name,
    extract_patient_name_from_bulk_upload_file_name,
)

logger = LoggingService(__name__)


class MetadataUsbPreprocessorService:
    def validate_record_filename(self, file_path: str) -> str:

        directory_path, file_name = extract_document_path(file_path)
        file_extension = os.path.splitext(file_name)[1]

        if file_extension != ".pdf":
            logger.info(f"Rejecting file as it is not a PDF: {file_path}")
            raise InvalidFileNameException("Only PDF files are supported.")

        try:
            numbers = extract_document_number_bulk_upload_file_name(file_name)
        except InvalidFileNameException:
            numbers = None

        if numbers:
            first_document_number, second_document_number, _ = numbers
            if first_document_number != 1 or second_document_number != 1:
                logger.info(
                    f"Rejecting file as it is part of a multi-part document: {file_path}"
                )
                raise InvalidFileNameException(
                    "Multi-part documents (e.g. 1of2) are not supported. Only '1of1' is allowed."
                )

        nhs_number, remaining_path = extract_nhs_number_from_bulk_upload_file_name(
            directory_path
        )

        patient_name, remaining_path = extract_patient_name_from_bulk_upload_file_name(
            remaining_path
        )

        date_of_birth_from_path, _ = extract_date_from_bulk_upload_file_name(
            remaining_path
        )

        new_filename = assemble_lg_valid_file_name_full_path(
            file_path_prefix=directory_path + "/",
            first_document_number=1,
            second_document_number=1,
            patient_name=patient_name,
            nhs_number=nhs_number,
            date_object=date_of_birth_from_path,
            file_extension=file_extension,
        )

        return new_filename
