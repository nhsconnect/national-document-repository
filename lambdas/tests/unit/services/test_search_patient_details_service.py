import pytest
from models.pds_models import PatientDetails
from services.search_patient_details_service import SearchPatientDetailsService
from tests.unit.conftest import TEST_UUID
from utils.exceptions import (
    InvalidResourceIdException,
    PatientNotFoundException,
    PdsErrorException,
    UserNotAuthorisedException,
)
from utils.lambda_exceptions import SearchPatientException
from utils.request_context import request_context

USER_VALID_ODS_CODE = "ABC123"
PATIENT_VALID_ODS_CODE = "XYZ789"
EMPTY_ODS_CODE = ""


@pytest.fixture(scope="function")
def mock_service(set_env, request, mocker):
    request_context.authorization = {"ndr_session_id": TEST_UUID}
    user_role, user_ods_code = request.param
    service = SearchPatientDetailsService(user_role, user_ods_code)
    mocker.patch.object(service, "manage_user_session_service")

    mocker.patch.object(service, "feature_flag_service")
    return service


@pytest.fixture()
def mock_pds_service_fetch(mocker):
    pds_service_response = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="LS1 6AE",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
        generalPracticeOds="Y12345",
        active=True,
    )
    mock_pds_service_fetch = mocker.patch(
        "services.patient_search_service.PatientSearch.fetch_patient_details"
    )
    mock_pds_service_fetch.return_value = pds_service_response
    yield mock_pds_service_fetch


@pytest.fixture()
def mock_check_if_user_authorise(mocker, mock_service):
    yield mocker.patch.object(mock_service, "check_if_user_authorise")


@pytest.mark.parametrize(
    "mock_service",
    (
        ("GP_ADMIN", USER_VALID_ODS_CODE),
        ("GP_CLINICAL", USER_VALID_ODS_CODE),
        ("PCSE", ""),
    ),
    indirect=True,
)
def test_check_if_user_authorise_valid(mock_service):
    try:
        expected_ods = mock_service.user_ods_code
        mock_service.check_if_user_authorise(expected_ods)
    except UserNotAuthorisedException as e:
        assert False, e


@pytest.mark.parametrize(
    "mock_service",
    (
        ("GP_ADMIN", USER_VALID_ODS_CODE),
        ("PCSE", ""),
    ),
    indirect=True,
)
def test_check_if_user_authorise_valid_when_arf_is_on(mocker, mock_service):
    try:
        mock_function = mocker.patch.object(
            mock_service.feature_flag_service, "get_feature_flags_by_flag"
        )
        mock_function.return_value = {"uploadArfWorkflowEnabled": True}
        mock_service.check_if_user_authorise("SUSP")
    except UserNotAuthorisedException as e:
        assert False, e


@pytest.mark.parametrize(
    "mock_service",
    (
        ("GP_ADMIN", USER_VALID_ODS_CODE),
        ("GP_ADMIN", EMPTY_ODS_CODE),
        ("GP_CLINICAL", USER_VALID_ODS_CODE),
        ("GP_CLINICAL", EMPTY_ODS_CODE),
        ("PCSE", EMPTY_ODS_CODE),
        ("PCSE", PATIENT_VALID_ODS_CODE),
        ("Not_valid", PATIENT_VALID_ODS_CODE),
        ("Not_valid", EMPTY_ODS_CODE),
    ),
    indirect=True,
)
def test_check_if_user_authorise_raise_error(mock_service):
    with pytest.raises(UserNotAuthorisedException):
        mock_service.check_if_user_authorise(PATIENT_VALID_ODS_CODE)


@pytest.mark.parametrize(
    "mock_service",
    (
        ("GP_ADMIN", USER_VALID_ODS_CODE),
        ("GP_ADMIN", EMPTY_ODS_CODE),
        ("GP_CLINICAL", USER_VALID_ODS_CODE),
        ("GP_CLINICAL", EMPTY_ODS_CODE),
    ),
    indirect=True,
)
def test_check_if_user_authorise_raise_error_arf_off_inactive_patient(
    mocker, mock_service
):
    mock_function = mocker.patch.object(
        mock_service.feature_flag_service, "get_feature_flags_by_flag"
    )
    mock_function.return_value = {"uploadArfWorkflowEnabled": False}
    with pytest.raises(UserNotAuthorisedException):
        mock_service.check_if_user_authorise("")


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_valid(
    mock_service,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
):

    expected_response = (
        '{"givenName":["Jane"],"familyName":"Smith","birthDate":"2010-10-22","postalCode":"LS1 '
        '6AE","nhsNumber":"9000000009","superseded":false,"restricted":false,'
        '"active":true,"deceased":false}'
    )

    actual_response = mock_service.handle_search_patient_request("9000000009")

    mock_check_if_user_authorise.assert_called()
    mock_pds_service_fetch.assert_called_with("9000000009")
    assert actual_response == expected_response


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_valid_skip_authorisation_check_when_patient_is_deceased(
    mock_service,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
):
    pds_service_response = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="LS1 6AE",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
        generalPracticeOds="Y12345",
        active=True,
        deceased=True,
    )
    expected_response = (
        '{"givenName":["Jane"],"familyName":"Smith","birthDate":"2010-10-22","postalCode":"LS1 '
        '6AE","nhsNumber":"9000000009","superseded":false,"restricted":false,'
        '"active":true,"deceased":true}'
    )
    mock_pds_service_fetch.return_value = pds_service_response

    actual_response = mock_service.handle_search_patient_request("9000000009")

    mock_check_if_user_authorise.assert_not_called()
    mock_pds_service_fetch.assert_called_with("9000000009")
    assert actual_response == expected_response


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_patient_not_found(
    mock_service, mock_pds_service_fetch
):
    mock_pds_service_fetch.side_effect = PatientNotFoundException()
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request("9000000009")

    mock_pds_service_fetch.assert_called_with("9000000009")


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_user_is_not_auth(
    mock_service, mock_pds_service_fetch, mock_check_if_user_authorise
):
    mock_check_if_user_authorise.side_effect = UserNotAuthorisedException()
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request("9000000009")

    mock_pds_service_fetch.assert_called_with("9000000009")
    mock_check_if_user_authorise.assert_called()


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_invalid_patient(
    mock_service, mock_pds_service_fetch, mock_check_if_user_authorise
):
    mock_pds_service_fetch.side_effect = InvalidResourceIdException()
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request("9000000009")

    mock_pds_service_fetch.assert_called_with("9000000009")
    mock_check_if_user_authorise.assert_not_called()


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_pds_error(
    mock_service, mock_pds_service_fetch, mock_check_if_user_authorise
):
    mock_pds_service_fetch.side_effect = PdsErrorException()

    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request("9000000009")

    mock_pds_service_fetch.assert_called_with("9000000009")
    mock_check_if_user_authorise.assert_not_called()
