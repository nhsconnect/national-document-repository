import pytest
from models.pds_models import PatientDetails
from services.search_patient_details_service import SearchPatientDetailsService
from utils.exceptions import (
    InvalidResourceIdException,
    PatientNotFoundException,
    PdsErrorException,
    UserNotAuthorisedException,
)
from utils.lambda_exceptions import SearchPatientException


@pytest.fixture(scope="function")
def mock_service(request, mocker):
    user_role, user_ods_code = request.param
    service = SearchPatientDetailsService(user_role, user_ods_code)
    mocker.patch.object(service, "ssm_service")
    return service


@pytest.fixture()
def mock_pds_service_fetch(mocker):
    mock_pds_service_fetch = mocker.patch(
        "services.patient_search_service.PatientSearch.fetch_patient_details"
    )
    yield mock_pds_service_fetch


@pytest.fixture()
def mock_check_if_user_authorise(mocker, mock_service):
    yield mocker.patch.object(mock_service, "check_if_user_authorise")


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", "test_ods_code"), ("GP_CLINICAL", "test_ods_code"), ("PCSE", "")),
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
        ("GP_ADMIN", "test_ods_code"),
        ("GP_ADMIN", ""),
        ("GP_CLINICAL", "test_ods_code"),
        ("GP_CLINICAL", ""),
        ("PCSE", ""),
        ("PCSE", "new_gp_ods_code"),
        ("Not_valid", "new_gp_ods_code"),
        ("Not_valid", ""),
    ),
    indirect=True,
)
def test_check_if_user_authorise_raise_error(mock_service):
    with pytest.raises(UserNotAuthorisedException):
        mock_service.check_if_user_authorise("new_gp_ods_code")


@pytest.mark.parametrize(
    "mock_service", (("GP_ADMIN", "test_ods_code"), ("GP_ADMIN", "")), indirect=True
)
def test_handle_search_patient_request_valid(mock_service, mocker):
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
    expected_response = (
        '{"givenName":["Jane"],"familyName":"Smith","birthDate":"2010-10-22","postalCode":"LS1 '
        '6AE","nhsNumber":"9000000009","superseded":false,"restricted":false,"generalPracticeOds":"Y12345","active":true}'
    )
    mock_pds_service_fetch = mocker.patch(
        "services.patient_search_service.PatientSearch.fetch_patient_details",
        return_value=pds_service_response,
    )
    mocker.patch(
        "services.search_patient_details_service.SearchPatientDetailsService.check_if_user_authorise"
    )

    actual_response = mock_service.handle_search_patient_request("9000000009")

    mock_pds_service_fetch.assert_called_with("9000000009")
    assert actual_response == expected_response


@pytest.mark.parametrize(
    "mock_service", (("GP_ADMIN", "test_ods_code"), ("GP_ADMIN", "")), indirect=True
)
def test_handle_search_patient_request_raise_error_when_patient_not_found(
    mock_service, mock_pds_service_fetch
):
    mock_pds_service_fetch.side_effect = PatientNotFoundException()
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request("9000000009")

    mock_pds_service_fetch.assert_called_with("9000000009")


@pytest.mark.parametrize(
    "mock_service", (("GP_ADMIN", "test_ods_code"), ("GP_ADMIN", "")), indirect=True
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
    "mock_service", (("GP_ADMIN", "test_ods_code"), ("GP_ADMIN", "")), indirect=True
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
    "mock_service", (("GP_ADMIN", "test_ods_code"), ("GP_ADMIN", "")), indirect=True
)
def test_handle_search_patient_request_raise_error_when_pds_error(
    mock_service, mock_pds_service_fetch, mock_check_if_user_authorise
):
    mock_pds_service_fetch.side_effect = PdsErrorException()

    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request("9000000009")

    mock_pds_service_fetch.assert_called_with("9000000009")
    mock_check_if_user_authorise.assert_not_called()
