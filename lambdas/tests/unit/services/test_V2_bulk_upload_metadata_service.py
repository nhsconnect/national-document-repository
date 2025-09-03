import pytest
from freezegun import freeze_time
from msgpack.fallback import BytesIO
from services.V2_bulk_upload_metadata_service import (
    V2BulkUploadMetadataService,
)
from utils.exceptions import InvalidFileNameException


@pytest.fixture(autouse=True)
@freeze_time("2025-01-01T12:00:00")
def test_service(mocker, set_env):
    service = V2BulkUploadMetadataService(practice_directory="test_practice_directory")
    mocker.patch.object(service, "s3_service")
    return service

@pytest.fixture
def mock_get_metadata_rows_from_file(mocker, test_service):
    return mocker.patch.object(test_service, "get_metadata_rows_from_file")


@pytest.fixture
def mock_generate_and_save_csv_file(mocker, test_service):
    return mocker.patch.object(test_service, "generate_and_save_csv_file")


@pytest.fixture
def mock_s3_client(mocker, test_service):
    return mocker.patch.object(test_service.s3_service, "client")


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
