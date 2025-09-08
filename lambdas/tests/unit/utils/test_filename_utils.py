import datetime

import pytest

from utils.exceptions import InvalidFileNameException
from utils.filename_utils import (
    assemble_lg_valid_file_name_full_path,
    extract_date_from_bulk_upload_file_name,
    extract_document_number_bulk_upload_file_name,
    extract_document_path,
    extract_document_path_for_lloyd_george_record,
    extract_file_extension_from_bulk_upload_file_name,
    extract_lloyd_george_record_from_bulk_upload_file_name,
    extract_nhs_number_from_bulk_upload_file_name,
    extract_page_number,
    extract_patient_name_from_bulk_upload_file_name,
    extract_total_pages,
)


@pytest.mark.parametrize(
    ["filename", "expected"],
    [
        ("1of3_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf", 1),
        ("2of3_Lloyd_George_Record_[Jane Smith]_[123456789]_[25-12-2019].pdf", 2),
        (
            "123of456_Lloyd_George_Record_[Janet Smith]_[123456789]_[25-12-2019].pdf",
            123,
        ),
    ],
)
def test_extract_page_number(filename, expected):
    actual = extract_page_number(filename)
    assert actual == expected


@pytest.mark.parametrize(
    "invalid_filename", ["invalid_file_name.pdf", "abc_of_efg.pdf", "random string"]
)
def test_extract_page_number_raise_error_for_invalid_filename(invalid_filename):
    with pytest.raises(ValueError):
        extract_page_number(invalid_filename)


@pytest.mark.parametrize(
    ["filename", "expected"],
    [
        ("1of3_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf", 3),
        ("2of3_Lloyd_George_Record_[Jane Smith]_[123456789]_[25-12-2019].pdf", 3),
        (
            "123of456_Lloyd_George_Record_[Janet Smith]_[123456789]_[25-12-2019].pdf",
            456,
        ),
    ],
)
def test_extract_total_pages(filename, expected):
    actual = extract_total_pages(filename)
    assert actual == expected


@pytest.mark.parametrize(
    "invalid_filename", ["invalid_file_name.pdf", "abc_of_efg.pdf", "random string"]
)
def test_extract_total_pages_raise_error_for_invalid_filename(invalid_filename):
    with pytest.raises(ValueError):
        extract_total_pages(invalid_filename)


def test_correctly_assembles_valid_file_name():
    file_path_prefix = "/amazing-directory/"
    first_document_number = 1
    second_document_number = 2
    person_name = "Jim-Stevens"
    nhs_number = "9000000001"
    day = "22"
    month = "10"
    year = "2010"
    datetime_object = datetime.date(int(year), int(month), int(day))
    file_extension = ".txt"

    expected = "/amazing-directory/1of2_Lloyd_George_Record_[Jim-Stevens]_[9000000001]_[22-10-2010].txt"
    actual = assemble_lg_valid_file_name_full_path(
        file_path_prefix,
        first_document_number,
        second_document_number,
        person_name,
        nhs_number,
        datetime_object,
        file_extension,
    )
    assert actual == expected


@pytest.mark.parametrize(
    ["value", "expected"],
    [
        (
            "/M89002/10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            (
                "/M89002",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            ),
        ),
        (
            "/2020 Prince of Whales 2/10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            (
                "/2020 Prince of Whales 2",
                "10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
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
                "_10of10_Lloyd_George_Record_[Carol Hughes]_[1234567890]_[14-11-2000].pdf",
            ),
        ),
    ],
)
def test_extract_document_path(value, expected):
    actual = extract_document_path(value)
    assert actual == expected


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("-12012024.txt", (datetime.date(2024, 1, 12), ".txt")),
        ("-12.01.2024.csv", (datetime.date(2024, 1, 12), ".csv")),
        ("-12-01-2024.txt", (datetime.date(2024, 1, 12), ".txt")),
        ("-12-01-2024.txt", (datetime.date(2024, 1, 12), ".txt")),
        ("-01-01-2024.txt", (datetime.date(2024, 1, 1), ".txt")),
        ("_13-12-2023.pdf", (datetime.date(2023, 12, 13), ".pdf")),
        ("_13.12.2023.pdf", (datetime.date(2023, 12, 13), ".pdf")),
        ("_13122023.pdf", (datetime.date(2023, 12, 13), ".pdf")),
        ("_13/12/2023.pdf", (datetime.date(2023, 12, 13), ".pdf")),
        ("01-Nov-1992.pdf", (datetime.date(1992, 11, 1), ".pdf")),
        (" 01-Nov-1992.pdf", (datetime.date(1992, 11, 1), ".pdf")),
    ],
)
def test_correctly_extract_date_from_bulk_upload_file_name(input, expected):
    actual = extract_date_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_data_from_bulk_upload_file_name_with_incorrect_date_format():
    invalid_data = "_12-13-2024.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        extract_date_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid date format"


@pytest.mark.parametrize(
    ["input", "expected", "expected_exception"],
    [
        ("_-9991211234-12012024", ("9991211234", "-12012024"), None),
        (r"_-9-99/12?11\/234-12012024", ("9991211234", "-12012024"), None),
        (r"_-9-9l9/12?11\/234-12012024", ("9991211234", "-12012024"), None),
        (
            "12_12_12_12_12_12_12_2024.csv",
            "incorrect NHS number format",
            InvalidFileNameException,
        ),
        ("_9000000001_11_12_2025.csv", ("9000000001", "_11_12_2025.csv"), None),
        ("_900000000111_12_2025.csv", ("9000000001", "11_12_2025.csv"), None),
        ("900-000-000111.10.2010", ("9000000001", "11.10.2010"), None),
    ],
)
def test_correctly_extract_nhs_number_from_bulk_upload_file_name(
    input, expected, expected_exception
):
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            extract_nhs_number_from_bulk_upload_file_name(input)
            assert str(exc_info.value) == expected
    else:
        actual = extract_nhs_number_from_bulk_upload_file_name(input)
        assert actual == expected


def test_extract_nhs_number_from_bulk_upload_file_name_with_nhs_number():
    invalid_data = "invalid_nhs_number.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        extract_nhs_number_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid NHS number"


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
def test_correctly_extract_person_name_from_bulk_upload_file_name(input, expected):
    actual = extract_patient_name_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_person_name_from_bulk_upload_file_name_with_no_person_name():
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        extract_patient_name_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid patient name"


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
def test_extract_document_path(value, expected):
    actual = extract_document_path_for_lloyd_george_record(value)
    assert actual == expected


def test_extract_document_path_with_no_document_path():
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        extract_document_path_for_lloyd_george_record(invalid_data)

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
def test_correctly_extract_document_number_from_bulk_upload_file_name(input, expected):
    actual = extract_document_number_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_document_number_from_bulk_upload_file_name_with_no_document_number():
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        extract_document_number_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Incorrect document number format"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        ("_Lloyd_George_Record_person_name", "_person_name"),
        ("_lloyd_george_record_person_name", "_person_name"),
        ("_LLOYD_GEORGE_RECORD_person_name", "_person_name"),
        ("_lloyd_george_record_lloyd_george_12342", "_lloyd_george_12342"),
        (r"]{\lloyd george?record///person_name", "///person_name"),
        ("_Lloyd_George-Record_person_name", "_person_name"),
        ("_Ll0yd_Ge0rge-21Rec0rd_person_name", "_person_name"),
    ],
)
def test_correctly_extract_lloyd_george_record_from_bulk_upload_file_name(
    input, expected
):
    actual = extract_lloyd_george_record_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_lloyd_george_from_bulk_upload_file_name_with_no_lloyd_george():
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        extract_lloyd_george_record_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid Lloyd_George_Record separator"


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        (".txt", ".txt"),
        ("cool_stuff.txt", ".txt"),
        ("{}.[].txt", ".txt"),
        (".csv", ".csv"),
    ],
)
def test_correctly_extract_file_extension_from_bulk_upload_file_name(input, expected):
    actual = extract_file_extension_from_bulk_upload_file_name(input)
    assert actual == expected


def test_extract_file_extension_from_bulk_upload_file_name_with_incorrect_file_extension_format():
    invalid_data = "txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        extract_file_extension_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "Invalid file extension"
