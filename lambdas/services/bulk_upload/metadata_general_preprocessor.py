from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidFileNameException
from utils.filename_utils import assemble_lg_valid_file_name_full_path, extract_nhs_number_from_bulk_upload_file_name, \
    extract_patient_name_from_bulk_upload_file_name, extract_date_from_bulk_upload_file_name, \
    extract_file_extension_from_bulk_upload_file_name, extract_document_path_for_lloyd_george_record, \
    extract_document_number_bulk_upload_file_name, extract_lloyd_george_record_from_bulk_upload_file_name

logger = LoggingService(__name__)


class MetadataGeneralPreprocessor:
    def validate_record_filename(self, file_name) -> str:
        try:
            logger.info(f"Processing file name {file_name}")

            file_path_prefix, current_file_name = extract_document_path_for_lloyd_george_record(file_name)
            first_document_number, second_document_number, current_file_name = (
                extract_document_number_bulk_upload_file_name(current_file_name)
            )
            current_file_name = (
                extract_lloyd_george_record_from_bulk_upload_file_name(
                    current_file_name
                )
            )
            patient_name, current_file_name = (
                extract_patient_name_from_bulk_upload_file_name(current_file_name)
            )

            if sum(c.isdigit() for c in current_file_name) != 18:
                logger.info("Failed to find NHS number or date")
                raise InvalidFileNameException("Incorrect NHS number or date format")

            nhs_number, current_file_name = (
                extract_nhs_number_from_bulk_upload_file_name(current_file_name)
            )
            date, current_file_name = (
                extract_date_from_bulk_upload_file_name(current_file_name)
            )
            file_extension = extract_file_extension_from_bulk_upload_file_name(
                current_file_name
            )
            file_name = assemble_lg_valid_file_name_full_path(
                file_path_prefix,
                first_document_number,
                second_document_number,
                patient_name,
                nhs_number,
                date,
                file_extension,
            )
            logger.info(f"Finished processing, new file name is: {file_name}")
            return file_name

        except InvalidFileNameException as error:
            logger.error(f"Failed to process {file_name} due to error: {error}")
            raise error

