import pytest
from botocore.exceptions import ClientError
from enums.supported_document_types import SupportedDocumentTypes
from models.pds_models import Patient
from requests import Response
from services.base.ssm_service import SSMService
from services.document_service import DocumentService
from tests.unit.conftest import TEST_NHS_NUMBER
from tests.unit.helpers.data.bulk_upload.test_data import (
    TEST_DOCUMENT_REFERENCE_LIST,
    TEST_NHS_NUMBER_FOR_BULK_UPLOAD,
    TEST_STAGING_METADATA_WITH_INVALID_FILENAME,
)
from tests.unit.helpers.data.pds.pds_patient_response import (
    PDS_PATIENT,
    PDS_PATIENT_WITH_MIDDLE_NAME,
)
from tests.unit.models.test_document_reference import MOCK_DOCUMENT_REFERENCE
from utils.common_query_filters import NotDeleted
from utils.exceptions import (
    PatientRecordAlreadyExistException,
    PdsTooManyRequestsException,
)
from utils.lloyd_george_validator import (
    LGInvalidFilesException,
    allowed_to_ingest_ods_code,
    check_for_duplicate_files,
    check_for_file_names_agrees_with_each_other,
    check_for_number_of_files_match_expected,
    check_for_patient_already_exist_in_repo,
    extract_info_from_filename,
    get_allowed_ods_codes,
    getting_patient_info_from_pds,
    validate_file_name,
    validate_filename_with_patient_details,
    validate_lg_file_names,
    validate_lg_file_type,
    validate_lg_files,
)


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


def test_validate_nhs_id_with_pds_service(mocker, mock_pds_patient_details):
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    validate_filename_with_patient_details(lg_file_list, mock_pds_patient_details)


def test_mismatch_nhs_id(mocker):
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000005]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000005]_[22-10-2010].pdf",
    ]

    mocker.patch("utils.lloyd_george_validator.check_for_patient_already_exist_in_repo")
    mocker.patch(
        "utils.lloyd_george_validator.check_for_number_of_files_match_expected"
    )
    mocker.patch("utils.lloyd_george_validator.validate_file_name")

    with pytest.raises(LGInvalidFilesException):
        validate_lg_file_names(lg_file_list, "9000000009")


def test_mismatch_name_with_pds_service(mocker, mock_pds_patient_details):
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jake Plain Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jake Plain Smith]_[9000000009]_[22-10-2010].pdf",
    ]

    with pytest.raises(LGInvalidFilesException):
        validate_filename_with_patient_details(lg_file_list, mock_pds_patient_details)


def test_order_names_with_pds_service(mocker):
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jake Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jake Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    patient = Patient.model_validate(PDS_PATIENT_WITH_MIDDLE_NAME)
    patient_details = patient.get_minimum_patient_details("9000000009")
    try:
        validate_filename_with_patient_details(lg_file_list, patient_details)
    except LGInvalidFilesException:
        assert False


def test_missing_middle_name_names_with_pds_service(mocker):
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    patient = Patient.model_validate(PDS_PATIENT_WITH_MIDDLE_NAME)
    patient_details = patient.get_minimum_patient_details("9000000009")
    try:
        validate_filename_with_patient_details(lg_file_list, patient_details)
    except LGInvalidFilesException:
        assert False


def test_mismatch_dob_with_pds_service(mocker, mock_pds_patient_details):
    lg_file_list = [
        "1of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[14-01-2000].pdf",
        "2of2_Lloyd_George_Record_[Jane Plain Smith]_[9000000009]_[14-01-2000].pdf",
    ]

    with pytest.raises(LGInvalidFilesException):
        validate_filename_with_patient_details(lg_file_list, mock_pds_patient_details)


def test_patient_not_found_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 404

    mock_pds_call.return_value = response

    with pytest.raises(LGInvalidFilesException) as e:
        getting_patient_info_from_pds("9000000009")
    assert str(e.value) == "Could not find the given patient on PDS"

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)


def test_bad_request_with_pds_service(mocker, mock_pds_call):
    response = Response()
    response.status_code = 400

    mock_pds_call.return_value = response

    with pytest.raises(LGInvalidFilesException) as e:
        getting_patient_info_from_pds("9000000009")
    assert str(e.value) == "Failed to retrieve patient data from PDS"

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)


def test_validate_with_pds_service_raise_PdsTooManyRequestsException(
    mocker, mock_pds_call
):
    response = Response()
    response.status_code = 429
    response._content = b"Too Many Requests"
    mock_pds_call.return_value = response

    with pytest.raises(PdsTooManyRequestsException):
        getting_patient_info_from_pds("9000000009")

    mock_pds_call.assert_called_with(nhs_number="9000000009", retry_on_expired=True)


def test_check_for_patient_already_exist_in_repo_return_none_when_patient_record_not_exist(
    set_env, mock_fetch_available_document_references_by_type
):
    mock_fetch_available_document_references_by_type.return_value = []
    expected = None
    actual = check_for_patient_already_exist_in_repo(TEST_NHS_NUMBER)

    assert actual == expected

    mock_fetch_available_document_references_by_type.assert_called_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.LG,
        query_filter=NotDeleted,
    )


def test_check_check_for_patient_already_exist_in_repo_raise_exception_when_patient_record_already_exist(
    set_env, mock_fetch_available_document_references_by_type
):
    mock_fetch_available_document_references_by_type.return_value = [
        MOCK_DOCUMENT_REFERENCE
    ]

    with pytest.raises(PatientRecordAlreadyExistException):
        check_for_patient_already_exist_in_repo(TEST_NHS_NUMBER)

    mock_fetch_available_document_references_by_type.assert_called_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.LG,
        query_filter=NotDeleted,
    )


def test_validate_bulk_files_raises_PatientRecordAlreadyExistException_when_patient_record_already_exists(
    set_env, mocker
):
    mocker.patch(
        "utils.lloyd_george_validator.check_for_patient_already_exist_in_repo",
        side_effect=PatientRecordAlreadyExistException,
    )

    with pytest.raises(PatientRecordAlreadyExistException):
        validate_lg_file_names(
            TEST_STAGING_METADATA_WITH_INVALID_FILENAME, TEST_NHS_NUMBER_FOR_BULK_UPLOAD
        )


def test_get_allowed_ods_codes_return_a_list_of_ods_codes(mock_get_ssm_parameter):
    mock_get_ssm_parameter.return_value = "Y12345, H81109"
    expected = ["Y12345", "H81109"]

    actual = get_allowed_ods_codes()

    assert actual == expected


def test_get_allowed_ods_codes_can_handle_the_ALL_option(mock_get_ssm_parameter):
    mock_get_ssm_parameter.return_value = "ALL"

    expected = ["ALL"]

    actual = get_allowed_ods_codes()

    assert actual == expected


def test_get_allowed_ods_codes_remove_whitespaces_and_return_ods_codes_in_upper_case(
    mock_get_ssm_parameter,
):
    mock_get_ssm_parameter.return_value = "h12345 , abc12  ,  345xy "

    expected = ["H12345", "ABC12", "345XY"]

    actual = get_allowed_ods_codes()

    assert actual == expected


@pytest.mark.parametrize(
    ["gp_ods_param_value", "patient_ods_code", "expected"],
    [
        # can handle single ods code
        ["H81109", "H81109", True],
        ["H85686", "H81109", False],
        # can handle a list of ods codes
        ["H81109, H85686", "H81109", True],
        ["H81109, H85686", "H85686", True],
        ["H81109, H85686", "Y12345", False],
        # present of "ALL" option will allow any ods code to be accepted
        ["ALL", "H81109", True],
        ["ALL", "H85686", True],
        ["ALL", "", True],
        ["H81109, H85686, ALL", "Y12345", True],
    ],
)
def test_allowed_to_ingest_ods_code(
    mock_get_ssm_parameter, gp_ods_param_value, patient_ods_code, expected
):
    mock_get_ssm_parameter.return_value = gp_ods_param_value

    actual = allowed_to_ingest_ods_code(patient_ods_code)

    assert actual == expected


def test_allowed_to_ingest_ods_code_propagate_error(mock_get_ssm_parameter):
    mock_get_ssm_parameter.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "test error"}}, "GetParameter"
    )

    with pytest.raises(ClientError):
        allowed_to_ingest_ods_code("H81109")


def test_mismatch_nhs_in_validate_lg_file(mocker):
    mocker.patch(
        "utils.lloyd_george_validator.check_for_number_of_files_match_expected"
    )
    mocker.patch("utils.lloyd_george_validator.validate_file_name")

    with pytest.raises(LGInvalidFilesException):
        validate_lg_files(TEST_DOCUMENT_REFERENCE_LIST, "9000000009")


@pytest.fixture
def mock_get_ssm_parameter(mocker):
    return mocker.patch.object(SSMService, "get_ssm_parameter")


@pytest.fixture
def mock_pds_call(mocker):
    yield mocker.patch("services.mock_pds_service.MockPdsApiService.pds_request")


@pytest.fixture
def mock_fetch_available_document_references_by_type(mocker):
    yield mocker.patch.object(
        DocumentService, "fetch_available_document_references_by_type"
    )


@pytest.fixture
def mock_pds_patient_details():
    patient = Patient.model_validate(PDS_PATIENT)
    patient_details = patient.get_minimum_patient_details("9000000009")
    return patient_details
