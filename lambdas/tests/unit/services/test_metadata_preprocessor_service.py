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
        "/M89002/01 of 02_Lloyd_George_Record_Jim Stevens_9000000001_22.10.2010.txt"
    )
    expected_file_path = (
        "/M89002/1of2_Lloyd_George_Record_[Jim Stevens]_[9000000001]_[22-10-2010].txt"
    )

    actual = test_service.validate_record_filename(wrong_file_path)

    assert actual == expected_file_path


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
    test_service, input: str, expected
):
    actual = test_service.extract_document_number_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_document_number_from_bulk_upload_file_name_with_no_document_number(
    test_service,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        test_service.extract_document_number_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect document number format"


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
def test_correctly_extract_Lloyd_George_Record_from_bulk_upload_file_name(
    test_service, input, expected
):
    actual = test_service.extract_lloyd_george_record_from_bulk_upload_file_name(input)
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
        # (
        #     "_X Æ A-12_9000000001_22.10.2010.txt",
        #     ("X Æ A-12", "_9000000001_22.10.2010.txt"),
        # ),
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

    assert str(exc_info.value) == "incorrect person name format"


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

    assert str(exc_info.value) == "incorrect NHS number format"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("-12012024.txt", ("12", "01", "2024", ".txt")),
        ("-12.01.2024.csv", ("12", "01", "2024", ".csv")),
        ("-12-01-2024.txt", ("12", "01", "2024", ".txt")),
        ("-12-01-2024.txt", ("12", "01", "2024", ".txt")),
        ("-01-01-2024.txt", ("01", "01", "2024", ".txt")),
        ("_13-12-2023.pdf", ("13", "12", "2023", ".pdf")),
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

    assert str(exc_info.value) == "not a valid date"


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

    assert str(exc_info.value) == "incorrect file extension format"


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


def test_update_record_filename(test_service, mocker):
    # Arrange
    original_row = {"FILEPATH": "/old/path/file1.pdf"}
    updated_row = {"FILEPATH": "/test_practice_directory/new/path/file1.pdf"}

    # Mock S3 client copy and delete operations
    mock_client = mocker.Mock()
    test_service.s3_service.client = mock_client

    # Act
    result = test_service.update_record_filename(original_row, updated_row)

    # Assert
    mock_client.copy_object.assert_called_once_with(
        Bucket=MOCK_STAGING_STORE_BUCKET,
        CopySource={
            "Bucket": MOCK_STAGING_STORE_BUCKET,
            "Key": "test_practice_directory/old/path/file1.pdf",
        },
        Key="test_practice_directory/new/path/file1.pdf",
    )

    mock_client.delete_object.assert_called_once_with(
        Bucket=MOCK_STAGING_STORE_BUCKET,
        Key="test_practice_directory/old/path/file1.pdf",
    )

    assert result == updated_row


def test_update_file_name_file_not_found(test_service, mocker):
    test_service.staging_store_bucket = MOCK_STAGING_STORE_BUCKET
    mocker.patch.object(test_service.s3_service, "file_exist_on_s3", return_value=False)

    test_service.s3_service.client.copy_object.assert_not_called()
    test_service.s3_service.client.delete_object.assert_not_called()


def test_update_and_standardize_filenames_success_and_failure(test_service, mocker):
    # Arrange
    original_row1 = {"FILEPATH": "/path/original1.pdf"}
    updated_row1 = {"FILEPATH": "/path/updated1.pdf"}

    original_row2 = {"FILEPATH": "/path/original2.pdf"}
    updated_row2 = {"FILEPATH": "/path/updated2.pdf"}

    renaming_map = [(original_row1, updated_row1), (original_row2, updated_row2)]

    # Mock update_record_filename to return the updated_row (simulate success)
    mock_update = mocker.patch.object(
        test_service,
        "update_record_filename",
        side_effect=lambda orig, upd: upd,  # Return the updated row
    )

    # Act
    result = test_service.standardize_filenames(renaming_map)

    assert result == [updated_row1, updated_row2]
    assert mock_update.call_count == 2
    mock_update.assert_any_call(original_row1, updated_row1)
    mock_update.assert_any_call(original_row2, updated_row2)


def test_generate_renaming_map(test_service, mocker):
    # Arrange
    metadata_rows = [
        {"FILEPATH": "file1.pdf"},
        {"FILEPATH": "file2.pdf"},
    ]
    # Mock
    mock_validate = mocker.patch.object(
        test_service,
        "validate_record_filename",
        side_effect=lambda x: x,  # Assume filename is already valid
    )
    # Act
    renaming_map, rejected_rows, rejected_reasons = test_service.generate_renaming_map(
        metadata_rows
    )

    # Assert
    assert renaming_map == [
        (metadata_rows[0], {"FILEPATH": "test_practice_directory/file1.pdf"}),
        (metadata_rows[1], {"FILEPATH": "test_practice_directory/file2.pdf"}),
    ]
    assert rejected_rows == []
    assert rejected_reasons == []
    assert mock_validate.call_count == 2
