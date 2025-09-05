import os

from utils.filename_utils import assemble_lg_valid_file_name_full_path, extract_document_path, \
    extract_nhs_number_from_bulk_upload_file_name, extract_patient_name_from_bulk_upload_file_name, \
    extract_date_from_bulk_upload_file_name


class MetadataUsbPreprocessorService:
    def validate_record_filename(self, file_path: str) -> str:

        directory_path, file_name = extract_document_path(file_path)

        nhs_number, remaining_path = extract_nhs_number_from_bulk_upload_file_name(directory_path)

        patient_name, remaining_path = extract_patient_name_from_bulk_upload_file_name(remaining_path)

        date_of_birth_from_path, _ = extract_date_from_bulk_upload_file_name(remaining_path)

        file_extension = os.path.splitext(file_name)[1]

        new_filename = assemble_lg_valid_file_name_full_path(
            file_path_prefix=directory_path + '/',
            first_document_number=1,
            second_document_number=1,
            patient_name=patient_name,
            nhs_number=nhs_number,
            date_object=date_of_birth_from_path,
            file_extension=file_extension
        )

        return new_filename