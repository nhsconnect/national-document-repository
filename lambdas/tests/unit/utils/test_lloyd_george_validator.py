import json

import pytest
from botocore.exceptions import ClientError
from requests import Response
from services.document_service import DocumentService
from tests.unit.conftest import MOCK_LG_TABLE_NAME, TEST_NHS_NUMBER
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT
from tests.unit.models.test_document_reference import MOCK_DOCUMENT_REFERENCE
from utils.exceptions import (PatientAlreadyExistException,
                              PdsTooManyRequestsException)
from utils.lloyd_george_validator import (
    LGInvalidFilesException, check_for_duplicate_files,
    check_for_file_names_agrees_with_each_other,
    check_for_number_of_files_match_expected,
    check_for_patient_already_exist_in_repo, extract_info_from_filename,
    validate_file_name, validate_lg_file_type, validate_with_pds_service)


def test_catching_error_when_file_type_not_pdf():
    with pytest.raises(LGInvalidFilesException):
        file_type = "image/png"
        validate_lg_file_type(file_type)


def test_valid_file_type():
    try:
        file_type = "application/pdf"
        validate_lg_file_type(file_type)
    except LGInvalidFilesException:
        assert False, "One or more of the files do not match the required file type"


def test_invalid_file_name():
    with pytest.raises(LGInvalidFilesException):
        file_name = "bad_name"
        validate_file_name(file_name)


def test_valid_file_name():
    try:
        file_name = (
            "1of1_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf"
        )
        validate_file_name(file_name)
    except LGInvalidFilesException:
        assert False, "One or more of the files do not match naming convention"


@pytest.mark.parametrize(
    "file_name",
    [
        "1of1_Lloyd_George_Record_[James O'Brien]_[1111111111]_[25-12-2019].pdf",
        "1of1_Lloyd_George_Record_[Joé Blöggês-Glüë]_[1111111111]_[25-12-2019].pdf",
        "1of1_Lloyd_George_Record_[Joé Blöggês-Glüë]_[1111111111]_[25-12-2019].pdf",  # same string in NFD form
    ],
    ids=[
        "Patient name with apostrophe",
        "Patient name with accented char in NFC code point",
        "Patient name with accented char in NFD code point",
    ],
)
def test_valid_file_name_special_characters(file_name):
    try:
        validate_file_name(file_name)
    except LGInvalidFilesException:
        assert (
            False
        ), "validate_file_name should be handle patient names with special characters"


def test_valid_file_name_with_apostrophe():
    try:
        file_name = (
            "1of1_Lloyd_George_Record_[Joé Blöggê's-Glüë]_[1111111111]_[25-12-2019].pdf"
        )
        validate_file_name(file_name)
    except LGInvalidFilesException:
        assert False, "One or more of the files do not match naming convention"


def test_files_with_duplication():
    with pytest.raises(LGInvalidFilesException):
        lg_file_list = [
            "1of1_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "1of1_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        ]
        check_for_duplicate_files(lg_file_list)


def test_files_without_duplication():
    try:
        lg_file_list = [
            "1of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "2of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        ]
        check_for_duplicate_files(lg_file_list)
    except LGInvalidFilesException:
        assert False, "One or more of the files has the same filename"


def test_files_list_with_missing_files():
    with pytest.raises(LGInvalidFilesException) as e:
        lg_file_list = [
            "1of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "2of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        ]
        check_for_number_of_files_match_expected(lg_file_list[0], len(lg_file_list))
    assert str(e.value) == "There are missing file(s) in the request"


def test_files_list_with_too_many_files():
    with pytest.raises(LGInvalidFilesException) as e:
        lg_file_list = [
            "1of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "2of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "3of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "1of3_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        ]
        check_for_number_of_files_match_expected(lg_file_list[0], len(lg_file_list))
    assert str(e.value) == "There are more files than the total number in file name"


def test_files_list_with_invalid_name():
    with pytest.raises(LGInvalidFilesException) as e:
        lg_file_list = [
            "invalid_file_name",
            "2of4_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "3of4_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "4of4_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        ]
        check_for_number_of_files_match_expected(lg_file_list[0], len(lg_file_list))
    assert str(e.value) == "One or more of the files do not match naming convention"


def test_file_name_with_apostrophe_as_name():
    """
    This is an edge case which currently passes.
    As part of prmdr-520 it was decided that it was acceptable to have an apostrophe accepted as a name
    This is because patient names will only ever come from PDS
    """
    try:
        file_name = "1of1_Lloyd_George_Record_[']_[1111111111]_[25-12-2019].pdf"
        validate_file_name(file_name)
    except LGInvalidFilesException:
        assert False, "One or more of the files do not match naming convention"


def test_files_without_missing_files():
    try:
        lg_file_list = [
            "1of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
            "2of2_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        ]
        check_for_number_of_files_match_expected(lg_file_list[0], len(lg_file_list))
    except LGInvalidFilesException:
        assert False, "There are missing file(s) in the request"


@pytest.mark.parametrize(
    ["file_name", "patient_name"],
    [
        (
            "123of456_Lloyd_George_Record_[James O'Brien]_[1111111111]_[25-12-2019].pdf",
            "James O'Brien",
        ),
        (
            "123of456_Lloyd_George_Record_[Joé Blöggês-Glüë]_[1111111111]_[25-12-2019].pdf",
            "Joé Blöggês-Glüë",
        ),
        (
            "123of456_Lloyd_George_Record_[Joé Blöggês-Glüë]_[1111111111]_[25-12-2019].pdf",
            "Joé Blöggês-Glüë",
        ),  # same string in NFD form
    ],
    ids=[
        "Patient name with apostrophe",
        "Patient name with accented char in NFC code point",
        "Patient name with accented char in NFD code point",
    ],
)
def test_extract_info_from_filename(file_name, patient_name):
    expected = {
        "page_no": "123",
        "total_page_no": "456",
        "patient_name": patient_name,
        "nhs_number": "1111111111",
        "date_of_birth": "25-12-2019",
    }

    actual = extract_info_from_filename(file_name)

    assert actual == expected


def test_files_for_different_patients():
    lg_file_list = [
        "1of4_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        "2of4_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
        "3of4_Lloyd_George_Record_[John Smith]_[1111111112]_[25-12-2019].pdf",
        "4of4_Lloyd_George_Record_[Joe Bloggs]_[1111111111]_[25-12-2019].pdf",
    ]
    with pytest.raises(LGInvalidFilesException) as e:
        check_for_file_names_agrees_with_each_other(lg_file_list)
    assert str(e.value) == "File names does not match with each other"


def test_validate_nhs_id_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_pds_call.return_value = response
    mock_odc_code = mocker.patch(
        "utils.lloyd_george_validator.get_user_ods_code", return_value="Y12345"
    )

    validate_with_pds_service(lg_file_list, "9000000009")

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)
    mock_odc_code.assert_called_once()


def test_mismatch_nhs_id_no_pds_service(mocker, mock_pds_call):
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000005]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000005]_[22-10-2010].pdf",
    ]
    mock_odc_code = mocker.patch(
        "utils.lloyd_george_validator.get_user_ods_code", return_value="Y12345"
    )

    with pytest.raises(LGInvalidFilesException):
        validate_with_pds_service(lg_file_list, "9000000009")

    mock_pds_call.assert_not_called()
    mock_odc_code.assert_not_called()


def test_mismatch_name_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_pds_call.return_value = response
    mock_odc_code = mocker.patch("utils.lloyd_george_validator.get_user_ods_code")

    with pytest.raises(LGInvalidFilesException):
        validate_with_pds_service(lg_file_list, "9000000009")

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)
    mock_odc_code.assert_not_called()


def test_mismatch_ods_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_pds_call.return_value = response
    mock_odc_code = mocker.patch(
        "utils.lloyd_george_validator.get_user_ods_code", return_value="H98765"
    )

    with pytest.raises(LGInvalidFilesException):
        validate_with_pds_service(lg_file_list, "9000000009")

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)
    mock_odc_code.assert_called_once()


def test_mismatch_dob_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[14-01-2000].pdf",
        "2of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[14-01-2000].pdf",
    ]
    mock_pds_call.return_value = response
    mock_odc_code = mocker.patch("utils.lloyd_george_validator.get_user_ods_code")

    with pytest.raises(LGInvalidFilesException):
        validate_with_pds_service(lg_file_list, "9000000009")

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)
    mock_odc_code.assert_not_called()


def test_patient_not_found_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 404
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_pds_call.return_value = response
    mock_odc_code = mocker.patch("utils.lloyd_george_validator.get_user_ods_code")

    with pytest.raises(LGInvalidFilesException) as e:
        validate_with_pds_service(lg_file_list, "9000000009")
    assert str(e.value) == "Could not find the given patient on PDS"

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)
    mock_odc_code.assert_not_called()


def test_bad_request_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 400
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_pds_call.return_value = response
    mock_odc_code = mocker.patch("utils.lloyd_george_validator.get_user_ods_code")

    with pytest.raises(LGInvalidFilesException) as e:
        validate_with_pds_service(lg_file_list, "9000000009")
    assert str(e.value) == "Failed to retrieve patient data from PDS"

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)
    mock_odc_code.assert_not_called()


def test_raise_client_error_from_ssm_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")
    mock_client_error = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "testing"
    )
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_pds_call.return_value = response
    mock_odc_code = mocker.patch(
        "utils.lloyd_george_validator.get_user_ods_code", return_value=mock_client_error
    )

    with pytest.raises(LGInvalidFilesException):
        validate_with_pds_service(lg_file_list, "9000000009")

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)
    mock_odc_code.assert_called_once()


def test_validate_with_pds_service_raise_PdsTooManyRequestsException(
    mocker, mock_pds_call
):
    response = Response()
    response.status_code = 429
    response._content = b"Too Many Requests"
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    mock_pds_call.return_value = response

    mocker.patch("utils.lloyd_george_validator.get_user_ods_code")

    with pytest.raises(PdsTooManyRequestsException):
        validate_with_pds_service(lg_file_list, "9000000009")

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)


def test_check_for_patient_already_exist_in_repo_return_none_when_patient_record_not_exist(
    set_env, mock_fetch_documents_from_table
):
    mock_fetch_documents_from_table.return_value = []
    expected = None
    actual = check_for_patient_already_exist_in_repo(TEST_NHS_NUMBER)

    assert actual == expected

    mock_fetch_documents_from_table.assert_called_with(
        TEST_NHS_NUMBER, MOCK_LG_TABLE_NAME
    )


def test_check_check_for_patient_already_exist_in_repo_raise_exception_when_patient_record_already_exist(
    set_env, mock_fetch_documents_from_table
):
    mock_fetch_documents_from_table.return_value = [MOCK_DOCUMENT_REFERENCE]

    with pytest.raises(PatientAlreadyExistException):
        check_for_patient_already_exist_in_repo(TEST_NHS_NUMBER)

    mock_fetch_documents_from_table.assert_called_with(
        TEST_NHS_NUMBER, MOCK_LG_TABLE_NAME
    )


@pytest.fixture
def mock_pds_call(mocker):
    yield mocker.patch("services.mock_pds_service.MockPdsApiService.pds_request")


@pytest.fixture
def mock_fetch_documents_from_table(mocker):
    yield mocker.patch.object(DocumentService, "fetch_documents_from_table")
