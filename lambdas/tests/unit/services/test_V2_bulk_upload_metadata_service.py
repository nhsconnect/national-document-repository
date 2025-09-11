import os
import tempfile
import textwrap
from unittest.mock import call

import pytest
from botocore.exceptions import ClientError
from freezegun import freeze_time
from models.staging_metadata import METADATA_FILENAME
from services.V2_bulk_upload_metadata_service import V2BulkUploadMetadataService
from tests.unit.conftest import MOCK_LG_METADATA_SQS_QUEUE
from tests.unit.helpers.data.bulk_upload.test_data import (
    EXPECTED_PARSED_METADATA,
    EXPECTED_PARSED_METADATA_2,
    EXPECTED_SQS_MSG_FOR_PATIENT_123456789,
    EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
    MOCK_METADATA,
)
from utils.exceptions import BulkUploadMetadataException, InvalidFileNameException

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


@pytest.fixture(autouse=True)
@freeze_time("2025-01-01T12:00:00")
def test_service(mocker, set_env):
    service = V2BulkUploadMetadataService(practice_directory="test_practice_directory")
    mocker.patch.object(service, "s3_service")
    return service


@pytest.fixture
def metadata_service():
    yield V2BulkUploadMetadataService("test_practice_directory")


@pytest.fixture
def metadata_filename():
    return METADATA_FILENAME


@pytest.fixture
def mock_download_metadata_from_s3(mocker):
    yield mocker.patch.object(V2BulkUploadMetadataService, "download_metadata_from_s3")


@pytest.fixture
def mock_s3_service(mocker):
    patched_instance = mocker.patch(
        "services.V2_bulk_upload_metadata_service.S3Service"
    ).return_value
    yield patched_instance


@pytest.fixture
def mock_tempfile(mocker):
    mocker.patch.object(tempfile, "mkdtemp", return_value=MOCK_TEMP_FOLDER)
    mocker.patch("shutil.rmtree")
    yield


@pytest.fixture
def mock_sqs_service(mocker):
    patched_instance = mocker.patch(
        "services.V2_bulk_upload_metadata_service.SQSService"
    ).return_value
    yield patched_instance


def test_validate_record_filename_successful(test_service, mocker):
    original_filename = "/M89002/01 of 02_Lloyd_George_Record_[Dwayne The Rock Johnson]_[9730787506]_[18-09-1974].pdf"
    smaller_path = "[9730787506]_[18-09-1974].pdf"

    mocker.patch.object(
        test_service, "extract_document_path", return_value=("/M89002/", smaller_path)
    )
    mocker.patch.object(
        test_service,
        "extract_document_number_bulk_upload_file_name",
        return_value=("01", "02", smaller_path),
    )
    mocker.patch.object(
        test_service,
        "extract_lloyd_george_record_from_bulk_upload_file_name",
        return_value=("Lloyd_George_Record", smaller_path),
    )
    mocker.patch.object(
        test_service,
        "extract_patient_name_from_bulk_upload_file_name",
        return_value=("Dwayne The Rock Johnson", smaller_path),
    )
    mocker.patch.object(
        test_service,
        "extract_nhs_number_from_bulk_upload_file_name",
        return_value=("9730787506", smaller_path),
    )
    mocker.patch.object(
        test_service,
        "extract_date_from_bulk_upload_file_name",
        return_value=("18", "09", "1974", smaller_path),
    )
    mocker.patch.object(
        test_service,
        "extract_file_extension_from_bulk_upload_file_name",
        return_value="pdf",
    )
    mock_assemble = mocker.patch.object(
        test_service, "assemble_valid_file_name", return_value="final_filename.pdf"
    )

    result = test_service.validate_record_filename(original_filename)

    assert result == "final_filename.pdf"
    mock_assemble.assert_called_once()


def test_validate_record_filename_invalid_digit_count(mocker, test_service, caplog):
    bad_filename = "01 of 02_Lloyd_George_Record_[John Doe]_[12345]_[01-01-2000].pdf"

    mocker.patch.object(
        test_service, "extract_document_path", return_value=("prefix", bad_filename)
    )
    mocker.patch.object(
        test_service,
        "extract_document_number_bulk_upload_file_name",
        return_value=("01", "02", bad_filename),
    )
    mocker.patch.object(
        test_service,
        "extract_lloyd_george_record_from_bulk_upload_file_name",
        return_value=("LG", bad_filename),
    )
    mocker.patch.object(
        test_service,
        "extract_patient_name_from_bulk_upload_file_name",
        return_value=("John Doe", bad_filename),
    )

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.validate_record_filename(bad_filename)

    assert str(exc_info.value) == "Incorrect NHS number or date format"


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        (
            "/M89002/10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            (
                "/M89002/",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            ),
        ),
        (
            "/2020 Prince of Whales 2/10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            (
                "/2020 Prince of Whales 2/",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            ),
        ),
        (
            "/2020 Prince of Whales 2/10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14/11/2000].pdf",
            (
                "/2020 Prince of Whales 2/",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14/11/2000].pdf",
            ),
        ),
        (
            "/2020of2024 Prince of Whales 2/2020 Prince of Whales 2/"
            "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14/11/2000].pdf",
            (
                "/2020of2024 Prince of Whales 2/2020 Prince of Whales 2/",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14/11/2000].pdf",
            ),
        ),
        (
            "/M89002/_10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14/11/2000].pdf",
            (
                "/M89002/",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14/11/2000].pdf",
            ),
        ),
        (
            "/10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            (
                "/",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            ),
        ),
        (
            "/_10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            (
                "/",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            ),
        ),
    ],
)
def test_extract_document_path(test_service, value, expected):
    actual = test_service.extract_document_path(value)
    assert actual == expected


def test_extract_document_path_with_no_document_path(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_document_path(invalid_data)

    assert str(exc_info.value) == "Incorrect document path format"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("1 of 02_Lloyd_George_Record", (1, 2, "_Lloyd_George_Record")),
        ("1of12_Lloyd_George_Record", (1, 12, "_Lloyd_George_Record")),
        ("!~/01!of 12_Lloyd_George_Record", (1, 12, "_Lloyd_George_Record")),
        ("X12of34YZ", (12, 34, "YZ")),
        ("8ab12of34YZ", (12, 34, "YZ")),
        ("8ab12of34YZ2442-ofladimus 900123", (12, 34, "YZ2442-ofladimus 900123")),
        ("1 of 02_Lloyd_George_Record", (1, 2, "_Lloyd_George_Record")),
        ("/9730786895/01 of 01_Lloyd_George_Record", (1, 1, "_Lloyd_George_Record")),
        (
            "test/nested/9730786895/01 of 01_Lloyd_George_Record",
            (1, 1, "_Lloyd_George_Record"),
        ),
    ],
)
def test_correctly_extract_document_number_from_bulk_upload_file_name(
    test_service, input, expected
):
    actual = test_service.extract_document_number_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_document_number_from_bulk_upload_file_name_with_no_document_number(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_document_number_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Incorrect document number format"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("_Lloyd_George_Record_person_name", ("Lloyd_George_Record", "_person_name")),
        ("_lloyd_george_record_person_name", ("Lloyd_George_Record", "_person_name")),
        ("_LLOYD_GEORGE_RECORD_person_name", ("Lloyd_George_Record", "_person_name")),
        (
            "_lloyd_george_record_lloyd_george_12342",
            ("Lloyd_George_Record", "_lloyd_george_12342"),
        ),
        (
            "]{\lloyd george?record///person_name",
            ("Lloyd_George_Record", "///person_name"),
        ),
        ("_Lloyd_George-Record_person_name", ("Lloyd_George_Record", "_person_name")),
        ("_Ll0yd_Ge0rge-21Rec0rd_person_name", ("Lloyd_George_Record", "_person_name")),
    ],
)
def test_correctly_extract_lloyd_george_record_from_bulk_upload_file_name(
    test_service, input, expected
):
    actual = test_service.extract_lloyd_george_record_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_lloyd_george_from_bulk_upload_file_name_with_no_lloyd_george(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_lloyd_george_record_from_bulk_upload_file_name(
            invalid_data
        )

    assert str(exc_info.value) == "Invalid Lloyd_George_Record separator"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("_John_doe-1231", ("John_doe", "-1231")),
        ("-José María-1231", ("José María", "-1231")),
        (
            "-Sir. Roger Guilbert the third-1231",
            ("Sir. Roger Guilbert the third", "-1231"),
        ),
        ("-José&María-Grandola&1231", ("José&María-Grandola", "&1231")),
        (
            "_Jim Stevens_9000000001_22.10.2010.txt",
            ("Jim Stevens", "_9000000001_22.10.2010.txt"),
        ),
        (
            'Dwain "The Rock" Johnson_9000000001_22.10.2010.txt',
            ('Dwain "The Rock" Johnson', "_9000000001_22.10.2010.txt"),
        ),
    ],
)
def test_correctly_extract_person_name_from_bulk_upload_file_name(
    test_service, input, expected
):
    actual = test_service.extract_patient_name_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_person_name_from_bulk_upload_file_name_with_no_person_name(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_patient_name_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid patient name"


@pytest.mark.parametrize(
    ["input", "expected", "expected_exception"],
    [
        ("_-9991211234-12012024", ("9991211234", "-12012024"), None),
        ("_-9-99/12?11\/234-12012024", ("9991211234", "-12012024"), None),
        ("_-9-9l9/12?11\/234-12012024", ("9991211234", "-12012024"), None),
        (
            "12_12_12_12_12_12_12_2024.csv",
            "incorrect NHS number format",
            InvalidFileNameException,
        ),
        ("_9000000001_11_12_2025.csv", ("9000000001", "_11_12_2025.csv"), None),
        ("_900000000111_12_2025.csv", ("9000000001", "11_12_2025.csv"), None),
    ],
)
def test_correctly_extract_nhs_number_from_bulk_upload_file_name(
    test_service, input, expected, expected_exception
):
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            test_service.extract_nhs_number_from_bulk_upload_file_name(input)
            assert str(exc_info.value) == expected
    else:
        actual = test_service.extract_nhs_number_from_bulk_upload_file_name(input)
        assert actual == expected


def test_extract_nhs_number_from_bulk_upload_file_name_with_nhs_number(test_service):
    invalid_data = "invalid_nhs_number.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_nhs_number_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid NHS number"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("-12012024.txt", ("12", "01", "2024", ".txt")),
        ("-12.01.2024.csv", ("12", "01", "2024", ".csv")),
        ("-12-01-2024.txt", ("12", "01", "2024", ".txt")),
        ("-12-01-2024.txt", ("12", "01", "2024", ".txt")),
        ("-01-01-2024.txt", ("01", "01", "2024", ".txt")),
        ("_13-12-2023.pdf", ("13", "12", "2023", ".pdf")),
        ("_13.12.2023.pdf", ("13", "12", "2023", ".pdf")),
        ("_13/12/2023.pdf", ("13", "12", "2023", ".pdf")),
    ],
)
def test_correctly_extract_date_from_bulk_upload_file_name(
    test_service, input, expected
):
    actual = test_service.extract_date_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_data_from_bulk_upload_file_name_with_incorrect_date_format(
    test_service,
):
    invalid_data = "_12-13-2024.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_date_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid date format"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        (".txt", ".txt"),
        ("cool_stuff.txt", ".txt"),
        ("{}.[].txt", ".txt"),
        (".csv", ".csv"),
    ],
)
def test_correctly_extract_file_extension_from_bulk_upload_file_name(
    test_service, input, expected
):
    actual = test_service.extract_file_extension_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_file_extension_from_bulk_upload_file_name_with_incorrect_file_extension_format(
    test_service,
):
    invalid_data = "txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_file_extension_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid file extension"


def test_correctly_assembles_valid_file_name(test_service):
    file_path_prefix = "/amazing-directory/"
    first_document_number = 1
    second_document_number = 2
    lloyd_george_record = "Lloyd_George_Record"
    person_name = "Jim-Stevens"
    nhs_number = "9000000001"
    day = "22"
    month = "10"
    year = "2010"
    file_extension = ".txt"

    expected = "/amazing-directory/1of2_Lloyd_George_Record_[Jim-Stevens]_[9000000001]_[22-10-2010].txt"
    actual = test_service.assemble_valid_file_name(
        file_path_prefix,
        first_document_number,
        second_document_number,
        lloyd_george_record,
        person_name,
        nhs_number,
        day,
        month,
        year,
        file_extension,
    )
    assert actual == expected


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
    metadata_service,
    mock_download_metadata_from_s3,
):
    fake_csv_path = "fake/path/metadata.csv"
    fake_uuid = "123412342"

    mock_download_metadata_from_s3.return_value = fake_csv_path

    mocker.patch.object(
        metadata_service.s3_service, "copy_across_bucket", return_value=None
    )
    mocker.patch.object(metadata_service.s3_service, "delete_object", return_value=None)

    mocker.patch("uuid.uuid4", return_value=fake_uuid)

    fake_metadata = [
        {"nhs_number": "1234567890", "some_data": "value1"},
        {"nhs_number": "123456789", "some_data": "value2"},
        {"nhs_number": "0000000000", "some_data": "value3"},
    ]
    mocker.patch.object(
        metadata_service, "csv_to_staging_metadata", return_value=fake_metadata
    )

    mocked_send_metadata = mocker.patch.object(
        metadata_service, "send_metadata_to_fifo_sqs"
    )

    metadata_service.process_metadata()

    assert mocked_send_metadata.call_count == 1
    mocked_send_metadata.assert_called_once_with(fake_metadata)


def test_process_metadata_catch_and_log_error_when_fail_to_get_metadata_csv_from_s3(
    set_env,
    caplog,
    mock_s3_service,
    mock_sqs_service,
    metadata_service,
):
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}},
        "S3:HeadObject",
    )
    expected_err_msg = 'No metadata file could be found with the name "metadata.csv"'

    with pytest.raises(BulkUploadMetadataException) as e:
        metadata_service.process_metadata()

    assert expected_err_msg in str(e.value)
    assert caplog.records[-1].msg == expected_err_msg
    assert caplog.records[-1].levelname == "ERROR"

    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_validation_error_when_metadata_csv_is_invalid(
    mock_sqs_service,
    mock_download_metadata_from_s3,
    metadata_service,
    mocker,
):
    mock_download_metadata_from_s3.return_value = "fake/path.csv"

    mocker.patch.object(
        metadata_service,
        "csv_to_staging_metadata",
        side_effect=BulkUploadMetadataException("validation error"),
    )

    with pytest.raises(BulkUploadMetadataException) as exc_info:
        metadata_service.process_metadata()

    assert "validation error" in str(exc_info.value)
    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_validation_error_when_gp_practice_code_is_missing(
    caplog,
    mock_sqs_service,
    mock_download_metadata_from_s3,
    metadata_service,
    mocker,
):
    mock_download_metadata_from_s3.return_value = "fake/path.csv"

    expected_error_log = (
        "Failed to parse metadata.csv: 1 validation error for MetadataFile\n"
        + "GP-PRACTICE-CODE\n  missing GP-PRACTICE-CODE for patient 1234567890"
    )

    mocker.patch.object(
        metadata_service,
        "csv_to_staging_metadata",
        side_effect=BulkUploadMetadataException(expected_error_log),
    )

    with pytest.raises(BulkUploadMetadataException) as e:
        metadata_service.process_metadata()

    assert expected_error_log in str(e.value)

    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_not_called()


def test_process_metadata_raise_client_error_when_failed_to_send_message_to_sqs(
    metadata_service,
    mocker,
):
    mocker.patch.object(
        metadata_service, "download_metadata_from_s3", return_value="fake/path.csv"
    )

    dummy_staging_metadata = mocker.Mock()
    dummy_staging_metadata.nhs_number = "1234567890"
    mocker.patch.object(
        metadata_service,
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
        metadata_service,
        "send_metadata_to_fifo_sqs",
        side_effect=BulkUploadMetadataException(str(mock_client_error)),
    )

    expected_err_msg = (
        "An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the SendMessage operation:"
        " The specified queue does not exist"
    )

    with pytest.raises(BulkUploadMetadataException) as e:
        metadata_service.process_metadata()

    assert expected_err_msg in str(e.value)


def test_download_metadata_from_s3(mock_s3_service, metadata_service):
    result = metadata_service.download_metadata_from_s3()

    expected_download_path = os.path.join(
        metadata_service.temp_download_dir, METADATA_FILENAME
    )
    expected_file_key = f"{metadata_service.practice_directory}/{METADATA_FILENAME}"

    mock_s3_service.download_file.assert_called_once_with(
        s3_bucket_name=metadata_service.staging_bucket_name,
        file_key=expected_file_key,
        download_path=expected_download_path,
    )

    assert result == expected_download_path


def test_download_metadata_from_s3_raise_error_when_failed_to_download(
    set_env, mock_s3_service, mock_tempfile, metadata_service
):
    mock_s3_service.download_file.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "file not exist in bucket"}},
        "s3_get_object",
    )

    with pytest.raises(ClientError):
        metadata_service.download_metadata_from_s3()


def test_duplicates_csv_to_staging_metadata(mocker, metadata_service):
    fake_csv_data = textwrap.dedent(
        """\
            FILEPATH,PAGE COUNT,GP-PRACTICE-CODE,NHS-NO,SECTION,SUB-SECTION,SCAN-DATE,SCAN-ID,USER-ID,UPLOAD
            /1234567890/1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y12345","1234567890",
            "LG","","03/09/2022","NEC","NEC","04/10/2023"
            /1234567890/2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y12345","1234567890",
            "LG","","03/09/2022","NEC","NEC","04/10/2023"
            /1234567890/1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y6789","1234567890",
            "LG","","03/09/2022","NEC","NEC","04/10/2023"
            /1234567890/2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf,"","Y6789","1234567890",
            "LG","","03/09/2022","NEC","NEC","04/10/2023"
            1of1_Lloyd_George_Record_[Joe Bloggs_invalid]_[123456789]_[25-12-2019].txt,"","Y12345","123456789",
            "LG","","04/09/2022","NEC","NEC","04/10/2023"
            1of1_Lloyd_George_Record_[Joe Bloggs_invalid]_[123456789]_[25-12-2019].txt,"","Y6789","123456789",
            "LG","","04/09/2022","NEC","NEC","04/10/2023"
            1of1_Lloyd_George_Record_[Jane Smith]_[1234567892]_[25-12-2019].txt,"","Y12345","",
            "LG","","04/09/2022","NEC","NEC","04/10/2023"
            1of1_Lloyd_George_Record_[Jane Smith]_[1234567892]_[25-12-2019].txt,"","Y6789","",
            "LG","","04/09/2022","NEC","NEC","04/10/2023"
        """
    )

    mocker.patch("builtins.open", mocker.mock_open(read_data=fake_csv_data))
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch.object(
        metadata_service, "validate_record_filename", side_effect=lambda x: x
    )

    actual = metadata_service.csv_to_staging_metadata("fake/path.csv")
    expected = EXPECTED_PARSED_METADATA_2
    assert actual == expected


def test_send_metadata_to_sqs(set_env, mocker, mock_sqs_service, metadata_service):
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

    metadata_service.send_metadata_to_fifo_sqs(MOCK_METADATA)

    mock_sqs_service.send_message_with_nhs_number_attr_fifo.assert_has_calls(
        expected_calls
    )
    assert mock_sqs_service.send_message_with_nhs_number_attr_fifo.call_count == 2


def test_send_metadata_to_sqs_raise_error_when_fail_to_send_message(
    set_env, mock_sqs_service, metadata_service
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
        metadata_service.send_metadata_to_fifo_sqs(EXPECTED_PARSED_METADATA)


def test_clear_temp_storage(set_env, mocker, mock_tempfile, metadata_service):
    mocked_rm = mocker.patch("shutil.rmtree")

    metadata_service.clear_temp_storage()

    mocked_rm.assert_called_once_with(metadata_service.temp_download_dir)
