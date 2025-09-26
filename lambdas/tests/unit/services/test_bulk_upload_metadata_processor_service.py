import os
import tempfile
from unittest.mock import call

import pytest
from botocore.exceptions import ClientError
from enums.upload_status import UploadStatus
from freezegun import freeze_time
from models.staging_metadata import METADATA_FILENAME, MetadataFile
from services.bulk_upload_metadata_preprocessor_service import MetadataPreprocessorService
from services.bulk_upload_metadata_processor_service import (
    BulkUploadMetadataProcessorService,
)
from tests.unit.conftest import MOCK_LG_METADATA_SQS_QUEUE
from tests.unit.helpers.data.bulk_upload.test_data import (
    EXPECTED_PARSED_METADATA,
    EXPECTED_PARSED_METADATA_2,
    EXPECTED_SQS_MSG_FOR_PATIENT_123456789,
    EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
    MOCK_METADATA,
)
from utils.exceptions import BulkUploadMetadataException, InvalidFileNameException, LGInvalidFilesException

METADATA_FILE_DIR = "tests/unit/helpers/data/bulk_upload"
MOCK_METADATA_CSV = f"{METADATA_FILE_DIR}/metadata.csv"
MOCK_DUPLICATE_ODS_METADATA_CSV = (
    f"{METADATA_FILE_DIR}/metadata_with_duplicates_different_ods.csv"
)
MOCK_INVALID_METADATA_CSV_FILES = [
    f"{METADATA_FILE_DIR}/metadata_invalid.csv",
    f"{METADATA_FILE_DIR}/metadata_invalid_empty_nhs_number.csv",
    f"{METADATA_FILE_DIR}/metadata_invalid_unexpected_comma.csv",
]
MOCK_TEMP_FOLDER = "tests/unit/helpers/data/bulk_upload"

SERVICE_PATH = "services.bulk_upload_metadata_processor_service"

class MockMetadataPreprocessorService(MetadataPreprocessorService):
    def validate_record_filename(self, original_filename: str, *args, **kwargs) -> str:
        return original_filename


@pytest.fixture(autouse=True)
@freeze_time("2025-01-01T12:00:00")
def test_service(mocker, set_env, mock_tempfile):
    mocker.patch("services.bulk_upload_metadata_processor_service.S3Service")
    mocker.patch("services.bulk_upload_metadata_processor_service.SQSService")
    mocker.patch("services.bulk_upload_metadata_processor_service.BulkUploadDynamoRepository")
    service = BulkUploadMetadataProcessorService(
        MockMetadataPreprocessorService(practice_directory="test_practice_directory")
    )
    mocker.patch.object(service, "s3_service")
    return service


@pytest.fixture
def metadata_filename():
    return METADATA_FILENAME


@pytest.fixture
def mock_download_metadata_from_s3(mocker):
    yield mocker.patch.object(
        BulkUploadMetadataProcessorService, "download_metadata_from_s3"
    )


@pytest.fixture
def mock_s3_service(test_service):
    return test_service.s3_service


@pytest.fixture
def mock_tempfile(mocker):
    mocker.patch.object(tempfile, "mkdtemp", return_value=MOCK_TEMP_FOLDER)
    mocker.patch("shutil.rmtree")
    yield


@pytest.fixture
def mock_sqs_service(test_service):
    return test_service.sqs_service


@pytest.fixture
def base_metadata_file():
    row = {
        "FILEPATH": "valid/path/to/file.pdf",
        "GP-PRACTICE-CODE": "Y12345",
        "NHS-NO": "1234567890",
        "PAGE COUNT": "1",
        "SECTION": "LG",
        "SUB-SECTION": "",
        "SCAN-DATE": "02/01/2023",
        "SCAN-ID": "SID456",
        "USER-ID": "UID456",
        "UPLOAD": "02/01/2023",
    }

    return MetadataFile.model_validate(row)


# TODO: Possibly needed as part of PRMT-576
# def test_update_date_in_row(test_service):
#     metadata_row = {"SCAN-DATE": "2025.01.01", "UPLOAD": "2025.01.01"}
#
#     updated_row = test_service.update_date_in_row(metadata_row)
#
#     assert updated_row["SCAN-DATE"] == "2025/01/01"
#     assert updated_row["UPLOAD"] == "2025/01/01"


def test_process_metadata_send_metadata_to_sqs_queue(
    mocker,
    test_service,
    mock_download_metadata_from_s3,
):
    fake_csv_path = "fake/path/metadata.csv"
    fake_uuid = "123412342"

    mock_download_metadata_from_s3.return_value = fake_csv_path

    mocker.patch.object(
        test_service.s3_service, "copy_across_bucket", return_value=None
    )
    mocker.patch.object(
        test_service.s3_service, "delete_object", return_value=None
    )

    mocker.patch("uuid.uuid4", return_value=fake_uuid)

    fake_metadata = [
        {"nhs_number": "1234567890", "some_data": "value1"},
        {"nhs_number": "123456789", "some_data": "value2"},
        {"nhs_number": "0000000000", "some_data": "value3"},
    ]
    mocker.patch.object(
        test_service,
        "csv_to_staging_metadata",
        return_value=fake_metadata,
    )

    mocked_send_metadata = mocker.patch.object(
        test_service, "send_metadata_to_fifo_sqs"
    )

    test_service.process_metadata()

    assert mocked_send_metadata.call_count == 1
    mocked_send_metadata.assert_called_once_with(fake_metadata)


def test_process_metadata_catch_and_log_error_when_fail_to_get_metadata_csv_from_s3(
    set_env,
    caplog,
    mock_s3_service,
    mock_sqs_service,
    test_service,
):
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}},
        "S3:HeadObject",
    )
    expected_err_msg = 'No metadata file could be found with the name "metadata.csv"'

    with pytest.raises(BulkUploadMetadataException) as e:
        test_service.process_metadata()

    assert expected_err_msg in str(e.value)
    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"

    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_validation_error_when_metadata_csv_is_invalid(
    mock_sqs_service,
    mock_download_metadata_from_s3,
    test_service,
    mocker,
):
    mock_download_metadata_from_s3.return_value = "fake/path.csv"

    mocker.patch.object(
        test_service,
        "csv_to_staging_metadata",
        side_effect=BulkUploadMetadataException("validation error"),
    )

    with pytest.raises(BulkUploadMetadataException) as exc_info:
        test_service.process_metadata()

    assert "validation error" in str(exc_info.value)
    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_validation_error_when_gp_practice_code_is_missing(
    caplog,
    mock_sqs_service,
    mock_download_metadata_from_s3,
    test_service,
    mocker,
):
    mock_download_metadata_from_s3.return_value = "fake/path.csv"

    expected_error_log = (
        "Failed to parse metadata.csv: 1 validation error for MetadataFile\n"
        + "GP-PRACTICE-CODE\n  missing GP-PRACTICE-CODE for patient 1234567890"
    )

    mocker.patch.object(
        test_service,
        "csv_to_staging_metadata",
        side_effect=BulkUploadMetadataException(expected_error_log),
    )

    with pytest.raises(BulkUploadMetadataException) as e:
        test_service.process_metadata()

    assert expected_error_log in str(e.value)

    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_client_error_when_failed_to_send_message_to_sqs(
    test_service,
    mocker,
):
    mocker.patch.object(
        test_service,
        "download_metadata_from_s3",
        return_value="fake/path.csv",
    )

    dummy_staging_metadata = mocker.Mock()
    dummy_staging_metadata.nhs_number = "1234567890"
    mocker.patch.object(
        test_service,
        "csv_to_staging_metadata",
        return_value=[dummy_staging_metadata],
    )

    mock_client_error = ClientError(
        {
            "Error": {
                "Code": "AWS.SimpleQueueService.NonExistentQueue",
                "Message": "The specified queue does not exist",
            }
        },
        "SendMessage",
    )

    mocker.patch.object(
        test_service,
        "send_metadata_to_fifo_sqs",
        side_effect=BulkUploadMetadataException(str(mock_client_error)),
    )

    expected_err_msg = (
        "An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the SendMessage operation:"
        " The specified queue does not exist"
    )

    with pytest.raises(BulkUploadMetadataException) as e:
        test_service.process_metadata()

    assert expected_err_msg in str(e.value)


def test_download_metadata_from_s3(mock_s3_service, test_service):
    result = test_service.download_metadata_from_s3()

    expected_download_path = os.path.join(
        test_service.temp_download_dir, METADATA_FILENAME
    )
    expected_file_key = (
        f"{test_service.practice_directory}/{METADATA_FILENAME}"
    )

    mock_s3_service.download_file.assert_called_once_with(
        s3_bucket_name=test_service.staging_bucket_name,
        file_key=expected_file_key,
        download_path=expected_download_path,
    )

    assert result == expected_download_path


def test_download_metadata_from_s3_raise_error_when_failed_to_download(
    set_env, mock_s3_service, mock_tempfile, test_service
):
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "file not exist in bucket"}},
        "s3_get_object",
    )

    with pytest.raises(ClientError):
        test_service.download_metadata_from_s3()


def test_duplicates_csv_to_staging_metadata(mocker, test_service):
    header = (
        "FILEPATH,PAGE COUNT,GP-PRACTICE-CODE,NHS-NO,SECTION,SUB-SECTION,"
        "SCAN-DATE,SCAN-ID,USER-ID,UPLOAD"
    )
    line1 = (
        '/1234567890/1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y12345",'
        '"1234567890","LG","","03/09/2022","NEC","NEC","04/10/2023"'
    )
    line2 = (
        '/1234567890/2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y12345",'
        '"1234567890","LG","","03/09/2022","NEC","NEC","04/10/2023"'
    )
    line3 = (
        '/1234567890/1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y6789",'
        '"1234567890","LG","","03/09/2022","NEC","NEC","04/10/2023"'
    )
    line4 = (
        '/1234567890/2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y6789",'
        '"1234567890","LG","","03/09/2022","NEC","NEC","04/10/2023"'
    )
    line5 = (
        '1of1_Lloyd_George_Record_[Joe Bloggs_invalid]_[123456789]_[25-12-2019].txt,"","Y12345",'
        '"123456789","LG","","04/09/2022","NEC","NEC","04/10/2023"'
    )
    line6 = (
        '1of1_Lloyd_George_Record_[Joe Bloggs_invalid]_[123456789]_[25-12-2019].txt,"","Y6789",'
        '"123456789","LG","","04/09/2022","NEC","NEC","04/10/2023"'
    )
    line7 = (
        '1of1_Lloyd_George_Record_[Jane Smith]_[1234567892]_[25-12-2019].txt,"","Y12345","","LG","","04/09/2022",'
        '"NEC","NEC","04/10/2023"'
    )
    line8 = (
        '1of1_Lloyd_George_Record_[Jane Smith]_[1234567892]_[25-12-2019].txt,"","Y6789","","LG","","04/09/2022",'
        '"NEC","NEC","04/10/2023"'
    )

    fake_csv_data = "\n".join(
        [header, line1, line2, line3, line4, line5, line6, line7, line8]
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=fake_csv_data))
    mocker.patch("os.path.isfile", return_value=True)

    actual = test_service.csv_to_staging_metadata("fake/path.csv")
    expected = EXPECTED_PARSED_METADATA_2
    assert actual == expected


def test_send_metadata_to_sqs(
    set_env, mocker, mock_sqs_service, test_service
):
    mocker.patch("uuid.uuid4", return_value="123412342")
    expected_calls = [
        call(
            queue_url=MOCK_LG_METADATA_SQS_QUEUE,
            message_body=EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
            nhs_number="1234567890",
            group_id="bulk_upload_123412342",
        ),
        call(
            queue_url=MOCK_LG_METADATA_SQS_QUEUE,
            message_body=EXPECTED_SQS_MSG_FOR_PATIENT_123456789,
            nhs_number="123456789",
            group_id="bulk_upload_123412342",
        ),
    ]

    test_service.send_metadata_to_fifo_sqs(MOCK_METADATA)

    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_has_calls(
        expected_calls
    )
    assert mock_sqs_service.send_message_with_nhs_number_attr_fifo.call_count == 2


def test_send_metadata_to_sqs_raise_error_when_fail_to_send_message(
    set_env, mock_sqs_service, test_service
):
    mock_sqs_service.send_message_with_nhs_number_attr_fifo.side_effect = ClientError(
        {
            "Error": {
                "Code": "AWS.SimpleQueueService.NonExistentQueue",
                "Message": "The specified queue does not exist",
            }
        },
        "SendMessage",
    )

    with pytest.raises(ClientError):
        test_service.send_metadata_to_fifo_sqs(EXPECTED_PARSED_METADATA)


def test_clear_temp_storage(set_env, mocker, mock_tempfile, test_service):
    mocked_rm = mocker.patch("shutil.rmtree")

    test_service.clear_temp_storage()

    mocked_rm.assert_called_once_with(test_service.temp_download_dir)


def test_process_metadata_row_success(mocker, test_service):
    patients = {}
    row = {
        "FILEPATH": "/some/path/file.pdf",
        "GP-PRACTICE-CODE": "Y12345",
        "NHS-NO": "1234567890",
        "PAGE COUNT": "5",
        "SECTION": "LG",
        "SUB-SECTION": "",
        "SCAN-DATE": "01/01/2023",
        "SCAN-ID": "SID123",
        "USER-ID": "UID123",
        "UPLOAD": "01/01/2023",
    }

    mock_metadata = mocker.Mock()
    mocker.patch(
        f"{SERVICE_PATH}.MetadataFile.model_validate",
        return_value=mock_metadata,
    )

    mock_metadata.nhs_number = "1234567890"
    mock_metadata.gp_practice_code = "Y12345"
    mock_metadata.file_path = "/some/path/file.pdf"

    mocker.patch.object(
        test_service,
        "validate_correct_filename",
        return_value="corrected.pdf",
    )

    test_service.process_metadata_row(row, patients)

    key = ("1234567890", "Y12345")

    assert key in patients
    assert patients[key] == [mock_metadata]
    assert mock_metadata.stored_file_name == "corrected.pdf"




def test_process_metadata_row_adds_to_existing_entry(
    mocker, test_service
):
    key = ("1234567890", "Y12345")
    mock_metadata_existing = mocker.Mock()
    patients = {key: [mock_metadata_existing]}

    row = {
        "FILEPATH": "/some/path/file2.pdf",
        "GP-PRACTICE-CODE": "Y12345",
        "NHS-NO": "1234567890",
        "PAGE COUNT": "1",
        "SECTION": "LG",
        "SUB-SECTION": "",
        "SCAN-DATE": "02/01/2023",
        "SCAN-ID": "SID456",
        "USER-ID": "UID456",
        "UPLOAD": "02/01/2023",
    }

    mock_metadata = mocker.Mock()

    mock_metadata.nhs_number = "1234567890"
    mock_metadata.gp_practice_code = "Y12345"
    mock_metadata.file_path = "/some/path/file2.pdf"

    mocker.patch(
        f"{SERVICE_PATH}.MetadataFile.model_validate",
        return_value=mock_metadata,
    )

    test_service.process_metadata_row(row, patients)

    assert len(patients[key]) == 2
    assert patients[key][1] == mock_metadata


def test_extract_patient_info(test_service, base_metadata_file):
    nhs_number, ods_code = test_service.extract_patient_info(
        base_metadata_file
    )

    assert nhs_number == "1234567890"
    assert ods_code == "Y12345"


def test_validate_correct_filename_when_valid_filename(
        mocker, test_service,base_metadata_file
):
    valid_file_path = base_metadata_file.file_path
    filename = valid_file_path.split("/")[-1]

    mock_validate = mocker.patch(f"{SERVICE_PATH}.validate_file_name")

    result = test_service.validate_correct_filename(base_metadata_file)

    mock_validate.assert_called_once_with(filename)
    assert result == valid_file_path

def test_validate_correct_filename_when_invalid_filename_calls_formatter(
    mocker, test_service, base_metadata_file
):
    invalid_file_path = base_metadata_file.file_path
    filename = invalid_file_path.split("/")[-1]

    mock_validate = mocker.patch(f"{SERVICE_PATH}.validate_file_name")
    mock_validate.side_effect = LGInvalidFilesException("Invalid filename")

    mock_format = mocker.patch.object(
        test_service.metadata_formatter_service,
        "validate_record_filename",
        return_value="formatted/path/to/file.pdf"
    )

    result = test_service.validate_correct_filename(base_metadata_file)

    mock_validate.assert_called_once_with(filename)
    mock_format.assert_called_once_with(invalid_file_path)
    assert result == "formatted/path/to/file.pdf"

def test_handle_invalid_filename_writes_failed_entry_to_dynamo(
    mocker, test_service, base_metadata_file
):
    key = ("1234567890", "Y12345")
    error = InvalidFileNameException("Invalid filename format")

    fake_file = mocker.Mock()
    patients = {key: [fake_file]}

    mock_staging_metadata = mocker.patch(f"{SERVICE_PATH}.StagingMetadata")

    mock_write = mocker.patch.object(
        test_service.dynamo_repository, "write_report_upload_to_dynamo"
    )

    test_service.handle_invalid_filename(
        base_metadata_file, error, key, patients
    )

    mock_staging_metadata.assert_called_once_with(
        nhs_number=key[0],
        files=patients[key],
    )

    mock_write.assert_called_once_with(
        mock_staging_metadata.return_value,
        UploadStatus.FAILED,
        str(error),
    )
