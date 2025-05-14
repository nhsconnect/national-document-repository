import csv
import os
from unittest.mock import call

import pytest
from botocore.exceptions import ClientError
from freezegun import freeze_time
from msgpack.fallback import BytesIO
from services.bulk_upload_metadata_preprocessor_service import (
    MetadataPreprocessorService,
)
from tests.unit.conftest import MOCK_STAGING_STORE_BUCKET, TEST_BASE_DIRECTORY
from utils.exceptions import InvalidFileNameException, MetadataPreprocessingException

from lambdas.models.staging_metadata import METADATA_FILENAME


@pytest.fixture(autouse=True)
@freeze_time("2025-01-01T12:00:00")
def test_service(mocker, set_env):
    service = MetadataPreprocessorService(practice_directory="test_practice_directory")
    mocker.patch.object(service, "s3_service")
    return service


@pytest.fixture
def mock_get_metadata_rows_from_file(mocker, test_service):
    return mocker.patch.object(test_service, "get_metadata_rows_from_file")


@pytest.fixture
def mock_generate_and_save_csv_file(mocker, test_service):
    return mocker.patch.object(test_service, "generate_and_save_csv_file")


@pytest.fixture
def sample_metadata_row():
    return {
        "FILEPATH": "01 of 02_Lloyd_George_Record_[Dwayne Basil COWIE]_[9730787506]_[18-09-1974].pdf",
        "GP-PRACTICE-CODE": "M85143",
        "NHS-NO": "9730787506",
        "PAGE COUNT": "1",
        "SCAN-DATE": "03/09/2022",
        "SCAN-ID": "NEC",
        "SECTION": "LG",
        "SUB-SECTION": "",
        "UPLOAD": "04/10/2023",
        "USER-ID": "NEC",
    }


@pytest.fixture
def mock_metadata_file_get_object():
    def _mock_metadata_file_get_object(
        test_file_path: str,
        Bucket: str,
        Key: str,
    ):
        with open(test_file_path, "rb") as file:
            test_file_data = file.read()

        return {"Body": BytesIO(test_file_data)}

    return _mock_metadata_file_get_object


@pytest.fixture
def mock_update_date_in_row(mocker, test_service):
    return mocker.patch.object(
        test_service,
        "update_date_in_row",
        side_effect=lambda original_date: original_date,
    )


@pytest.fixture
def mock_valid_record_filename(mocker, test_service):
    return mocker.patch.object(
        test_service,
        "validate_record_filename",
        side_effect=lambda original_filename: original_filename,
    )


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
        "extract_person_name_from_bulk_upload_file_name",
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
        "extract_person_name_from_bulk_upload_file_name",
        return_value=("John Doe", bad_filename),
    )

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.validate_record_filename(bad_filename)

    assert str(exc_info.value) == "incorrect NHS number or date format"


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

    assert str(exc_info.value) == "Incorrect document number format"


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
    actual = test_service.extract_person_name_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_person_name_from_bulk_upload_file_name_with_no_person_name(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_person_name_from_bulk_upload_file_name(invalid_data)

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


@freeze_time("2025-01-01T12:00:00")
def test_process_metadata_file_exists(
    test_service, mock_metadata_file_get_object, mock_generate_and_save_csv_file
):
    test_processed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        f"{METADATA_FILENAME}",
    )

    test_rejections_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        "rejected.csv",
    )

    with open(test_processed_metadata_file, "rb") as file:
        test_file_data = file.read()
    expected_metadata_bytes = test_file_data

    with open(test_rejections_file, "rb") as file:
        test_file_data = file.read()
    expected_rejected_bytes = test_file_data

    test_preprocessed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        f"preprocessed_{METADATA_FILENAME}",
    )

    test_service.s3_service.file_exist_on_s3.return_value = True
    test_service.s3_service.client.get_object.side_effect = (
        lambda Bucket, Key: mock_metadata_file_get_object(
            test_preprocessed_metadata_file, Bucket, Key
        )
    )

    test_service.process_metadata()

    expected_updated_rows = list(
        csv.DictReader(expected_metadata_bytes.decode("utf-8-sig").splitlines())
    )
    expected_rejected_reasons = list(
        csv.DictReader(expected_rejected_bytes.decode("utf-8-sig").splitlines())
    )

    expected_calls = [
        call(
            csv_dict=expected_updated_rows,
            file_key=f"test_practice_directory/{METADATA_FILENAME}",
        ),
        call(
            csv_dict=expected_rejected_reasons,
            file_key="test_practice_directory/processed/2025-01-01 12:00/rejections.csv",
        ),
    ]

    mock_generate_and_save_csv_file.assert_has_calls(expected_calls, any_order=True)


def test_process_metadata_success(test_service, mocker):
    get_metadata_mock = mocker.patch.object(
        test_service,
        "get_metadata_rows_from_file",
        return_value=[{"FILEPATH": "file1.pdf"}],
    )
    generate_map_mock = mocker.patch.object(
        test_service,
        "generate_renaming_map",
        return_value=(
            [({"FILEPATH": "file1.pdf"}, {"FILEPATH": "new_file1.pdf"})],
            [{"FILEPATH": "bad_file.pdf"}],
            [{"REASON": "invalid"}],
        ),
    )
    standardize_mock = mocker.patch.object(
        test_service,
        "standardize_filenames",
        return_value=[{"FILEPATH": "new_file1.pdf"}],
    )
    move_file_mock = mocker.patch.object(
        test_service, "move_original_metadata_file", return_value=True
    )
    delete_mock = mocker.patch.object(test_service.s3_service, "delete_object")
    generate_csv_mock = mocker.patch.object(test_service, "generate_and_save_csv_file")

    test_service.process_metadata()

    assert get_metadata_mock.called
    assert generate_map_mock.called
    assert standardize_mock.called
    assert move_file_mock.called
    assert delete_mock.called
    assert generate_csv_mock.called


def test_get_metadata_csv_from_file_metadata_exists(
    test_service, mock_metadata_file_get_object
):
    test_preprocessed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/preprocessed",
        f"preprocessed_{METADATA_FILENAME}",
    )
    test_file_key = f"{test_service.practice_directory}/{METADATA_FILENAME}"

    test_service.s3_service.file_exist_on_s3.return_value = True
    test_service.s3_service.client.get_object.side_effect = (
        lambda Bucket, Key: mock_metadata_file_get_object(
            test_preprocessed_metadata_file, Bucket, Key
        )
    )

    test_service.get_metadata_rows_from_file(
        file_key=test_file_key,
        bucket_name=MOCK_STAGING_STORE_BUCKET,
    )

    test_service.s3_service.file_exist_on_s3.assert_called_once_with(
        s3_bucket_name=MOCK_STAGING_STORE_BUCKET, file_key=test_file_key
    )
    test_service.s3_service.client.get_object.assert_called_once_with(
        Bucket=MOCK_STAGING_STORE_BUCKET, Key=test_file_key
    )


def test_get_metadata_csv_from_file_metadata_does_not_exist(test_service, caplog):
    test_file_key = f"{test_service.practice_directory}/{METADATA_FILENAME}"

    test_service.s3_service.file_exist_on_s3.return_value = False

    with pytest.raises(MetadataPreprocessingException) as exc_info:
        test_service.get_metadata_rows_from_file(
            file_key=test_file_key,
            bucket_name=MOCK_STAGING_STORE_BUCKET,
        )
    expected_log = f"File {test_file_key} doesn't exist"
    actual_log = caplog.records[-1].msg
    assert expected_log == actual_log
    assert str(exc_info.value) == "Failed to retrieve metadata"

    test_service.s3_service.file_exist_on_s3.assert_called_once_with(
        s3_bucket_name=MOCK_STAGING_STORE_BUCKET, file_key=test_file_key
    )
    test_service.s3_service.client.get_object.assert_not_called()


def test_move_original_metadata_file(test_service):
    file_key = "input/preprocessed/metadata.csv"
    expected_destination_key = (
        f"{test_service.practice_directory}"
        f"/{test_service.processed_folder_name}/{test_service.processed_date}/{METADATA_FILENAME}"
    )

    test_service.move_original_metadata_file(file_key)

    test_service.s3_service.copy_across_bucket.assert_called_once_with(
        MOCK_STAGING_STORE_BUCKET,
        file_key,
        MOCK_STAGING_STORE_BUCKET,
        expected_destination_key,
    )


def test_move_original_metadata_file_handles_exception(test_service):
    file_key = "input/preprocessed/metadata.csv"

    error_response = {"Error": {"Code": "NoSuchKey", "Message": "File not found"}}
    operation_name = "CopyObject"

    test_service.s3_service.copy_across_bucket.side_effect = ClientError(
        error_response, operation_name
    )

    result = test_service.move_original_metadata_file(file_key)

    assert result is False
    test_service.s3_service.copy_across_bucket.assert_called_once()


def test_update_record_filename(test_service, mocker):
    original_row = {"FILEPATH": "/old/path/file1.pdf"}
    updated_row = {"FILEPATH": "/test_practice_directory/new/path/file1.pdf"}

    mock_client = mocker.Mock()
    test_service.s3_service.client = mock_client

    result = test_service.update_record_filename(original_row, updated_row)

    mock_client.copy_object.assert_called_once_with(
        Bucket=MOCK_STAGING_STORE_BUCKET,
        CopySource={
            "Bucket": MOCK_STAGING_STORE_BUCKET,
            "Key": "test_practice_directory/old/path/file1.pdf",
        },
        Key="test_practice_directory/new/path/file1.pdf",
        MetadataDirective="COPY",
        TaggingDirective="COPY",
    )

    mock_client.delete_object.assert_called_once_with(
        Bucket=MOCK_STAGING_STORE_BUCKET,
        Key="test_practice_directory/old/path/file1.pdf",
    )

    assert result == updated_row


def test_update_record_filename_exception(test_service, mocker):
    original_row = {"FILEPATH": "/old/path/file1.pdf"}
    updated_row = {"FILEPATH": "/test_practice_directory/new/path/file1.pdf"}

    mock_client = mocker.Mock()
    test_service.s3_service.client = mock_client

    error_response = {"Error": {"Code": "NoSuchKey", "Message": "File not found"}}
    operation_name = "CopyObject"

    mock_client.copy_object.side_effect = ClientError(error_response, operation_name)

    result = test_service.update_record_filename(original_row, updated_row)

    assert result is None
    mock_client.copy_object.assert_called_once()
    mock_client.delete_object.assert_not_called()


def test_update_file_name_file_not_found(test_service, mocker):
    test_service.staging_store_bucket = MOCK_STAGING_STORE_BUCKET
    mocker.patch.object(test_service.s3_service, "file_exist_on_s3", return_value=False)

    test_service.s3_service.client.copy_object.assert_not_called()
    test_service.s3_service.client.delete_object.assert_not_called()


def test_update_and_standardize_filenames_success_and_failure(test_service, mocker):
    original_row1 = {"FILEPATH": "/path/original1.pdf"}
    updated_row1 = {"FILEPATH": "/path/updated1.pdf"}

    original_row2 = {"FILEPATH": "/path/original2.pdf"}
    updated_row2 = {"FILEPATH": "/path/updated2.pdf"}

    renaming_map = [(original_row1, updated_row1), (original_row2, updated_row2)]

    mock_update = mocker.patch.object(
        test_service,
        "update_record_filename",
        side_effect=lambda orig, upd: upd,  # Return the updated row
    )

    result = test_service.standardize_filenames(renaming_map)

    assert result == [updated_row1, updated_row2]
    assert mock_update.call_count == 2
    mock_update.assert_any_call(original_row1, updated_row1)
    mock_update.assert_any_call(original_row2, updated_row2)


def test_generate_renaming_map(test_service, mocker, mock_valid_record_filename):
    metadata_rows = [
        {"FILEPATH": "file1.pdf", "SCAN-DATE": "01/01/2000", "UPLOAD": "10/10/2010"},
        {"FILEPATH": "file2.pdf", "SCAN-DATE": "01/01/2000", "UPLOAD": "10/10/2010"},
    ]

    renaming_map, rejected_rows, rejected_reasons = test_service.generate_renaming_map(
        metadata_rows
    )

    assert renaming_map == [
        (
            metadata_rows[0],
            {
                "FILEPATH": "test_practice_directory/file1.pdf",
                "SCAN-DATE": "01/01/2000",
                "UPLOAD": "10/10/2010",
            },
        ),
        (
            metadata_rows[1],
            {
                "FILEPATH": "test_practice_directory/file2.pdf",
                "SCAN-DATE": "01/01/2000",
                "UPLOAD": "10/10/2010",
            },
        ),
    ]
    assert rejected_rows == []
    assert rejected_reasons == []
    assert mock_valid_record_filename.call_count == 2


def test_generate_renaming_map_happy_path(
    test_service, mock_update_date_in_row, mock_valid_record_filename
):
    row = {"FILEPATH": "valid_file.pdf"}

    metadata = [row]
    renaming_map, rejected_rows, rejected_reasons = test_service.generate_renaming_map(
        metadata
    )

    assert len(renaming_map) == 1
    assert renaming_map[0][0] == row
    assert (
        renaming_map[0][1]["FILEPATH"]
        == f"{test_service.practice_directory}/valid_file.pdf"
    )
    assert rejected_rows == []
    assert rejected_reasons == []


def test_generate_renaming_map_duplicate_file(
    test_service, mock_update_date_in_row, mock_valid_record_filename
):
    row1 = {"FILEPATH": "dup.pdf"}
    row2 = {"FILEPATH": "dup.pdf"}

    metadata = [row1, row2]
    renaming_map, rejected_rows, rejected_reasons = test_service.generate_renaming_map(
        metadata
    )

    assert len(renaming_map) == 1
    assert len(rejected_rows) == 1
    assert rejected_rows[0] == row2
    assert rejected_reasons[0]["REASON"] == "Duplicate filename after renaming"


def test_generate_renaming_map_invalid_filename(
    mocker, test_service, mock_update_date_in_row
):
    row = {"FILEPATH": "invalid_file.pdf"}

    mocker.patch.object(
        test_service,
        "validate_record_filename",
        side_effect=InvalidFileNameException("Bad format"),
    )

    metadata = [row]
    renaming_map, rejected_rows, rejected_reasons = test_service.generate_renaming_map(
        metadata
    )

    assert renaming_map == []
    assert rejected_rows == [row]
    assert rejected_reasons[0]["REASON"], "Bad format"


def test_generate_renaming_map_skips_empty_row(test_service):
    metadata = [{}]  # One empty dict
    renaming_map, rejected_rows, rejected_reasons = test_service.generate_renaming_map(
        metadata
    )

    assert renaming_map == []
    assert rejected_rows == []
    assert rejected_reasons == []


def test_update_date_in_row(test_service):
    metadata_row = {"SCAN-DATE": "2025.01.01", "UPLOAD": "2025.01.01"}

    updated_row = test_service.update_date_in_row(metadata_row)

    assert updated_row["SCAN-DATE"] == "2025/01/01"
    assert updated_row["UPLOAD"] == "2025/01/01"


def test_generate_and_save_csv_file_updated_metadata(test_service, mocker):
    csv_dict = [
        {
            "FILEPATH": "01 of 02_Lloyd_George_Record_[Dwayne Basil COWIE]_[9730787506]_[18-09-1974].pdf",
            "GP-PRACTICE-CODE": "M85143",
        }
    ]
    file_key = "path/to/file.csv"
    expected_csv_data = b"col1,col2\nvalue1,value2\nvalue3,value4\n"
    mock_convert_csv = mocker.patch(
        "services.bulk_upload_metadata_preprocessor_service.convert_csv_dictionary_to_bytes",
        return_value=expected_csv_data,
    )

    mock_save_or_create_file = mocker.patch.object(
        test_service.s3_service, "save_or_create_file"
    )

    test_service.generate_and_save_csv_file(csv_dict, file_key)

    mock_convert_csv.assert_called_once_with(csv_dict[0].keys(), csv_dict)
    mock_save_or_create_file.assert_called_once()
