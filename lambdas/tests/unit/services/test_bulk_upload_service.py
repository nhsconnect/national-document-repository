import copy
from unittest.mock import call

import pytest
from botocore.exceptions import ClientError
from enums.virus_scan_result import SCAN_RESULT_TAG_KEY, VirusScanResult
from freezegun import freeze_time

from models.pds_models import Patient
from services.bulk_upload_service import BulkUploadService
from tests.unit.conftest import (
    MOCK_BULK_REPORT_TABLE_NAME,
    MOCK_LG_BUCKET,
    MOCK_LG_METADATA_SQS_QUEUE,
    MOCK_LG_STAGING_STORE_BUCKET,
    MOCK_LG_TABLE_NAME,
    TEST_OBJECT_KEY,
)
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_DOCUMENT_REFERENCE,
    TEST_DOCUMENT_REFERENCE_LIST,
    TEST_FILE_METADATA,
    TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    TEST_SQS_MESSAGE,
    TEST_SQS_MESSAGE_WITH_INVALID_FILENAME,
    TEST_STAGING_METADATA,
    TEST_STAGING_METADATA_WITH_INVALID_FILENAME,
    build_test_sqs_message,
    build_test_staging_metadata_from_patient_name,
    make_s3_file_paths,
    make_valid_lg_file_names,
)
from tests.unit.utils.test_unicode_utils import (
    NAME_WITH_ACCENT_NFC_FORM,
    NAME_WITH_ACCENT_NFD_FORM,
)
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT
from utils.exceptions import (
    DocumentInfectedException,
    InvalidMessageException,
    PatientRecordAlreadyExistException,
    S3FileNotFoundException,
    TagNotFoundException,
    VirusScanFailedException,
    VirusScanNoResultException,
)
from utils.lloyd_george_validator import LGInvalidFilesException


@pytest.fixture
def mock_uuid(mocker):
    test_uuid = TEST_OBJECT_KEY
    mocker.patch("uuid.uuid4", return_value=test_uuid)
    yield test_uuid


@pytest.fixture
def mock_check_virus_result(mocker):
    yield mocker.patch.object(BulkUploadService, "check_virus_result")


@pytest.fixture
def mock_validate_files(mocker):
    yield mocker.patch("services.bulk_upload_service.validate_lg_file_names")


@pytest.fixture
def mock_pds_service(mocker):
    patient = Patient.model_validate(PDS_PATIENT)
    patient_details = patient.get_minimum_patient_details("9000000009")
    mocker.patch(
        "services.bulk_upload_service.getting_patient_info_from_pds",
        return_value=patient_details,
    )
    yield patient_details


@pytest.fixture
def mock_pds_validation(mocker):
    yield mocker.patch("services.bulk_upload_service.validate_with_pds_service")


def build_resolved_file_names_cache(
    file_path_in_metadata: list[str], file_path_in_s3: list[str]
) -> dict:
    return dict(zip(file_path_in_metadata, file_path_in_s3))


def test_handle_sqs_message_happy_path(
    set_env,
    mocker,
    mock_uuid,
    mock_check_virus_result,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation,
):
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_report_upload_complete = mocker.patch.object(
        BulkUploadService, "report_upload_complete"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        BulkUploadService, "remove_ingested_file_from_source_bucket"
    )

    mock_validate_files.return_value = None
    mock_check_virus_result.return_value = None

    service = BulkUploadService()
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_called_with(TEST_STAGING_METADATA)
    mock_report_upload_complete.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()


def set_up_mocks_for_non_ascii_files(
    service: BulkUploadService, mocker, patient_name_on_s3: str
):
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()

    expected_s3_file_paths = make_s3_file_paths(
        make_valid_lg_file_names(total_number=3, patient_name=patient_name_on_s3)
    )

    def mock_file_exist_on_s3(s3_bucket_name: str, file_key: str) -> bool:
        return file_key in expected_s3_file_paths

    def mock_get_tag_value(s3_bucket_name: str, file_key: str, tag_key: str) -> str:
        if (
            s3_bucket_name == MOCK_LG_STAGING_STORE_BUCKET
            and tag_key == SCAN_RESULT_TAG_KEY
            and file_key in expected_s3_file_paths
        ):
            return VirusScanResult.CLEAN

        raise RuntimeError(
            "Unexpected S3 tag calls during non-ascii file name test case."
        )

    def mock_copy_across_bucket(
        source_bucket: str, source_file_key: str, dest_bucket: str, **_kwargs
    ):
        if (
            source_bucket == MOCK_LG_STAGING_STORE_BUCKET
            and dest_bucket == MOCK_LG_BUCKET
            and source_file_key in expected_s3_file_paths
        ):
            return

        raise RuntimeError("Unexpected S3 calls during non-ascii file name test case.")

    service.s3_service.get_tag_value.side_effect = mock_get_tag_value
    service.s3_service.copy_across_bucket.side_effect = mock_copy_across_bucket
    service.s3_service.file_exist_on_s3.side_effect = mock_file_exist_on_s3


@pytest.mark.parametrize(
    ["patient_name_in_metadata_file", "patient_name_on_s3"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITH_ACCENT_NFC_FORM),
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITH_ACCENT_NFD_FORM),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITH_ACCENT_NFC_FORM),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITH_ACCENT_NFD_FORM),
    ],
    ids=["NFC --> NFC", "NFC --> NFD", "NFD --> NFC", "NFD --> NFD"],
)
def test_handle_sqs_message_happy_path_with_non_ascii_filenames(
    set_env,
    mocker,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation,
    patient_name_on_s3,
    patient_name_in_metadata_file,
):
    mock_report_upload_complete = mocker.patch.object(
        BulkUploadService, "report_upload_complete"
    )
    mock_validate_files.return_value = None

    service = BulkUploadService()
    set_up_mocks_for_non_ascii_files(service, mocker, patient_name_on_s3)
    test_staging_metadata = build_test_staging_metadata_from_patient_name(
        patient_name_in_metadata_file
    )
    test_sqs_message = build_test_sqs_message(test_staging_metadata)

    service.handle_sqs_message(message=test_sqs_message)

    mock_report_upload_complete.assert_called()
    assert service.s3_service.get_tag_value.call_count == 3
    assert service.s3_service.copy_across_bucket.call_count == 3


def test_handle_sqs_message_calls_report_upload_failure_when_patient_record_already_in_repo(
    set_env, mocker, mock_uuid, mock_validate_files, mock_pds_validation
):
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        BulkUploadService, "remove_ingested_file_from_source_bucket"
    )
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )

    mocked_error = PatientRecordAlreadyExistException(
        "Lloyd George already exists for patient, upload cancelled."
    )
    mock_validate_files.side_effect = mocked_error

    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()

    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA, str(mocked_error), ""
    )


def test_handle_sqs_message_calls_report_upload_failure_when_lg_file_name_invalid(
    set_env, mocker, mock_uuid, mock_validate_files, mock_pds_validation
):
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        BulkUploadService, "remove_ingested_file_from_source_bucket"
    )
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )
    mocked_error = LGInvalidFilesException(
        "One or more of the files do not match naming convention"
    )
    mock_validate_files.side_effect = mocked_error

    service = BulkUploadService()
    service.handle_sqs_message(message=TEST_SQS_MESSAGE_WITH_INVALID_FILENAME)

    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA_WITH_INVALID_FILENAME, str(mocked_error), ""
    )


def test_handle_sqs_message_report_failure_when_document_is_infected(
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service,
    mock_pds_validation,
):
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        BulkUploadService, "remove_ingested_file_from_source_bucket"
    )
    mock_check_virus_result.side_effect = DocumentInfectedException

    service = BulkUploadService()
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA,
        "One or more of the files failed virus scanner check",
        mock_pds_service.general_practice_ods,
    )
    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()


def test_handle_sqs_message_report_failure_when_document_not_exist(
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service,
    mock_pds_validation,
):
    mock_check_virus_result.side_effect = S3FileNotFoundException
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )

    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA,
        "One or more of the files is not accessible from staging bucket",
        mock_pds_service.general_practice_ods,
    )


def test_handle_sqs_message_put_staging_metadata_back_to_queue_when_virus_scan_result_not_available(
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service,
    mock_pds_validation,
):
    mock_check_virus_result.side_effect = VirusScanNoResultException
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        BulkUploadService, "remove_ingested_file_from_source_bucket"
    )
    mock_put_staging_metadata_back_to_queue = mocker.patch.object(
        BulkUploadService, "put_staging_metadata_back_to_queue"
    )

    service = BulkUploadService()
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_put_staging_metadata_back_to_queue.assert_called_with(
        TEST_STAGING_METADATA, mock_pds_service.general_practice_ods
    )

    mock_report_upload_failure.assert_not_called()
    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()


def test_handle_sqs_message_rollback_transaction_when_validation_pass_but_file_transfer_failed_halfway(
    set_env,
    mocker,
    mock_uuid,
    mock_check_virus_result,
    mock_pds_service,
    mock_validate_files,
    mock_pds_validation,
):
    mock_rollback_transaction = mocker.patch.object(
        BulkUploadService, "rollback_transaction"
    )
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        BulkUploadService, "remove_ingested_file_from_source_bucket"
    )
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()

    mock_client_error = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "GetObject",
    )

    # simulate a client error occur when copying the 3rd file
    service.s3_service.copy_across_bucket.side_effect = [None, None, mock_client_error]

    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_rollback_transaction.assert_called()
    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA,
        "Validation passed but error occurred during file transfer",
        mock_pds_service.general_practice_ods,
    )
    mock_remove_ingested_file_from_source_bucket.assert_not_called()


def test_handle_sqs_message_raise_InvalidMessageException_when_failed_to_extract_data_from_message(
    set_env, mocker
):
    invalid_message = {"body": "invalid content"}
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )

    service = BulkUploadService()
    with pytest.raises(InvalidMessageException):
        service.handle_sqs_message(invalid_message)

    mock_create_lg_records_and_copy_files.assert_not_called()


def test_validate_files_propagate_PatientRecordAlreadyExistException_when_patient_record_already_in_repo(
    set_env, mocker, mock_validate_files
):
    mock_validate_files.side_effect = PatientRecordAlreadyExistException("test text")
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA, "test text", ""
    )


def test_validate_files_raise_LGInvalidFilesException_when_file_names_invalid(
    set_env, mocker, mock_validate_files
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()
    mock_validate_files.side_effect = LGInvalidFilesException("test text")
    mock_report_upload_failure = mocker.patch.object(
        BulkUploadService, "report_upload_failure"
    )
    service.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA, "test text", ""
    )


def test_check_virus_result_raise_no_error_when_all_files_are_clean(
    set_env, mocker, caplog
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.s3_service.get_tag_value.return_value = VirusScanResult.CLEAN
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    service.check_virus_result(TEST_STAGING_METADATA)

    expected_log = f"Verified that all documents for patient {TEST_STAGING_METADATA.nhs_number} are clean."
    actual_log = caplog.records[-1].msg
    assert actual_log == expected_log


def test_check_virus_result_raise_VirusScanNoResultException_when_one_file_not_scanned(
    set_env, mocker
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    service.s3_service.get_tag_value.side_effect = [
        VirusScanResult.CLEAN,
        VirusScanResult.CLEAN,
        TagNotFoundException,  # the 3rd file is not scanned yet
    ]

    with pytest.raises(VirusScanNoResultException):
        service.check_virus_result(TEST_STAGING_METADATA)


def test_check_virus_result_raise_DocumentInfectedException_when_one_file_was_infected(
    set_env, mocker
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    service.s3_service.get_tag_value.side_effect = [
        VirusScanResult.CLEAN,
        VirusScanResult.INFECTED,
        VirusScanResult.CLEAN,
    ]

    with pytest.raises(DocumentInfectedException):
        service.check_virus_result(TEST_STAGING_METADATA)


def test_check_virus_result_raise_S3FileNotFoundException_when_one_file_not_exist_in_bucket(
    set_env, mocker
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    mock_s3_exception = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "GetObjectTagging",
    )

    service.s3_service.get_tag_value.side_effect = [
        VirusScanResult.CLEAN,
        VirusScanResult.CLEAN,
        mock_s3_exception,
    ]

    with pytest.raises(S3FileNotFoundException):
        service.check_virus_result(TEST_STAGING_METADATA)


def test_check_virus_result_raise_VirusScanFailedException_for_special_cases(
    set_env, mocker
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    cases_to_test_for = [
        VirusScanResult.UNSCANNABLE,
        VirusScanResult.ERROR,
        VirusScanResult.INFECTED_ALLOWED,
        "some_other_unexpected_value",
    ]

    for tag_value in cases_to_test_for:
        service.s3_service.get_tag_value.return_value = tag_value
        with pytest.raises(VirusScanFailedException):
            service.check_virus_result(TEST_STAGING_METADATA)


def test_put_staging_metadata_back_to_queue_and_increases_retries(set_env, mocker):
    service = BulkUploadService()
    service.sqs_service = mocker.MagicMock()
    mocker.patch("uuid.uuid4", return_value="123412342")

    TEST_STAGING_METADATA.retries = 2
    metadata_copy = copy.deepcopy(TEST_STAGING_METADATA)
    metadata_copy.retries = 3

    service.put_staging_metadata_back_to_queue(TEST_STAGING_METADATA, "")

    service.sqs_service.send_message_with_nhs_number_attr_fifo.assert_called_with(
        group_id="back_to_queue_bulk_upload_123412342",
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=metadata_copy.model_dump_json(by_alias=True),
        nhs_number=TEST_STAGING_METADATA.nhs_number,
    )


@freeze_time("2023-10-2 13:00:00")
def test_reports_failure_when_max_retries_reached(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.sqs_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()

    mock_failure_reason = (
        "File was not scanned for viruses before maximum retries attempted"
    )
    TEST_STAGING_METADATA.retries = 15

    mocker.patch("uuid.uuid4", return_value="123412342")

    service.put_staging_metadata_back_to_queue(TEST_STAGING_METADATA, "test_ods")

    service.sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()

    for file in TEST_STAGING_METADATA.files:
        expected_dynamo_db_record = {
            "Date": "2023-10-02",
            "FilePath": file.file_path,
            "ID": "123412342",
            "NhsNumber": TEST_STAGING_METADATA.nhs_number,
            "Timestamp": 1696251600,
            "UploadStatus": "failed",
            "FailureReason": mock_failure_reason,
            "OdsCode": "test_ods",
        }
        service.dynamo_service.create_item.assert_any_call(
            item=expected_dynamo_db_record, table_name=MOCK_BULK_REPORT_TABLE_NAME
        )


def test_resolve_source_file_path_when_filenames_dont_have_accented_chars(set_env):
    service = BulkUploadService()
    expected = {
        file.file_path: file.file_path.lstrip("/")
        for file in TEST_STAGING_METADATA.files
    }

    service.resolve_source_file_path(TEST_STAGING_METADATA)
    actual = service.file_path_cache

    assert actual == expected


@pytest.mark.parametrize(
    ["patient_name_in_metadata_file", "patient_name_on_s3"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITH_ACCENT_NFC_FORM),
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITH_ACCENT_NFD_FORM),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITH_ACCENT_NFC_FORM),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITH_ACCENT_NFD_FORM),
    ],
    ids=["NFC --> NFC", "NFC --> NFD", "NFD --> NFC", "NFD --> NFD"],
)
def test_resolve_source_file_path_when_filenames_have_accented_chars(
    set_env, mocker, patient_name_on_s3, patient_name_in_metadata_file
):
    service = BulkUploadService()

    expected_cache = {}
    for i in range(1, 4):
        file_path_in_metadata = (
            f"/9000000009/{i}of3_Lloyd_George_Record_"
            f"[{patient_name_in_metadata_file}]_[9000000009]_[22-10-2010].pdf"
        )
        file_path_on_s3 = f"9000000009/{i}of3_Lloyd_George_Record_[{patient_name_on_s3}]_[9000000009]_[22-10-2010].pdf"
        expected_cache[file_path_in_metadata] = file_path_on_s3

    set_up_mocks_for_non_ascii_files(service, mocker, patient_name_on_s3)
    test_staging_metadata = build_test_staging_metadata_from_patient_name(
        patient_name_in_metadata_file
    )
    service.resolve_source_file_path(test_staging_metadata)
    actual = service.file_path_cache

    assert actual == expected_cache


def test_resolve_source_file_path_raise_S3FileNotFoundException_if_filename_cant_match(
    set_env, mocker
):
    service = BulkUploadService()
    patient_name_on_s3 = "Some Name That Not Matching Metadata File"
    patient_name_in_metadata_file = NAME_WITH_ACCENT_NFC_FORM

    set_up_mocks_for_non_ascii_files(service, mocker, patient_name_on_s3)
    test_staging_metadata = build_test_staging_metadata_from_patient_name(
        patient_name_in_metadata_file
    )

    with pytest.raises(S3FileNotFoundException):
        service.resolve_source_file_path(test_staging_metadata)


def test_put_sqs_message_back_to_queue(set_env, mocker):
    service = BulkUploadService()
    service.sqs_service = mocker.MagicMock()

    service.put_sqs_message_back_to_queue(TEST_SQS_MESSAGE)

    service.sqs_service.send_message_with_nhs_number_attr_fifo.assert_called_with(
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=TEST_SQS_MESSAGE["body"],
        nhs_number=TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    )


def test_create_lg_records_and_copy_files(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()
    service.convert_to_document_reference = mocker.MagicMock(
        return_value=TEST_DOCUMENT_REFERENCE
    )
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    service.create_lg_records_and_copy_files(TEST_STAGING_METADATA)

    nhs_number = TEST_STAGING_METADATA.nhs_number

    for file in TEST_STAGING_METADATA.files:
        expected_source_file_key = BulkUploadService.strip_leading_slash(file.file_path)
        expected_dest_file_key = f"{nhs_number}/{mock_uuid}"
        service.s3_service.copy_across_bucket.assert_any_call(
            source_bucket=MOCK_LG_STAGING_STORE_BUCKET,
            source_file_key=expected_source_file_key,
            dest_bucket=MOCK_LG_BUCKET,
            dest_file_key=expected_dest_file_key,
        )
    assert service.s3_service.copy_across_bucket.call_count == 3

    service.dynamo_service.create_item.assert_any_call(
        table_name=MOCK_LG_TABLE_NAME, item=TEST_DOCUMENT_REFERENCE.to_dict()
    )
    assert service.dynamo_service.create_item.call_count == 3


def test_create_lg_records_and_copy_files_keep_track_of_successfully_ingested_files(
    set_env, mocker, mock_uuid
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()
    service.convert_to_document_reference = mocker.MagicMock(
        return_value=TEST_DOCUMENT_REFERENCE
    )
    service.resolve_source_file_path(TEST_STAGING_METADATA)
    expected = [
        service.strip_leading_slash(file.file_path)
        for file in TEST_STAGING_METADATA.files
    ]

    service.create_lg_records_and_copy_files(TEST_STAGING_METADATA)

    actual = service.source_bucket_files_in_transaction

    assert actual == expected


def test_convert_to_document_reference(set_env, mock_uuid):
    service = BulkUploadService()

    expected = TEST_DOCUMENT_REFERENCE
    actual = service.convert_to_document_reference(
        file_metadata=TEST_FILE_METADATA, nhs_number=TEST_STAGING_METADATA.nhs_number
    )

    # exclude the `created` timestamp from comparison
    actual.created = "mock_timestamp"
    expected.created = "mock_timestamp"

    assert actual == expected


def test_remove_ingested_file_from_source_bucket(set_env, mocker):
    service = BulkUploadService()

    service.s3_service = mocker.MagicMock()
    mock_source_file_keys = [
        "9000000009/1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "9000000009/2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    service.source_bucket_files_in_transaction = mock_source_file_keys

    expected_deletion_calls = [
        call(s3_bucket_name=MOCK_LG_STAGING_STORE_BUCKET, file_key=file_key)
        for file_key in mock_source_file_keys
    ]

    service.remove_ingested_file_from_source_bucket()

    service.s3_service.delete_object.assert_has_calls(expected_deletion_calls)


def test_rollback_transaction(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_service = mocker.MagicMock()

    service.dynamo_records_in_transaction = TEST_DOCUMENT_REFERENCE_LIST
    service.dest_bucket_files_in_transaction = [
        f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_1",
        f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_2",
    ]

    service.rollback_transaction()

    service.dynamo_service.delete_item.assert_called_with(
        table_name=MOCK_LG_TABLE_NAME, key={"ID": mock_uuid}
    )
    assert service.dynamo_service.delete_item.call_count == len(
        TEST_DOCUMENT_REFERENCE_LIST
    )

    service.s3_service.delete_object.assert_any_call(
        s3_bucket_name=MOCK_LG_BUCKET,
        file_key=f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_1",
    )
    service.s3_service.delete_object.assert_any_call(
        s3_bucket_name=MOCK_LG_BUCKET,
        file_key=f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_2",
    )
    assert service.s3_service.delete_object.call_count == 2


@freeze_time("2023-10-1 13:00:00")
def test_report_upload_complete_add_record_to_dynamodb(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.dynamo_service = mocker.MagicMock()

    service.report_upload_complete(TEST_STAGING_METADATA, "")

    assert service.dynamo_service.create_item.call_count == len(
        TEST_STAGING_METADATA.files
    )

    for file in TEST_STAGING_METADATA.files:
        expected_dynamo_db_record = {
            "Date": "2023-10-01",
            "FilePath": file.file_path,
            "ID": mock_uuid,
            "NhsNumber": TEST_STAGING_METADATA.nhs_number,
            "Timestamp": 1696165200,
            "UploadStatus": "complete",
            "OdsCode": "",
        }
        service.dynamo_service.create_item.assert_any_call(
            item=expected_dynamo_db_record, table_name=MOCK_BULK_REPORT_TABLE_NAME
        )


@freeze_time("2023-10-2 13:00:00")
def test_report_upload_failure_add_record_to_dynamodb(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.dynamo_service = mocker.MagicMock()

    mock_failure_reason = "File name invalid"
    service.report_upload_failure(
        TEST_STAGING_METADATA, failure_reason=mock_failure_reason
    )

    for file in TEST_STAGING_METADATA.files:
        expected_dynamo_db_record = {
            "Date": "2023-10-02",
            "FilePath": file.file_path,
            "ID": mock_uuid,
            "NhsNumber": TEST_STAGING_METADATA.nhs_number,
            "Timestamp": 1696251600,
            "UploadStatus": "failed",
            "FailureReason": mock_failure_reason,
            "OdsCode": "",
        }
        service.dynamo_service.create_item.assert_any_call(
            item=expected_dynamo_db_record, table_name=MOCK_BULK_REPORT_TABLE_NAME
        )
