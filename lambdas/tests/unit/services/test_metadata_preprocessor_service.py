import os

import pytest
from freezegun import freeze_time
from msgpack.fallback import BytesIO
from services.bulk_upload_metadata_preprocessor_service import (
    MetadataPreprocessorService,
)
from tests.unit.conftest import MOCK_STAGING_STORE_BUCKET, TEST_BASE_DIRECTORY
from utils.exceptions import InvalidFileNameException

from lambdas.models.staging_metadata import METADATA_FILENAME


@pytest.fixture
@freeze_time("2025-01-01T12:00:00")
def test_service(mocker, set_env):
    service = MetadataPreprocessorService(practice_directory="test_practice_directory")
    mocker.patch.object(service, "s3_service")
    return service


@pytest.fixture
def mock_get_metadata_rows_from_file(mocker, test_service):
    return mocker.patch.object(test_service, "get_metadata_rows_from_file")


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
def mock_validate_record_filename(mocker, test_service):
    def _mock_validate(filename):
        if filename == "invalid_file.csv":
            raise InvalidFileNameException("Invalid filename")
        return f"updated_{filename}"

    return mocker.patch.object(
        test_service,
        "validate_record_filename",
        side_effect=_mock_validate,
    )


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


def test_validate_and_update_file_name_returns_a_valid_file_path(test_service):
    wrong_file_path = (
        "01 of 02_Lloyd_George_Record_Jim Stevens_9000000001_22.10.2010.txt"
    )
    expected_file_path = (
        "1of2_Lloyd_George_Record_[Jim Stevens]_[9000000001]_[22-10-2010].txt"
    )

    actual = test_service.validate_record_filename(wrong_file_path)

    assert actual == expected_file_path


def test_correctly_extract_document_number_from_bulk_upload_file_name(test_service):
    # paths, expected_results
    test_cases = [
        ("1 of 02_Lloyd_George_Record", (1, 2, "_Lloyd_George_Record")),
        ("1of12_Lloyd_George_Record", (1, 12, "_Lloyd_George_Record")),
        ("!~/01!of 12_Lloyd_George_Record", (1, 12, "_Lloyd_George_Record")),
        ("X12of34YZ", (12, 34, "YZ")),
        ("8ab12of34YZ", (12, 34, "YZ")),
        ("8ab12of34YZ2442-ofladimus 900123", (12, 34, "YZ2442-ofladimus 900123")),
    ]

    for input_str, expected in test_cases:
        actual = test_service.extract_document_number_bulk_upload_file_name(input_str)
        assert actual == expected


def test_extract_document_number_from_bulk_upload_file_name_with_no_document_number(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_document_number_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect document number format"


def test_correctly_extract_Lloyd_George_Record_from_bulk_upload_file_name(
    test_service,
):
    test_cases = [
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
    ]

    for input_str, expected in test_cases:
        actual = test_service.extract_lloyd_george_record_from_bulk_upload_file_name(
            input_str
        )
        assert actual == expected


def test_extract_Lloyd_george_from_bulk_upload_file_name_with_no_Lloyd_george(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_lloyd_george_record_from_bulk_upload_file_name(
            invalid_data
        )

    assert str(exc_info.value) == "incorrect Lloyd George Record format"


def test_correctly_extract_person_name_from_bulk_upload_file_name(test_service):
    test_cases = [
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
    ]

    for input_str, expected in test_cases:
        actual = test_service.extract_person_name_from_bulk_upload_file_name(input_str)
        assert actual == expected


def test_extract_person_name_from_bulk_upload_file_name_with_no_person_name(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_person_name_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect person name format"


def test_correctly_extract_nhs_number_from_bulk_upload_file_name(test_service):
    # paths, expected_results
    test_cases = [
        ("_-9991211234-12012024", ("9991211234", "-12012024")),
        ("_-9-99/12?11\/234-12012024", ("9991211234", "-12012024")),
        ("_-9-9l9/12?11\/234-12012024", ("9991211234", "-12012024")),
    ]

    for input_str, expected in test_cases:
        actual = test_service.extract_nhs_number_from_bulk_upload_file_name(input_str)
        assert actual == expected


def test_extract_nhs_number_from_bulk_upload_file_name_with_nhs_number(test_service):
    invalid_data = "invalid_nhs_number.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_nhs_number_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect NHS number format"


def test_correctly_extract_date_from_bulk_upload_file_name(test_service):
    test_cases = [
        ("-12012024.txt", ("12", "01", "2024", ".txt")),
        ("-12.01.2024.csv", ("12", "01", "2024", ".csv")),
        ("-12-01-2024.txt", ("12", "01", "2024", ".txt")),
        ("-12-1-2024.txt", ("12", "01", "2024", ".txt")),
        ("-1-01-2024.txt", ("01", "01", "2024", ".txt")),
        ("-1-01-24.txt", ("01", "01", "2024", ".txt")),
    ]

    for input_str, expected in test_cases:
        actual = test_service.extract_date_from_bulk_upload_file_name(input_str)
        assert actual == expected


def test_extract_data_from_bulk_upload_file_name_with_incorrect_date_format(
    test_service,
):
    invalid_data = "12-july-2024.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_date_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect date format"


def test_correctly_extract_file_extension_from_bulk_upload_file_name(test_service):
    test_cases = [
        (".txt", ".txt"),
        ("cool_stuff.txt", ".txt"),
        ("{}.[].txt", ".txt"),
        (".csv", ".csv"),
    ]

    for input_str, expected in test_cases:
        actual = test_service.extract_file_extension_from_bulk_upload_file_name(
            input_str
        )
        assert actual == expected


def test_extract_file_extension_from_bulk_upload_file_name_with_incorrect_file_extension_format(
    test_service,
):
    invalid_data = "txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_file_extension_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect file extension format"


def test_correctly_assembles_valid_file_name(test_service):
    first_document_number = 1
    second_document_number = 2
    lloyd_george_record = "Lloyd_George_Record"
    person_name = "Jim-Stevens"
    nhs_number = "9000000001"
    day = "22"
    month = "10"
    year = "2010"
    file_extension = ".txt"

    expected = "1of2_Lloyd_George_Record_[Jim-Stevens]_[9000000001]_[22-10-2010].txt"
    actual = test_service.assemble_valid_file_name(
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


def test_process_metadata_file_exists(test_service, mock_metadata_file_get_object):
    test_preprocessed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/unprocessed",
        f"unprocessed_{METADATA_FILENAME}",
    )

    test_service.s3_service.file_exist_on_s3.return_value = True
    test_service.s3_service.client.get_object.side_effect = (
        lambda Bucket, Key: mock_metadata_file_get_object(
            test_preprocessed_metadata_file, Bucket, Key
        )
    )

    test_service.process_metadata()


def test_get_metadata_csv_from_file(test_service, mock_metadata_file_get_object):
    test_preprocessed_metadata_file = os.path.join(
        TEST_BASE_DIRECTORY,
        "helpers/data/bulk_upload/unprocessed",
        f"unprocessed_{METADATA_FILENAME}",
    )

    test_service.s3_service.file_exist_on_s3.return_value = True
    test_service.s3_service.client.get_object.side_effect = (
        lambda Bucket, Key: mock_metadata_file_get_object(
            test_preprocessed_metadata_file, Bucket, Key
        )
    )
    test_service.process_metadata()

    test_service.get_metadata_rows_from_file(
        file_key=f"{test_service.practice_directory}/{METADATA_FILENAME}",
        bucket_name=MOCK_STAGING_STORE_BUCKET,
    )


def test_move_original_metadata_file(test_service):
    file_key = "input/unprocessed/metadata.csv"
    expected_destination_key = (
        f"{test_service.practice_directory}"
        f"/{test_service.processed_folder_name}/{test_service.processed_date}/{METADATA_FILENAME}"
    )

    # Act
    test_service.move_original_metadata_file(file_key)

    # Assert
    test_service.s3_service.copy_across_bucket.assert_called_once_with(
        MOCK_STAGING_STORE_BUCKET,
        file_key,
        MOCK_STAGING_STORE_BUCKET,
        expected_destination_key,
    )


def test_update_file_name(mocker, test_service):
    original_file_name = "old_file.csv"
    new_file_name = "new_file.csv"
    original_file_key = f"{test_service.practice_directory}/{original_file_name}"
    new_file_key = f"{test_service.practice_directory}/{new_file_name}"
    test_service.staging_store_bucket = MOCK_STAGING_STORE_BUCKET

    # Mock that the original file exists
    test_service.s3_service.file_exist_on_s3.return_value = True
    mock_copy = mocker.patch.object(test_service.s3_service.client, "copy_object")
    mock_delete = mocker.patch.object(test_service.s3_service.client, "delete_object")

    # Act
    test_service.update_record_filename(original_file_name, new_file_name)

    # Assert
    mock_copy.assert_called_once_with(
        Bucket=MOCK_STAGING_STORE_BUCKET,
        CopySource={"Bucket": MOCK_STAGING_STORE_BUCKET, "Key": original_file_key},
        Key=new_file_key,
    )
    mock_delete.assert_called_once_with(
        Bucket=MOCK_STAGING_STORE_BUCKET,
        Key=original_file_key,
    )


def test_update_file_name_file_not_found(test_service, mocker):
    test_service.staging_store_bucket = MOCK_STAGING_STORE_BUCKET
    mocker.patch.object(test_service.s3_service, "file_exist_on_s3", return_value=False)

    test_service.s3_service.client.copy_object.assert_not_called()
    test_service.s3_service.client.delete_object.assert_not_called()


def test_convert_csv_dictionary_to_bytes(test_service, mocker):
    # Arrange
    headers = ["id", "name", "age"]
    metadata_csv_data = [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
    ]

    # Act
    result_bytes = test_service.convert_csv_dictionary_to_bytes(
        headers=headers, metadata_csv_data=metadata_csv_data, encoding="utf-8"
    )

    # Assert
    result_str = result_bytes.decode("utf-8")
    expected_output = "id,name,age\r\n1,Alice,30\r\n2,Bob,25\r\n"

    assert result_str == expected_output


def test_update_and_standardize_filenames_success_and_failure(test_service, mocker):
    # Arrange
    input_data = [
        {"FILEPATH": "valid_file_1.csv"},
        {"FILEPATH": "invalid_file.csv"},
        {"FILEPATH": "valid_file_2.csv"},
    ]

    # Define side effects for validate_and_update_file_name
    def mock_validate_record_filename(filename):
        if filename == "invalid_file.csv":
            raise InvalidFileNameException("Invalid filename")
        return f"updated_{filename}"

    # Patch dependent methods
    mocker.patch.object(
        test_service,
        "validate_record_filename",
        side_effect=mock_validate_record_filename,
    )
    mock_update_file_name = mocker.patch.object(test_service, "update_record_filename")

    # Act
    updated_metadata_rows, rejected_rows, error_list = (
        test_service.standardize_filenames(input_data)
    )

    # Assert
    assert updated_metadata_rows == [
        {"FILEPATH": "updated_valid_file_1.csv"},  # Not updated due to exception
        {"FILEPATH": "updated_valid_file_2.csv"},
    ]
    assert rejected_rows == [{"FILEPATH": "invalid_file.csv"}]
    assert error_list == [{"invalid_file.csv", "Invalid filename"}]
    assert mock_update_file_name.call_count == 2
    mock_update_file_name.assert_any_call(
        "valid_file_1.csv", "updated_valid_file_1.csv"
    )
    mock_update_file_name.assert_any_call(
        "valid_file_2.csv", "updated_valid_file_2.csv"
    )


def test_process_row_valid_filename(
    test_service, sample_metadata_row, mock_validate_record_filename, mocker
):
    # Arrange
    filename = sample_metadata_row["FILEPATH"]
    updated_filename = "updated_" + filename
    mock_update = mocker.patch.object(test_service, "update_record_filename")
    # Act
    success, updated_row, error = test_service.process_metadata_row(sample_metadata_row)
    # Assert
    assert success is True
    assert updated_row["FILEPATH"] == updated_filename
    assert error is None
    mock_update.assert_called_once_with(filename, updated_filename)
