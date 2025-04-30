import pytest
from services.metadata_preprocessing_sevice import MetadataPreprocessingService
from utils.exceptions import InvalidFileNameException


@pytest.fixture
def repo_under_test(set_env, mocker):
    service = MetadataPreprocessingService()
    yield service


def test_validate_and_update_file_name_returns_a_valid_file_path(repo_under_test):
    wrong_file_path = "01 of 02_Lloyd_George_Record_Jim Stevens_9000000001_22.10.2010"
    expected_file_path = (
        "1of2_Lloyd_George_Record_[Jim Stevens]_[9000000001]_[22-10-2010]"
    )

    actual = repo_under_test.validate_and_update_bulk_uplodad_file_name(wrong_file_path)

    assert actual == expected_file_path


def test_correctly_extract_document_number_from_bulk_upload_file_name(repo_under_test):
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
        actual = repo_under_test.extract_document_number_bulk_upload_file_name(
            input_str
        )
        assert actual == expected


def test_extract_document_number_from_bulk_upload_file_name_with_no_document_number(
    repo_under_test,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        repo_under_test.extract_document_number_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect document number format"


def test_correctly_extract_Lloyd_George_Record_from_bulk_upload_file_name(
    repo_under_test,
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
        actual = repo_under_test.extract_lloyd_george_record_from_bulk_upload_file_name(
            input_str
        )
        assert actual == expected


def test_extract_Lloyd_george_from_bulk_upload_file_name_with_no_Lloyd_george(
    repo_under_test,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        repo_under_test.extract_lloyd_george_record_from_bulk_upload_file_name(
            invalid_data
        )

    assert str(exc_info.value) == "incorrect Lloyd George Record format"


def test_correctly_extract_person_name_from_bulk_upload_file_name(repo_under_test):
    test_cases = [
        ("_John_doe-1231", ("John Doe", "-1231")),
        ("-José-María-1231", ("José María", "-1231")),
        ("-José&María-Grandola&1231", ("José María Grandola", "&1231")),
    ]

    for input_str, expected in test_cases:
        actual = repo_under_test.extract_person_name_from_bulk_upload_file_name(
            input_str
        )
        assert actual == expected


def test_extract_person_name_from_bulk_upload_file_name_with_no_person_name(
    repo_under_test,
):
    invalid_data = "12-12-2024"

    with pytest.raises(InvalidFileNameException) as exc_info:
        repo_under_test.extract_person_name_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect person name format"


def test_correctly_extract_nhs_number_from_bulk_upload_file_name(repo_under_test):
    # paths, expected_results
    test_cases = [
        ("_-9991211234-12012024", ("9991211234", "-12012024")),
        ("_-9-99/12?11\/234-12012024", ("9991211234", "-12012024")),
        ("_-9-9l9/12?11\/234-12012024", ("9991211234", "-12012024")),
    ]

    for input_str, expected in test_cases:
        actual = repo_under_test.extract_nhs_number_from_bulk_upload_file_name(
            input_str
        )
        assert actual == expected


def test_extract_nhs_number_from_bulk_upload_file_name_with_nhs_number(repo_under_test):
    invalid_data = "invalid_nhs_number.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        repo_under_test.extract_nhs_number_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect NHS number format"


def test_correctly_extract_date_from_bulk_upload_file_name(repo_under_test):
    test_cases = [
        ("-12012024", ("12", "01", "2024")),
        ("-12.01.2024", ("12", "01", "2024")),
        ("-12-01-2024", ("12", "01", "2024")),
        ("-12-1-2024", ("12", "01", "2024")),
        ("-1-01-2024", ("01", "01", "2024")),
        ("-1-01-24", ("01", "01", "2024")),
    ]

    for input_str, expected in test_cases:
        actual = repo_under_test.extract_date_from_bulk_upload_file_name(input_str)
        assert actual == expected


def test_extract_data_from_bulk_upload_file_name_with_incorrect_date_format(
    repo_under_test,
):
    invalid_data = "12-july-2024.txt"

    with pytest.raises(InvalidFileNameException) as exc_info:
        repo_under_test.extract_date_from_bulk_upload_file_name(invalid_data)

    assert str(exc_info.value) == "incorrect date format"


def test_correctly_assembles_valid_file_name(repo_under_test):
    firstDocumentNumber = 1
    secondDocumentNumber = 2
    lloyd_george_record = "Lloyd_George_Record"
    person_name = "Jim Stevens"
    nhs_number = "9000000001"
    day = 22
    month = 10
    year = 2010

    expected = "1of2_Lloyd_George_Record_[Jim Stevens]_[9000000001]_[22-10-2010]"
    actual = repo_under_test.assemble_valid_file_name(
        firstDocumentNumber,
        secondDocumentNumber,
        lloyd_george_record,
        person_name,
        nhs_number,
        day,
        month,
        year,
    )
    assert actual == expected
