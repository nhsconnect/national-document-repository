import json
import os
from copy import copy

import pytest
import services.bulk_upload_service_v2 as bulk_upload_module
from botocore.exceptions import ClientError
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from enums.upload_status import UploadStatus
from enums.virus_scan_result import SCAN_RESULT_TAG_KEY, VirusScanResult
from freezegun import freeze_time
from models.pds_models import Patient
from repositories.bulk_upload.bulk_upload_s3_repository import BulkUploadS3Repository
from repositories.bulk_upload.bulk_upload_sqs_repository import BulkUploadSqsRepository
from services.bulk_upload_service_v2 import BulkUploadService
from tests.unit.conftest import (
    MOCK_LG_BUCKET,
    MOCK_STAGING_STORE_BUCKET,
    TEST_CURRENT_GP_ODS,
)
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_DOCUMENT_REFERENCE,
    TEST_FILE_METADATA,
    TEST_SQS_10_MESSAGES_AS_LIST,
    TEST_SQS_MESSAGE,
    TEST_SQS_MESSAGE_SINGLE_FILE,
    TEST_SQS_MESSAGE_WITH_INVALID_FILENAME,
    TEST_SQS_MESSAGES_AS_LIST,
    TEST_STAGING_METADATA,
    TEST_STAGING_METADATA_SINGLE_FILE,
    TEST_STAGING_METADATA_WITH_INVALID_FILENAME,
    build_test_sqs_message,
    build_test_staging_metadata_from_patient_name,
    make_s3_file_paths,
    make_valid_lg_file_names,
)
from tests.unit.helpers.data.pds.pds_patient_response import (
    PDS_PATIENT,
    PDS_PATIENT_DECEASED_FORMAL,
    PDS_PATIENT_DECEASED_INFORMAL,
    PDS_PATIENT_RESTRICTED,
)
from tests.unit.utils.test_unicode_utils import (
    NAME_WITH_ACCENT_NFC_FORM,
    NAME_WITH_ACCENT_NFD_FORM,
)
from utils.exceptions import (
    BulkUploadException,
    DocumentInfectedException,
    InvalidMessageException,
    InvalidNhsNumberException,
    PatientRecordAlreadyExistException,
    PdsErrorException,
    PdsTooManyRequestsException,
    S3FileNotFoundException,
    VirusScanFailedException,
    VirusScanNoResultException,
)
from utils.lloyd_george_validator import LGInvalidFilesException

from lambdas.models.staging_metadata import MetadataFile, StagingMetadata


@pytest.fixture
def repo_under_test(set_env, mocker):
    service = BulkUploadService(strict_mode=True)
    mocker.patch.object(service, "dynamo_repository")
    mocker.patch.object(service, "sqs_repository")
    mocker.patch.object(service, "bulk_upload_s3_repository")
    yield service


@pytest.fixture
def mock_check_virus_result(mocker):
    yield mocker.patch.object(BulkUploadS3Repository, "check_virus_result")


@pytest.fixture
def mock_validate_files(mocker):
    return mocker.patch.object(bulk_upload_module, "validate_lg_file_names")


@pytest.fixture
def mock_pds_service(mocker):
    patient = Patient.model_validate(PDS_PATIENT)
    mocker.patch.object(
        bulk_upload_module,
        "getting_patient_info_from_pds",
        return_value=patient,
    )
    yield patient


@pytest.fixture
def mock_pds_service_patient_deceased_formal(mocker):
    patient = Patient.model_validate(PDS_PATIENT_DECEASED_FORMAL)
    mocker.patch.object(
        bulk_upload_module,
        "getting_patient_info_from_pds",
        return_value=patient,
    )
    yield patient


@pytest.fixture
def mock_pds_service_patient_deceased_informal(mocker):
    patient = Patient.model_validate(PDS_PATIENT_DECEASED_INFORMAL)
    mocker.patch.object(
        bulk_upload_module,
        "getting_patient_info_from_pds",
        return_value=patient,
    )
    yield patient


@pytest.fixture
def mock_pds_service_patient_restricted(mocker):
    patient = Patient.model_validate(PDS_PATIENT_RESTRICTED)
    mocker.patch.object(
        bulk_upload_module,
        "getting_patient_info_from_pds",
        return_value=patient,
    )
    return patient


@pytest.fixture
def mock_pds_validation_lenient(mocker):
    return mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_lenient",
        return_value=("test string", True),
    )


@pytest.fixture
def mock_pds_validation_strict(mocker):
    return mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_strict",
    )


@pytest.fixture
def mock_ods_validation(mocker):
    return mocker.patch.object(bulk_upload_module, "allowed_to_ingest_ods_code")


@pytest.fixture
def mock_ods_validation_true(mocker):
    patcher = mocker.patch.object(
        bulk_upload_module,
        "allowed_to_ingest_ods_code",
        return_value=True,
    )
    yield patcher


@pytest.fixture
def mock_handle_sqs_message(mocker):
    yield mocker.patch.object(BulkUploadService, "handle_sqs_message")


@pytest.fixture
def mock_back_to_queue(mocker):
    yield mocker.patch.object(BulkUploadSqsRepository, "put_sqs_message_back_to_queue")


def build_resolved_file_names_cache(
    file_path_in_metadata: list[str], file_path_in_s3: list[str]
) -> dict:
    return dict(zip(file_path_in_metadata, file_path_in_s3))


def test_process_message_queue_happy_path(mocker, repo_under_test):
    message1 = {"body": json.dumps({"NHS-NO": "1234567890"})}
    message2 = {"body": json.dumps({"NHS-NO": "9876543210"})}
    records = [message1, message2]

    mock_handle = mocker.patch.object(repo_under_test, "handle_sqs_message")
    mock_log_summary = mocker.patch.object(repo_under_test, "log_processing_summary")

    repo_under_test.process_message_queue(records)

    assert mock_handle.call_count == 2
    mock_handle.assert_any_call(message1)
    mock_handle.assert_any_call(message2)

    mock_log_summary.assert_called_once_with(records)


@pytest.mark.parametrize(
    "exception_instance",
    [
        ClientError(
            {"Error": {"Code": "500", "Message": "An error occurred"}}, "TestOperation"
        ),
        InvalidMessageException("Error occurred"),
        LGInvalidFilesException("Error occurred"),
        Exception("Error occurred"),
    ],
)
def test_process_message_queue_general_error(
    mocker, repo_under_test, exception_instance
):
    message = {"body": json.dumps({"NHS-NO": "1234567890"})}
    records = [message]

    mock_handle = mocker.patch.object(
        repo_under_test, "handle_sqs_message", side_effect=exception_instance
    )
    mock_general_error = mocker.patch.object(
        repo_under_test, "handle_process_message_general_error"
    )
    mock_log_summary = mocker.patch.object(repo_under_test, "log_processing_summary")

    repo_under_test.process_message_queue(records)

    mock_handle.assert_called_once_with(message)
    mock_general_error.assert_called_once_with(message, exception_instance)
    mock_log_summary.assert_called_once_with(records)


@pytest.mark.parametrize(
    "pds_exception_instance",
    [
        PdsTooManyRequestsException("Rate limit reached"),
        PdsErrorException("PDS error occurred"),
    ],
)
def test_process_message_queue_pds_error(
    mocker, repo_under_test, pds_exception_instance
):
    message1 = {"body": json.dumps({"NHS-NO": "1234567890"})}
    message2 = {"body": json.dumps({"NHS-NO": "9876543210"})}
    records = [message1, message2]

    mock_handle = mocker.patch.object(
        repo_under_test, "handle_sqs_message", side_effect=pds_exception_instance
    )
    mock_pds_error = mocker.patch.object(
        repo_under_test, "handle_process_message_pds_error"
    )
    mock_log_summary = mocker.patch.object(repo_under_test, "log_processing_summary")

    with pytest.raises(
        BulkUploadException,
        match="Bulk upload process paused due to PDS rate limit reached",
    ):
        repo_under_test.process_message_queue(records)

    mock_handle.assert_called_once_with(message1)
    mock_pds_error.assert_called_once_with(records, 1, pds_exception_instance)
    mock_log_summary.assert_not_called()


def test_handle_process_message_pds_error_calls_put_sqs_message_back_to_queue_correctly(
    mocker, repo_under_test
):
    msg1 = {"body": "msg1"}
    msg2 = {"body": "msg2"}
    msg3 = {"body": "msg3"}
    records = [msg1, msg2, msg3]

    current_index = 2

    mock_put = mocker.patch.object(
        repo_under_test.sqs_repository, "put_sqs_message_back_to_queue"
    )

    error = Exception("PDS rate limit error")

    repo_under_test.handle_process_message_pds_error(records, current_index, error)

    assert mock_put.call_count == 2
    mock_put.assert_any_call(msg2)
    mock_put.assert_any_call(msg3)


def test_handle_process_message_general_error_adds_message_to_unhandled(
    mocker, repo_under_test
):
    message = {"body": "test message"}
    error = Exception("some error")

    assert repo_under_test.unhandled_messages == []

    repo_under_test.handle_process_message_general_error(message, error)

    assert message in repo_under_test.unhandled_messages


def test_log_processing_summary_without_unhandled_messages(mocker, repo_under_test):
    message1 = {"body": json.dumps({"NHS-NO": "1234567890"})}
    records = [message1]

    repo_under_test.unhandled_messages = []

    mock_logger_info = mocker.patch.object(bulk_upload_module.logger, "info")

    repo_under_test.log_processing_summary(records)

    mock_logger_info.assert_any_call(
        f"Finished processing {len(records)} of {len(records)} messages"
    )
    assert not any(
        "Unable to process the following messages:" in str(call.args[0])
        for call in mock_logger_info.mock_calls
    )


def test_log_processing_summary_with_unhandled_messages(mocker, repo_under_test):
    message1 = {"body": json.dumps({"NHS-NO": "1234567890"})}
    message2 = {"body": json.dumps({"NHS-NO": "0987654321"})}
    records = [message1, message2]

    repo_under_test.unhandled_messages = [message1, message2]

    mock_logger_info = mocker.patch.object(bulk_upload_module.logger, "info")
    mock_request_context = mocker.patch.object(
        bulk_upload_module, "request_context", create=True
    )

    repo_under_test.log_processing_summary(records)

    mock_logger_info.assert_any_call(
        f"Finished processing 0 of {len(records)} messages"
    )
    mock_logger_info.assert_any_call("Unable to process the following messages:")
    mock_logger_info.assert_any_call(json.loads(message1["body"]))
    mock_logger_info.assert_any_call(json.loads(message2["body"]))

    assert mock_request_context.patient_nhs_no == "0987654321"


def test_lambda_handler_process_each_sqs_message_one_by_one(
    set_env, mock_handle_sqs_message
):
    service = BulkUploadService(True)

    service.process_message_queue(TEST_SQS_MESSAGES_AS_LIST)

    assert mock_handle_sqs_message.call_count == len(TEST_SQS_MESSAGES_AS_LIST)
    for message in TEST_SQS_MESSAGES_AS_LIST:
        mock_handle_sqs_message.assert_any_call(message)


def test_lambda_handler_continue_process_next_message_after_handled_error(
    set_env, mock_handle_sqs_message
):
    # emulate that unexpected error happen at 2nd message
    mock_handle_sqs_message.side_effect = [
        None,
        InvalidMessageException,
        None,
    ]
    service = BulkUploadService(True)
    service.process_message_queue(TEST_SQS_MESSAGES_AS_LIST)

    assert mock_handle_sqs_message.call_count == len(TEST_SQS_MESSAGES_AS_LIST)
    mock_handle_sqs_message.assert_called_with(TEST_SQS_MESSAGES_AS_LIST[2])


def test_lambda_handler_handle_pds_too_many_requests_exception(
    set_env, mock_handle_sqs_message, mock_back_to_queue
):
    # emulate that unexpected error happen at 7th message
    mock_handle_sqs_message.side_effect = (
        [None] * 6 + [PdsTooManyRequestsException] + [None] * 3
    )
    expected_handled_messages = TEST_SQS_10_MESSAGES_AS_LIST[0:6]
    expected_unhandled_message = TEST_SQS_10_MESSAGES_AS_LIST[6:]

    service = BulkUploadService(True)
    with pytest.raises(BulkUploadException):
        service.process_message_queue(TEST_SQS_10_MESSAGES_AS_LIST)

    assert mock_handle_sqs_message.call_count == 7

    for message in expected_handled_messages:
        mock_handle_sqs_message.assert_any_call(message)

    for message in expected_unhandled_message:
        mock_back_to_queue.assert_any_call(message)


def test_handle_sqs_message_happy_path(
    set_env,
    mocker,
    mock_uuid,
    repo_under_test,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0

    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_report_upload_complete = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    mocker.patch.object(repo_under_test.bulk_upload_s3_repository, "check_virus_result")

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)
    mock_create_lg_records_and_copy_files.assert_called_with(
        TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS
    )
    mock_pds_validation_strict.assert_called()
    mock_report_upload_complete.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()
    repo_under_test.sqs_repository.send_message_to_pdf_stitching_queue.assert_called()


def test_handle_sqs_message_happy_path_single_file(
    set_env,
    mocker,
    mock_uuid,
    repo_under_test,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_create_lg_records_and_copy_files.return_value = TEST_DOCUMENT_REFERENCE
    mock_report_upload_complete = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    mocker.patch.object(repo_under_test.bulk_upload_s3_repository, "check_virus_result")

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE_SINGLE_FILE)

    mock_create_lg_records_and_copy_files.assert_called_with(
        TEST_STAGING_METADATA_SINGLE_FILE, TEST_CURRENT_GP_ODS
    )
    mock_report_upload_complete.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()
    repo_under_test.sqs_repository.send_message_to_pdf_stitching_queue.assert_called()


def set_up_mocks_for_non_ascii_files(
    service: BulkUploadService, mocker, patient_name_on_s3: str
):
    service.s3_service = mocker.MagicMock()
    service.dynamo_repository = mocker.MagicMock()

    expected_s3_file_paths = make_s3_file_paths(
        make_valid_lg_file_names(total_number=3, patient_name=patient_name_on_s3)
    )

    def mock_file_exist_on_s3(file_key: str) -> bool:
        return file_key in expected_s3_file_paths

    def mock_get_tag_value(s3_bucket_name: str, file_key: str, tag_key: str) -> str:
        if (
            s3_bucket_name == MOCK_STAGING_STORE_BUCKET
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
            source_bucket == MOCK_STAGING_STORE_BUCKET
            and dest_bucket == MOCK_LG_BUCKET
            and source_file_key in expected_s3_file_paths
        ):
            return

        raise RuntimeError("Unexpected S3 calls during non-ascii file name test case.")

    service.s3_service.get_tag_value.side_effect = mock_get_tag_value
    service.s3_service.copy_across_bucket.side_effect = mock_copy_across_bucket
    service.s3_service.file_exists_on_staging_bucket.side_effect = mock_file_exist_on_s3


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
    repo_under_test,
    set_env,
    mocker,
    mock_validate_files,
    patient_name_on_s3,
    patient_name_in_metadata_file,
    mock_pds_validation_strict,
    mock_pds_service,
    mock_ods_validation,
):
    mock_validate_files.return_value = None
    repo_under_test.bulk_upload_s3_repository.lg_bucket_name = MOCK_LG_BUCKET
    set_up_mocks_for_non_ascii_files(repo_under_test, mocker, patient_name_on_s3)
    test_staging_metadata = build_test_staging_metadata_from_patient_name(
        patient_name_in_metadata_file
    )
    test_sqs_message = build_test_sqs_message(test_staging_metadata)

    repo_under_test.handle_sqs_message(message=test_sqs_message)

    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called()
    assert repo_under_test.bulk_upload_s3_repository.check_virus_result.call_count == 1
    assert repo_under_test.bulk_upload_s3_repository.copy_to_lg_bucket.call_count == 3


def test_handle_sqs_message_calls_report_upload_failure_when_patient_record_already_in_repo(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
):
    TEST_STAGING_METADATA.retries = 0

    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    mock_report_upload_failure = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mocked_error = PatientRecordAlreadyExistException(
        "Lloyd George already exists for patient, upload cancelled."
    )
    mock_validate_files.side_effect = mocked_error

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()
    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA, UploadStatus.FAILED, str(mocked_error), ""
    )
    repo_under_test.sqs_repository.send_message_to_pdf_stitching_queue.assert_not_called()


def test_handle_sqs_message_calls_report_upload_failure_when_lg_file_name_invalid(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
):
    TEST_STAGING_METADATA.retries = 0
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    mock_report_upload_failure = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mocked_error = LGInvalidFilesException(
        "One or more of the files do not match naming convention"
    )
    mock_validate_files.side_effect = mocked_error

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE_WITH_INVALID_FILENAME)

    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()
    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA_WITH_INVALID_FILENAME,
        UploadStatus.FAILED,
        str(mocked_error),
        "",
    )
    repo_under_test.sqs_repository.send_message_to_pdf_stitching_queue.assert_not_called()


def test_handle_sqs_message_report_failure_when_document_is_infected(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0
    mock_report_upload_failure = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    repo_under_test.bulk_upload_s3_repository.check_virus_result.side_effect = (
        DocumentInfectedException
    )

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "One or more of the files failed virus scanner check",
        "Y12345",
    )
    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()
    repo_under_test.sqs_repository.send_message_to_pdf_stitching_queue.assert_not_called()


def test_handle_sqs_message_report_failure_when_document_not_exist(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0
    repo_under_test.bulk_upload_s3_repository.check_virus_result.side_effect = (
        S3FileNotFoundException
    )
    mock_report_upload_failure = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "One or more of the files is not accessible from staging bucket",
        "Y12345",
    )
    repo_under_test.sqs_repository.send_message_to_pdf_stitching_queue.assert_not_called()


def test_handle_sqs_message_calls_report_upload_successful_when_patient_is_formally_deceased(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service_patient_deceased_formal,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = (
        repo_under_test.bulk_upload_s3_repository.remove_ingested_file_from_source_bucket
    )
    mock_pds_validation_strict.return_value = False
    mock_put_staging_metadata_back_to_queue = (
        repo_under_test.sqs_repository.put_staging_metadata_back_to_queue
    )
    mock_report_upload = repo_under_test.dynamo_repository.write_report_upload_to_dynamo

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()
    mock_put_staging_metadata_back_to_queue.assert_not_called()

    mock_report_upload.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.COMPLETE,
        "Patient is deceased - FORMAL",
        PatientOdsInactiveStatus.DECEASED,
    )


def test_handle_sqs_message_calls_report_upload_successful_when_patient_is_informally_deceased_and_historical(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service_patient_deceased_informal,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_pds_validation_strict.return_value = True
    mock_remove_ingested_file_from_source_bucket = (
        repo_under_test.bulk_upload_s3_repository.remove_ingested_file_from_source_bucket
    )
    mock_put_staging_metadata_back_to_queue = (
        repo_under_test.sqs_repository.put_staging_metadata_back_to_queue
    )
    mock_report_upload = repo_under_test.dynamo_repository.write_report_upload_to_dynamo

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()
    mock_put_staging_metadata_back_to_queue.assert_not_called()

    mock_report_upload.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.COMPLETE,
        "Patient matched on historical name, Patient is deceased - INFORMAL",
        "Y12345",
    )


def test_handle_sqs_message_calls_report_upload_successful_when_patient_has_historical_name_and_rest(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service_patient_restricted,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_pds_validation_strict.return_value = True
    mock_remove_ingested_file_from_source_bucket = (
        repo_under_test.bulk_upload_s3_repository.remove_ingested_file_from_source_bucket
    )
    mock_put_staging_metadata_back_to_queue = (
        repo_under_test.sqs_repository.put_staging_metadata_back_to_queue
    )
    mock_report_upload = repo_under_test.dynamo_repository.write_report_upload_to_dynamo

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()
    mock_put_staging_metadata_back_to_queue.assert_not_called()

    mock_report_upload.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.COMPLETE,
        "Patient matched on historical name, PDS record is restricted",
        "REST",
    )


def test_handle_sqs_message_calls_report_upload_successful_when_patient_is_informally_deceased(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service_patient_deceased_informal,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_pds_validation_strict.return_value = False
    mock_remove_ingested_file_from_source_bucket = (
        repo_under_test.bulk_upload_s3_repository.remove_ingested_file_from_source_bucket
    )
    mock_put_staging_metadata_back_to_queue = (
        repo_under_test.sqs_repository.put_staging_metadata_back_to_queue
    )
    mock_report_upload = repo_under_test.dynamo_repository.write_report_upload_to_dynamo

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()
    mock_put_staging_metadata_back_to_queue.assert_not_called()

    mock_report_upload.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.COMPLETE,
        "Patient is deceased - INFORMAL",
        "Y12345",
    )


def test_handle_sqs_message_put_staging_metadata_back_to_queue_when_virus_scan_result_not_available(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_check_virus_result,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0
    repo_under_test.bulk_upload_s3_repository.check_virus_result.side_effect = (
        VirusScanNoResultException
    )
    mock_report_upload_failure = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    mock_put_staging_metadata_back_to_queue = mocker.patch.object(
        repo_under_test.sqs_repository, "put_staging_metadata_back_to_queue"
    )

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_put_staging_metadata_back_to_queue.assert_called_with(TEST_STAGING_METADATA)

    mock_report_upload_failure.assert_not_called()
    mock_create_lg_records_and_copy_files.assert_not_called()
    mock_remove_ingested_file_from_source_bucket.assert_not_called()
    repo_under_test.sqs_repository.send_message_to_pdf_stitching_queue.assert_not_called()


def test_handle_sqs_message_rollback_transaction_when_validation_pass_but_file_transfer_failed_halfway(
    repo_under_test,
    set_env,
    mocker,
    mock_uuid,
    mock_check_virus_result,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    repo_under_test.bulk_upload_s3_repository.lg_bucket_name = MOCK_LG_BUCKET

    TEST_STAGING_METADATA.retries = 0
    mock_rollback_transaction_s3 = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository, "rollback_transaction"
    )
    mock_rollback_transaction_dynamo = mocker.patch.object(
        repo_under_test.dynamo_repository, "rollback_transaction"
    )
    mock_report_upload_failure = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    mock_client_error = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "GetObject",
    )

    # simulate a client error occur when copying the 3rd file
    repo_under_test.bulk_upload_s3_repository.copy_to_lg_bucket.side_effect = [
        None,
        None,
        mock_client_error,
    ]

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_rollback_transaction_dynamo.assert_called()
    mock_rollback_transaction_s3.assert_called()
    mock_report_upload_failure.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "Validation passed but error occurred during file transfer",
        "Y12345",
    )
    mock_remove_ingested_file_from_source_bucket.assert_not_called()
    assert (
        repo_under_test.dynamo_repository.create_record_in_lg_dynamo_table.call_count
        == 2
    )


def test_handle_sqs_message_raise_InvalidMessageException_when_failed_to_extract_data_from_message(
    repo_under_test, set_env, mocker
):
    invalid_message = {"body": "invalid content"}
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )

    with pytest.raises(InvalidMessageException):
        repo_under_test.handle_sqs_message(invalid_message)

    mock_create_lg_records_and_copy_files.assert_not_called()


def test_validate_files_raise_LGInvalidFilesException_when_file_names_invalid(
    repo_under_test, set_env, mock_validate_files
):
    TEST_STAGING_METADATA.retries = 0
    invalid_file_name_metadata_as_json = json.dumps(
        TEST_STAGING_METADATA_WITH_INVALID_FILENAME.model_dump()
    )
    mock_validate_files.side_effect = LGInvalidFilesException

    repo_under_test.handle_sqs_message({"body": invalid_file_name_metadata_as_json})

    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called()


@freeze_time("2023-10-2 13:00:00")
def test_reports_failure_when_max_retries_reached(
    set_env, mocker, mock_uuid, repo_under_test, mock_validate_files
):
    mocker.patch("uuid.uuid4", return_value="123412342")

    TEST_STAGING_METADATA.retries = 15
    metadata_as_json = json.dumps(TEST_STAGING_METADATA.model_dump())
    mock_validate_files.side_effect = LGInvalidFilesException
    repo_under_test.handle_sqs_message({"body": metadata_as_json})

    repo_under_test.sqs_repository.send_message_with_nhs_number_attr_fifo.assert_not_called()
    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called()


def test_resolve_source_file_path_when_filenames_dont_have_accented_chars(
    set_env, repo_under_test
):
    expected = {
        file.file_path: file.file_path.lstrip("/")
        for file in TEST_STAGING_METADATA.files
    }

    repo_under_test.resolve_source_file_path(TEST_STAGING_METADATA)
    actual = repo_under_test.file_path_cache

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
    set_env, mocker, patient_name_on_s3, patient_name_in_metadata_file, repo_under_test
):
    patient_name = "Évèlynêë François Ågāřdñ"
    expected_cache = {}
    for i in range(1, 4):
        file_path_in_metadata = (
            f"/9000000009/{i}of3_Lloyd_George_Record_"
            f"[{patient_name_in_metadata_file}]_[9000000009]_[22-10-2010].pdf"
        )
        file_path_on_s3 = f"9000000009/{i}of3_Lloyd_George_Record_[{patient_name}]_[9000000009]_[22-10-2010].pdf"
        expected_cache[file_path_in_metadata] = file_path_on_s3

    set_up_mocks_for_non_ascii_files(repo_under_test, mocker, patient_name_on_s3)
    test_staging_metadata = build_test_staging_metadata_from_patient_name(
        patient_name_in_metadata_file
    )
    repo_under_test.resolve_source_file_path(test_staging_metadata)
    actual = repo_under_test.file_path_cache

    assert actual == expected_cache


def test_resolves_source_file_path_raise_S3FileNotFoundException_if_filename_cant_match(
    set_env, mocker, repo_under_test
):
    patient_name_on_s3 = "Some Name That Not Matching Metadata File"
    patient_name_in_metadata_file = NAME_WITH_ACCENT_NFC_FORM
    repo_under_test.bulk_upload_s3_repository.file_exists_on_staging_bucket.return_value = (
        False
    )

    set_up_mocks_for_non_ascii_files(repo_under_test, mocker, patient_name_on_s3)
    test_staging_metadata = build_test_staging_metadata_from_patient_name(
        patient_name_in_metadata_file
    )

    with pytest.raises(S3FileNotFoundException):
        repo_under_test.resolve_source_file_path(test_staging_metadata)


def test_create_lg_records_and_copy_files(set_env, mocker, mock_uuid, repo_under_test):
    test_document_reference = copy(TEST_DOCUMENT_REFERENCE)
    repo_under_test.convert_to_document_reference = mocker.MagicMock(
        return_value=test_document_reference
    )
    TEST_STAGING_METADATA.retries = 0
    repo_under_test.resolve_source_file_path(TEST_STAGING_METADATA)

    repo_under_test.create_lg_records_and_copy_files(
        TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS
    )

    nhs_number = TEST_STAGING_METADATA.nhs_number

    for file in TEST_STAGING_METADATA.files:
        expected_source_file_key = BulkUploadService.strip_leading_slash(file.file_path)
        expected_dest_file_key = f"{nhs_number}/{mock_uuid}"
        repo_under_test.bulk_upload_s3_repository.copy_to_lg_bucket.assert_any_call(
            source_file_key=expected_source_file_key,
            dest_file_key=expected_dest_file_key,
        )
        assert test_document_reference.uploaded.__eq__(True)
    assert repo_under_test.bulk_upload_s3_repository.copy_to_lg_bucket.call_count == 3
    repo_under_test.dynamo_repository.create_record_in_lg_dynamo_table.assert_any_call(
        test_document_reference
    )
    assert (
        repo_under_test.dynamo_repository.create_record_in_lg_dynamo_table.call_count
        == 3
    )


@freeze_time("2024-01-01 12:00:00")
def test_convert_to_document_reference(set_env, mock_uuid, repo_under_test):
    TEST_STAGING_METADATA.retries = 0
    repo_under_test.bulk_upload_s3_repository.lg_bucket_name = "test_lg_s3_bucket"
    expected = TEST_DOCUMENT_REFERENCE

    actual = repo_under_test.convert_to_document_reference(
        file_metadata=TEST_FILE_METADATA,
        nhs_number=TEST_STAGING_METADATA.nhs_number,
        current_gp_ods=TEST_CURRENT_GP_ODS,
    )

    assert actual == expected


@freeze_time("2024-01-01 12:00:00")
def test_convert_to_document_reference_missing_scan_date(
    set_env, mock_uuid, repo_under_test
):
    TEST_STAGING_METADATA.retries = 0
    repo_under_test.bulk_upload_s3_repository.lg_bucket_name = "test_lg_s3_bucket"
    expected = TEST_DOCUMENT_REFERENCE
    expected.document_scan_creation = None
    TEST_FILE_METADATA.scan_date = ""

    actual = repo_under_test.convert_to_document_reference(
        file_metadata=TEST_FILE_METADATA,
        nhs_number=TEST_STAGING_METADATA.nhs_number,
        current_gp_ods=TEST_CURRENT_GP_ODS,
    )

    assert actual == expected

    TEST_FILE_METADATA.scan_date = "03/09/2022"
    TEST_DOCUMENT_REFERENCE.document_scan_creation = "2022-09-03"


def test_raise_client_error_from_ssm_with_pds_service(
    mock_ods_validation,
    repo_under_test,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
):
    mock_client_error = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )
    mock_ods_validation.side_effect = mock_client_error
    with pytest.raises(ClientError):
        repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)


def test_mismatch_ods_with_pds_service(
    repo_under_test,
    mock_ods_validation,
    set_env,
    mock_uuid,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
):
    mock_ods_validation.return_value = False

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "Patient not registered at your practice",
        "Y12345",
    )


def test_create_lg_records_and_copy_files_client_error(
    repo_under_test,
    mocker,
    set_env,
    mock_uuid,
    mock_check_virus_result,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        repo_under_test, "create_lg_records_and_copy_files"
    )
    mock_rollback_transaction = mocker.patch.object(
        repo_under_test, "rollback_transaction"
    )
    mock_client_error = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "GetObject",
    )
    mock_create_lg_records_and_copy_files.side_effect = mock_client_error

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_rollback_transaction.assert_called()
    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "Validation passed but error occurred during file transfer",
        "Y12345",
    )
    repo_under_test.bulk_upload_s3_repository.remove_ingested_file_from_source_bucket.assert_not_called()
    repo_under_test.dynamo_repository.report_upload_complete.assert_not_called()


def test_handle_sqs_message_happy_path_historical_name(
    set_env,
    mocker,
    mock_uuid,
    repo_under_test,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_report_upload_complete = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )
    mocker.patch.object(repo_under_test.bulk_upload_s3_repository, "check_virus_result")
    mock_pds_validation_strict.return_value = True

    repo_under_test.handle_sqs_message(message=TEST_SQS_MESSAGE)

    mock_create_lg_records_and_copy_files.assert_called_with(
        TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS
    )
    mock_report_upload_complete.assert_called()
    mock_report_upload_complete.assert_called_with(
        TEST_STAGING_METADATA,
        UploadStatus.COMPLETE,
        "Patient matched on historical name",
        "Y12345",
    )
    mock_remove_ingested_file_from_source_bucket.assert_called()


def test_handle_sqs_message_lenient_mode_happy_path(
    set_env,
    mocker,
    mock_uuid,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_lenient,
    mock_pds_validation_strict,
    mock_ods_validation,
):
    TEST_STAGING_METADATA.retries = 0
    service = BulkUploadService(strict_mode=False)
    mocker.patch.object(service, "dynamo_repository")
    mocker.patch.object(service, "sqs_repository")
    mocker.patch.object(service, "bulk_upload_s3_repository")
    mock_create_lg_records_and_copy_files = mocker.patch.object(
        BulkUploadService, "create_lg_records_and_copy_files"
    )
    mock_report_upload_complete = mocker.patch.object(
        service.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mock_remove_ingested_file_from_source_bucket = mocker.patch.object(
        service.bulk_upload_s3_repository, "remove_ingested_file_from_source_bucket"
    )
    mocker.patch.object(service.bulk_upload_s3_repository, "check_virus_result")

    service.handle_sqs_message(message=TEST_SQS_MESSAGE)
    mock_create_lg_records_and_copy_files.assert_called_with(
        TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS
    )
    mock_pds_validation_lenient.assert_called()
    mock_pds_validation_strict.assert_not_called()
    mock_report_upload_complete.assert_called()
    mock_remove_ingested_file_from_source_bucket.assert_called()


def test_concatenate_acceptance_reason(repo_under_test):
    accepted_reason = None
    test_reason = "test_reason_1"
    actual_reason = repo_under_test.concatenate_acceptance_reason(
        accepted_reason, test_reason
    )
    assert actual_reason == test_reason
    another_test_reason = "test_reason_2"
    another_actual_reason = repo_under_test.concatenate_acceptance_reason(
        actual_reason, another_test_reason
    )
    assert another_actual_reason == test_reason + ", " + another_test_reason


# Handle sqs message tests
def test_handle_sqs_message_happy_path_strict_mode(
    set_env,
    mocker,
    mock_uuid,
    repo_under_test,
    mock_validate_files,
    mock_pds_service,
    mock_pds_validation_strict,
    mock_ods_validation,
    mock_check_virus_result,
):
    TEST_STAGING_METADATA.retries = 0

    mock_check_virus_result_override = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository, "check_virus_result"
    )
    mock_check_virus_result_override.return_value = VirusScanResult.CLEAN

    mocker.patch.object(BulkUploadService, "create_lg_records_and_copy_files")
    mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )
    mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )

    mock_pds_validation_strict.return_value = True
    mock_ods_validation.return_value = True
    mock_validate_files.return_value = None

    repo_under_test.handle_sqs_message(TEST_SQS_MESSAGE)

    mock_check_virus_result_override.assert_called()

    expected_file_paths = [
        "1of3_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of3_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "3of3_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_validate_files.assert_called_with(
        expected_file_paths, TEST_STAGING_METADATA.nhs_number
    )


def test_handle_sqs_message_happy_path_v2(mocker, repo_under_test):
    mock_metadata = TEST_STAGING_METADATA
    mock_staging_metadata = mocker.patch.object(
        repo_under_test,
        "build_staging_metadata_from_message",
        return_value=mock_metadata,
    )

    mock_validate_entry = mocker.patch.object(
        repo_under_test, "validate_entry", return_value=("some reason", "Y12345")
    )

    mock_validate_virus_scan = mocker.patch.object(
        repo_under_test, "validate_virus_scan", return_value=True
    )

    mock_initiate_transactions = mocker.patch.object(
        repo_under_test, "initiate_transactions"
    )
    mock_transfer_files = mocker.patch.object(
        repo_under_test, "transfer_files", return_value=True
    )

    mock_remove_files = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "remove_ingested_file_from_source_bucket",
    )

    mock_write_report = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )

    mock_add_to_stitching_queue = mocker.patch.object(
        repo_under_test, "add_information_to_stitching_queue"
    )

    repo_under_test.handle_sqs_message(TEST_SQS_MESSAGE)

    mock_staging_metadata.assert_called_once_with(TEST_SQS_MESSAGE)
    mock_validate_entry.assert_called_once_with(mock_metadata)
    mock_validate_virus_scan.assert_called_once_with(mock_metadata, "Y12345")
    mock_initiate_transactions.assert_called_once()
    mock_transfer_files.assert_called_once_with(mock_metadata, "Y12345")
    mock_remove_files.assert_called_once()
    mock_write_report.assert_called_once_with(
        mock_metadata, UploadStatus.COMPLETE, "some reason", "Y12345"
    )
    mock_add_to_stitching_queue.assert_called_once_with(
        mock_metadata, "Y12345", "some reason"
    )


def test_build_staging_metadata_from_message(repo_under_test):
    result = repo_under_test.build_staging_metadata_from_message(TEST_SQS_MESSAGE)
    assert (
        result.nhs_number
        == TEST_SQS_MESSAGE["messageAttributes"]["NhsNumber"]["stringValue"]
    )
    assert len(result.files) > 0
    assert result.retries == 0


def test_build_staging_metadata_from_message_with_missing_body(repo_under_test):
    with pytest.raises(InvalidMessageException):
        repo_under_test.build_staging_metadata_from_message({})


def test_build_staging_metadata_from_message_with_invalid_json(repo_under_test):
    bad_message = {"body": '{"invalid_json": }'}
    with pytest.raises(InvalidMessageException):
        repo_under_test.build_staging_metadata_from_message(bad_message)


def test_validate_filenames(repo_under_test, mocker):
    test_file_path = "/9730787212/1of20_Lloyd_George_Record_[Brad Edmond Avery]_[9730787212]_[13-09-2006].pdf"
    test_nhs_number = "9730787212"

    metadata_file_data = {
        "FILEPATH": test_file_path,
        "PAGE COUNT": "20",
        "NHS-NO": test_nhs_number,
        "GP-PRACTICE-CODE": "Y12345",
        "SECTION": "SectionA",
        "SUB-SECTION": None,
        "SCAN-DATE": "13-09-2006",
        "SCAN-ID": "SCAN123",
        "USER-ID": "USER456",
        "UPLOAD": "UPLOAD789",
    }
    metadata_file = MetadataFile.parse_obj(metadata_file_data)

    staging_metadata_data = {
        "nhs_number": test_nhs_number,
        "files": [metadata_file],
        "retries": 0,
    }
    staging_metadata = StagingMetadata.parse_obj(staging_metadata_data)

    mock_validate_nhs = mocker.patch.object(bulk_upload_module, "validate_nhs_number")

    mock_validate_lg = mocker.patch.object(bulk_upload_module, "validate_lg_file_names")

    repo_under_test.validate_staging_metadata_filenames(staging_metadata)

    mock_validate_nhs.assert_called_once_with(test_nhs_number)
    mock_validate_lg.assert_called_once_with(
        [os.path.basename(test_file_path)],
        test_nhs_number,
    )


@pytest.fixture
def mock_patient(mocker):
    patient = mocker.Mock()
    patient.get_death_notification_status.return_value = None
    return patient


def test_validate_patient_data_happy_path(
    mocker, repo_under_test, mock_patient, mock_ods_validation_true
):
    file_names = ["Patient_John_Doe.pdf"]
    ods_code = "ODS123"

    repo_under_test.bypass_pds = False

    mock_validate_file_name = mocker.patch.object(
        repo_under_test, "validate_file_name", return_value="reason: filename check"
    )
    mock_deceased = mocker.patch.object(
        repo_under_test,
        "deceased_validation",
        return_value="reason: filename check; patient deceased",
    )
    mock_restricted = mocker.patch.object(
        repo_under_test,
        "restricted_validation",
        return_value="reason: filename check; patient deceased; restricted",
    )

    result = repo_under_test.validate_patient_data_access_conditions(
        file_names, mock_patient, ods_code
    )

    assert result == "reason: filename check; patient deceased; restricted"
    mock_validate_file_name.assert_called_once_with(file_names, mock_patient)
    mock_deceased.assert_called_once_with("reason: filename check", mock_patient)
    mock_restricted.assert_called_once_with(
        "reason: filename check; patient deceased", ods_code
    )


def test_validate_file_name_strict_mode_with_history_match(
    mocker, repo_under_test, mock_patient
):
    mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_strict",
        return_value=True,
    )
    mock_concat = mocker.patch.object(
        repo_under_test, "concatenate_acceptance_reason", side_effect=lambda a, b: b
    )

    result = repo_under_test.validate_file_name(["file.pdf"], mock_patient)

    assert result == "Patient matched on historical name"
    mock_concat.assert_called_once_with(None, "Patient matched on historical name")


def test_validate_file_name_strict_mode_with_no_history_match(
    mocker, repo_under_test, mock_patient
):
    mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_strict",
        return_value=False,
    )
    mock_concat = mocker.patch.object(repo_under_test, "concatenate_acceptance_reason")

    result = repo_under_test.validate_file_name(["file.pdf"], mock_patient)

    assert result is None
    mock_concat.assert_not_called()


def test_validate_file_name_lenient_mode_with_history_match(
    mocker, lenient_repo, mock_patient
):
    mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_lenient",
        return_value=("some reason", True),
    )
    mock_concat = mocker.patch.object(
        lenient_repo,
        "concatenate_acceptance_reason",
        side_effect=lambda a, b: f"{a}, {b}" if a else b,
    )

    result = lenient_repo.validate_file_name(["file.pdf"], mock_patient)

    assert result == "some reason, Patient matched on historical name"
    assert mock_concat.call_count == 2


def test_deceased_validation_with_status(mocker, repo_under_test, mock_patient):
    mock_status = mocker.Mock()
    mock_status.name = "FORMAL"
    mock_patient.get_death_notification_status.return_value = mock_status

    mock_concat = mocker.patch.object(
        repo_under_test,
        "concatenate_acceptance_reason",
        return_value="existing reason; Patient is deceased - FORMAL",
    )

    result = repo_under_test.deceased_validation("existing reason", mock_patient)

    mock_concat.assert_called_once_with(
        "existing reason", "Patient is deceased - FORMAL"
    )
    assert result == "existing reason; Patient is deceased - FORMAL"


def test_deceased_validation_without_status(mocker, repo_under_test, mock_patient):
    mock_patient.get_death_notification_status.return_value = None

    mock_concat = mocker.patch.object(repo_under_test, "concatenate_acceptance_reason")

    result = repo_under_test.deceased_validation("existing reason", mock_patient)

    assert result == "existing reason"
    mock_concat.assert_not_called()


def test_restricted_validation_with_restricted_code(mocker, repo_under_test):
    accepted_reason = "some reason"
    patient_ods_code = PatientOdsInactiveStatus.RESTRICTED

    mock_concat = mocker.patch.object(
        repo_under_test,
        "concatenate_acceptance_reason",
        return_value="some reason; PDS record is restricted",
    )

    result = repo_under_test.restricted_validation(accepted_reason, patient_ods_code)

    mock_concat.assert_called_once_with(accepted_reason, "PDS record is restricted")
    assert result == "some reason; PDS record is restricted"


def test_restricted_validation_with_non_restricted_code(mocker, repo_under_test):
    accepted_reason = "some reason"
    patient_ods_code = "ACTIVE"

    mock_concat = mocker.patch.object(repo_under_test, "concatenate_acceptance_reason")

    result = repo_under_test.restricted_validation(accepted_reason, patient_ods_code)

    mock_concat.assert_not_called()
    assert result == accepted_reason


def test_validate_entry_happy_path(mocker, repo_under_test, mock_patient):
    staging_metadata = TEST_STAGING_METADATA

    mock_validate_filenames = mocker.patch.object(
        repo_under_test, "validate_staging_metadata_filenames"
    )
    mock_getting_patient_info_from_pds = mocker.patch.object(
        bulk_upload_module, "getting_patient_info_from_pds"
    )
    mock_patient = mocker.Mock()
    mock_patient.get_ods_code_or_inactive_status_for_gp.return_value = "Y12345"
    mock_getting_patient_info_from_pds.return_value = mock_patient

    mock_validate_accessing_patient_data = mocker.patch.object(
        repo_under_test,
        "validate_patient_data_access_conditions",
        return_value="some reason",
    )

    accepted_reason, patient_ods_code = repo_under_test.validate_entry(staging_metadata)

    mock_validate_filenames.assert_called_once_with(staging_metadata)
    mock_getting_patient_info_from_pds.assert_called_once_with(
        staging_metadata.nhs_number
    )
    mock_validate_accessing_patient_data.assert_called_once_with(
        [os.path.basename(f.file_path) for f in staging_metadata.files],
        mock_patient,
        "Y12345",
    )

    assert accepted_reason == "some reason"
    assert patient_ods_code == "Y12345"


def test_validate_entry_invalid_file_exception_triggers_write_to_dynamo(
    mocker, repo_under_test
):
    staging_metadata = TEST_STAGING_METADATA

    mocker.patch.object(
        repo_under_test,
        "validate_staging_metadata_filenames",
        side_effect=LGInvalidFilesException("invalid file"),
    )
    mock_write_report = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )

    accepted_reason, patient_ods_code = repo_under_test.validate_entry(staging_metadata)

    mock_write_report.assert_called_once()
    args, kwargs = mock_write_report.call_args
    assert args[1] == UploadStatus.FAILED
    assert "invalid file" in args[2]

    assert accepted_reason is None
    assert patient_ods_code is None


def test_validate_entry_patient_record_exists_exception(mocker, repo_under_test):
    staging_metadata = TEST_STAGING_METADATA

    mocker.patch.object(
        repo_under_test,
        "validate_staging_metadata_filenames",
        side_effect=PatientRecordAlreadyExistException("record exists"),
    )
    mock_write_report = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )

    accepted_reason, patient_ods_code = repo_under_test.validate_entry(staging_metadata)

    mock_write_report.assert_called_once()
    args, kwargs = mock_write_report.call_args
    assert args[1] == UploadStatus.FAILED
    assert "record exists" in args[2]

    assert accepted_reason is None
    assert patient_ods_code is None


def test_validate_entry_invalid_nhs_number_exception(mocker, repo_under_test):
    staging_metadata = TEST_STAGING_METADATA

    mocker.patch.object(
        repo_under_test,
        "validate_staging_metadata_filenames",
        side_effect=InvalidNhsNumberException("bad nhs"),
    )
    mock_write_report = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )

    accepted_reason, patient_ods_code = repo_under_test.validate_entry(staging_metadata)

    mock_write_report.assert_called_once()
    args, kwargs = mock_write_report.call_args
    assert "bad nhs" in args[2]

    assert accepted_reason is None
    assert patient_ods_code is None


def test_validate_accessing_patient_data_returns_none_when_pds_fhir_always_true(
    repo_under_test, mock_patient
):
    repo_under_test.bypass_pds = True

    result = repo_under_test.validate_patient_data_access_conditions(
        ["file.pdf"], mock_patient, "A1234"
    )

    assert result is None


def test_validate_accessing_patient_data_strict_mode_calls_strict_validation(
    mocker, repo_under_test, mock_patient, mock_ods_validation_true
):
    mock_validate = mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_strict",
        return_value=False,
    )

    result = repo_under_test.validate_patient_data_access_conditions(
        ["file.pdf"], mock_patient, "A1234"
    )

    mock_validate.assert_called_once()
    mock_ods_validation_true.assert_called_once()
    assert result is None


@pytest.fixture
def lenient_repo(set_env, mocker):  # 👈 include set_env
    service = BulkUploadService(strict_mode=False)
    mocker.patch.object(service, "dynamo_repository")
    mocker.patch.object(service, "sqs_repository")
    mocker.patch.object(service, "bulk_upload_s3_repository")
    return service


@pytest.fixture
def mock_validate_lenient(mocker):
    patcher = mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_lenient",
        return_value=("some reason", False),
    )
    yield patcher


def test_validate_accessing_patient_data_lenient_mode_calls_lenient_validation(
    lenient_repo, mock_patient, mock_validate_lenient, mock_ods_validation_true
):
    result = lenient_repo.validate_patient_data_access_conditions(
        ["file.pdf"], mock_patient, "A1234"
    )

    mock_validate_lenient.assert_called_once()
    mock_ods_validation_true.assert_called_once()
    assert "some reason" in result


def test_validate_accessing_patient_data_adds_historic_name_reason_when_flag_true(
    mocker, lenient_repo, mock_patient, mock_ods_validation_true
):
    mocker.patch.object(
        bulk_upload_module,
        "validate_filename_with_patient_details_lenient",
        return_value=("some reason", True),
    )

    result = lenient_repo.validate_patient_data_access_conditions(
        ["file.pdf"], mock_patient, "A1234"
    )

    assert "some reason" in result
    assert "Patient matched on historical name" in result


def test_validate_accessing_patient_data_raises_exception_when_ods_code_not_allowed(
    lenient_repo, mock_patient, mock_validate_lenient, mock_ods_validation
):
    mock_ods_validation.return_value = False
    with pytest.raises(
        LGInvalidFilesException, match="Patient not registered at your practice"
    ):
        lenient_repo.validate_patient_data_access_conditions(
            ["file.pdf"], mock_patient, "A1234"
        )


def test_validate_accessing_patient_data_adds_deceased_reason(
    mocker, lenient_repo, mock_patient, mock_validate_lenient, mock_ods_validation_true
):
    deceased_status_mock = mocker.Mock()
    deceased_status_mock.name = "Formal"
    mock_patient.get_death_notification_status.return_value = deceased_status_mock

    result = lenient_repo.validate_patient_data_access_conditions(
        ["file.pdf"], mock_patient, "A1234"
    )

    assert "some reason" in result
    assert "Patient is deceased - Formal" in result


def test_validate_accessing_patient_data_adds_restricted_reason(
    mocker, lenient_repo, mock_patient, mock_validate_lenient
):
    mocker.patch.object(
        bulk_upload_module,
        "allowed_to_ingest_ods_code",
        return_value=True,
    )
    result = lenient_repo.validate_patient_data_access_conditions(
        ["file.pdf"], mock_patient, PatientOdsInactiveStatus.RESTRICTED
    )

    assert "some reason" in result
    assert "PDS record is restricted" in result


def test_virus_scan_success(repo_under_test, mocker):
    mocker.patch.object(repo_under_test, "resolve_source_file_path")
    mock_check = mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository, "check_virus_result"
    )

    result = repo_under_test.validate_virus_scan(TEST_STAGING_METADATA, "ODS123")

    assert result is True
    mock_check.assert_called_once_with(
        TEST_STAGING_METADATA, repo_under_test.file_path_cache
    )


def test_virus_scan_no_result_max_retries(repo_under_test, mocker):
    metadata = copy(TEST_STAGING_METADATA)
    metadata.retries = 15

    mocker.patch.object(repo_under_test, "resolve_source_file_path")
    mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "check_virus_result",
        side_effect=VirusScanNoResultException("no result"),
    )

    result = repo_under_test.validate_virus_scan(metadata, "ODS123")

    assert result is False
    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called_once_with(
        metadata,
        UploadStatus.FAILED,
        "File was not scanned for viruses before maximum retries attempted",
        "ODS123",
    )


def test_virus_scan_no_result_retries_remaining(repo_under_test, mocker):
    metadata = copy(TEST_STAGING_METADATA)
    metadata.retries = 5

    mocker.patch.object(repo_under_test, "resolve_source_file_path")
    mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "check_virus_result",
        side_effect=VirusScanNoResultException("no result"),
    )

    result = repo_under_test.validate_virus_scan(metadata, "ODS123")

    assert result is False
    repo_under_test.sqs_repository.put_staging_metadata_back_to_queue.assert_called_once_with(
        metadata
    )


def test_virus_scan_failed_exception(repo_under_test, mocker):
    mocker.patch.object(repo_under_test, "resolve_source_file_path")
    mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "check_virus_result",
        side_effect=VirusScanFailedException("fail"),
    )

    result = repo_under_test.validate_virus_scan(TEST_STAGING_METADATA, "ODS123")

    assert result is False
    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called_once_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "One or more of the files failed virus scanner check",
        "ODS123",
    )


def test_virus_scan_document_infected_exception(repo_under_test, mocker):
    mocker.patch.object(repo_under_test, "resolve_source_file_path")
    mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "check_virus_result",
        side_effect=DocumentInfectedException("infected"),
    )

    result = repo_under_test.validate_virus_scan(TEST_STAGING_METADATA, "ODS123")

    assert result is False
    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called_once_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "One or more of the files failed virus scanner check",
        "ODS123",
    )


def test_virus_scan_file_not_found(repo_under_test, mocker):
    mocker.patch.object(repo_under_test, "resolve_source_file_path")
    mocker.patch.object(
        repo_under_test.bulk_upload_s3_repository,
        "check_virus_result",
        side_effect=S3FileNotFoundException("missing"),
    )

    result = repo_under_test.validate_virus_scan(TEST_STAGING_METADATA, "ODS123")

    assert result is False
    repo_under_test.dynamo_repository.write_report_upload_to_dynamo.assert_called_once_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "One or more of the files is not accessible from staging bucket",
        "ODS123",
    )


def test_initiate_transactions_calls_repos(repo_under_test):
    repo_under_test.initiate_transactions()

    repo_under_test.bulk_upload_s3_repository.init_transaction.assert_called_once()
    repo_under_test.dynamo_repository.init_transaction.assert_called_once()


def test_transfer_files_success(repo_under_test, mocker):
    mock_create = mocker.patch.object(
        repo_under_test, "create_lg_records_and_copy_files"
    )

    result = repo_under_test.transfer_files(TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS)

    assert result is True
    mock_create.assert_called_once_with(TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS)


def test_transfer_files_client_error_triggers_rollback(repo_under_test, mocker):
    mocker.patch.object(
        repo_under_test,
        "create_lg_records_and_copy_files",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "Something failed"}}, "CopyObject"
        ),
    )
    mock_rollback = mocker.patch.object(repo_under_test, "rollback_transaction")
    mock_write_report = mocker.patch.object(
        repo_under_test.dynamo_repository, "write_report_upload_to_dynamo"
    )

    result = repo_under_test.transfer_files(TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS)

    assert result is False
    mock_rollback.assert_called_once()
    mock_write_report.assert_called_once_with(
        TEST_STAGING_METADATA,
        UploadStatus.FAILED,
        "Validation passed but error occurred during file transfer",
        TEST_CURRENT_GP_ODS,
    )


def test_add_information_to_stitching_queue(repo_under_test, mocker):
    mock_send = mocker.patch.object(
        repo_under_test.sqs_repository, "send_message_to_pdf_stitching_queue"
    )

    repo_under_test.add_information_to_stitching_queue(
        TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS, accepted_reason="Some reason"
    )

    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args

    assert kwargs["queue_url"] == repo_under_test.pdf_stitching_queue_url

    message = kwargs["message"]
    assert message.nhs_number == TEST_STAGING_METADATA.nhs_number
    assert message.snomed_code_doc_type.code == "16521000000101"
    assert message.snomed_code_doc_type.display_name == "Lloyd George record folder"


def test_add_information_to_stitching_queue_calls_send_with_correct_values(
    repo_under_test, mocker
):
    mock_send = mocker.patch.object(
        repo_under_test.sqs_repository, "send_message_to_pdf_stitching_queue"
    )

    repo_under_test.add_information_to_stitching_queue(
        TEST_STAGING_METADATA, TEST_CURRENT_GP_ODS, accepted_reason="Some reason"
    )

    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args

    assert kwargs["queue_url"] == repo_under_test.pdf_stitching_queue_url

    message = kwargs["message"]
    assert message.nhs_number == TEST_STAGING_METADATA.nhs_number
    assert message.snomed_code_doc_type.code == "16521000000101"
