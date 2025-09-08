import datetime

import pytest
from freezegun import freeze_time

from services.bulk_upload.metadata_general_preprocessor import MetadataGeneralPreprocessor
from utils.exceptions import InvalidFileNameException


@pytest.fixture(autouse=True)
@freeze_time("2025-01-01T12:00:00")
def test_service(mocker, set_env):
    service = MetadataGeneralPreprocessor()
    return service


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
    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.extract_patient_name_from_bulk_upload_file_name",
        return_value=("Dwayne The Rock Johnson", smaller_path),
    )
    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.extract_nhs_number_from_bulk_upload_file_name",
        return_value=("9730787506", smaller_path),
    )
    mocker.patch.object(
        test_service,
        "extract_date_from_bulk_upload_file_name",
        return_value=(datetime.date(2024, 1, 12) , smaller_path),
    )
    mocker.patch.object(
        test_service,
        "extract_file_extension_from_bulk_upload_file_name",
        return_value="pdf",
    )
    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.assemble_lg_valid_file_name_full_path",
        return_value="final_filename.pdf"
    )

    result = test_service.validate_record_filename(original_filename)

    assert result == "final_filename.pdf"


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
    mocker.patch(
        "services.bulk_upload.metadata_general_preprocessor.extract_patient_name_from_bulk_upload_file_name",
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
        ("_Lloyd_George_Record_person_name", "_person_name"),
        ("_lloyd_george_record_person_name", "_person_name"),
        ("_LLOYD_GEORGE_RECORD_person_name", "_person_name"),
        ("_lloyd_george_record_lloyd_george_12342", "_lloyd_george_12342"),
        ("]{\lloyd george?record///person_name", "///person_name"),
        ("_Lloyd_George-Record_person_name", "_person_name"),
        ("_Ll0yd_Ge0rge-21Rec0rd_person_name", "_person_name"),
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
        ("-12012024.txt", (datetime.date(2024, 1, 12), '.txt')),
        ("-12.01.2024.csv", (datetime.date(2024, 1, 12), '.csv')),
        ("-12-01-2024.txt", (datetime.date(2024, 1, 12), '.txt')),
        ("-12-01-2024.txt", (datetime.date(2024, 1, 12), '.txt')),
        ("-01-01-2024.txt", (datetime.date(2024, 1, 1), '.txt')),
        ("_13-12-2023.pdf", (datetime.date(2023, 12, 13), '.pdf')),
        ("_13.12.2023.pdf", (datetime.date(2023, 12, 13), '.pdf')),
        ("_13122023.pdf", (datetime.date(2023, 12, 13), '.pdf')),
        ("_13/12/2023.pdf", (datetime.date(2023, 12, 13), '.pdf')),
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
