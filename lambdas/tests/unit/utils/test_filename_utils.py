import pytest

from utils.filename_utils import extract_page_number, extract_total_pages, assemble_lg_valid_file_name_full_path


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
    file_extension = ".txt"

    expected = "/amazing-directory/1of2_Lloyd_George_Record_[Jim-Stevens]_[9000000001]_[22-10-2010].txt"
    actual = assemble_lg_valid_file_name_full_path(
        file_path_prefix,
        first_document_number,
        second_document_number,
        person_name,
        nhs_number,
        day,
        month,
        year,
        file_extension,
    )
    assert actual == expected
