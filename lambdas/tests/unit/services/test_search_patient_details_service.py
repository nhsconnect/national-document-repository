from unittest.mock import MagicMock, patch

import pytest
from enums.repository_role import RepositoryRole
from models.pds_models import PatientDetails
from services.search_patient_details_service import SearchPatientDetailsService
from utils.exceptions import (
    InvalidResourceIdException,
    PatientNotFoundException,
    PdsErrorException,
    UserNotAuthorisedException,
)
from utils.lambda_exceptions import SearchPatientException

USER_VALID_ODS_CODE = "X12345"
USER_INVALID_ODS_CODE = "X54321"
EMPTY_ODS_CODE = ""
NHS_NUMBER = "9000000009"


@pytest.fixture
def mock_patient_details():
    return PatientDetails(
        givenName=["John"],
        familyName="Doe",
        birthDate="1980-01-01",
        postalCode="AB1 2CD",
        nhsNumber=NHS_NUMBER,
        superseded=False,
        restricted=False,
        generalPracticeOds=USER_VALID_ODS_CODE,
        active=True,
        deceased=False,
        deathNotificationStatus=None,
    )


@pytest.fixture
def mock_deceased_patient_details():
    return PatientDetails(
        givenName=["John"],
        familyName="Doe",
        birthDate="1980-01-01",
        postalCode="AB1 2CD",
        nhsNumber=NHS_NUMBER,
        superseded=False,
        restricted=False,
        generalPracticeOds=USER_VALID_ODS_CODE,
        active=True,
        deceased=True,
    )


@pytest.fixture
def mock_pds_service_fetch(mock_patient_details):
    with patch("services.search_patient_details_service.get_pds_service") as mock:
        mock_pds = MagicMock()
        mock_pds.fetch_patient_details.return_value = mock_patient_details
        mock.return_value = mock_pds
        yield mock_pds.fetch_patient_details


@pytest.fixture
def mock_feature_flag_service():
    with patch("services.search_patient_details_service.FeatureFlagService"):
        mock_service = MagicMock()
        mock_service().get_feature_flags_by_flag.return_value = {
            "UPLOAD_ARF_WORKFLOW_ENABLED": True
        }
        yield mock_service


@pytest.fixture
def mock_check_if_user_authorise():
    with patch.object(
        SearchPatientDetailsService, "_check_authorization"
    ) as mock_check:
        yield mock_check


@pytest.fixture
def mock_update_session():
    with patch.object(SearchPatientDetailsService, "_update_session") as mock_update:
        yield mock_update


@pytest.fixture
def mock_service(request, mock_feature_flag_service):
    role, ods_code = (
        request.param
        if hasattr(request, "param")
        else (
            "GP_ADMIN",
            USER_VALID_ODS_CODE,
        )
    )
    with patch(
        "services.search_patient_details_service.ManageUserSessionAccess"
    ) as mock:
        mock_session = MagicMock()
        mock.return_value = mock_session
        service = SearchPatientDetailsService(role, ods_code)
        yield service


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE),),
    indirect=True,
)
def test_handle_search_patient_request_returns_patient_details(
    mock_service,
    mock_patient_details,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
):
    # Act
    result = mock_service.handle_search_patient_request(NHS_NUMBER)

    # Assert
    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_called_once()
    mock_update_session.assert_called_once()
    assert result == mock_patient_details


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE),),
    indirect=True,
)
def test_handle_search_patient_request_with_update_session_false(
    mock_service,
    mock_patient_details,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
):
    # Act
    result = mock_service.handle_search_patient_request(
        NHS_NUMBER, update_session=False
    )

    # Assert
    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_called_once()
    mock_update_session.assert_not_called()
    assert result == mock_patient_details


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE),),
    indirect=True,
)
def test_handle_search_patient_deceased_skips_authorization_check(
    mock_service,
    mock_deceased_patient_details,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
):
    # Arrange
    mock_pds_service_fetch.return_value = mock_deceased_patient_details

    # Act
    result = mock_service.handle_search_patient_request(NHS_NUMBER)

    # Assert
    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_not_called()
    mock_update_session.assert_called_once()
    assert result == mock_deceased_patient_details


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_patient_not_found(
    mock_service,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
):
    # Arrange
    mock_pds_service_fetch.side_effect = PatientNotFoundException()

    # Act & Assert
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request(NHS_NUMBER)

    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_not_called()
    mock_update_session.assert_not_called()


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_invalid_patient(
    mock_service,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
):
    # Arrange
    mock_pds_service_fetch.side_effect = InvalidResourceIdException()

    # Act & Assert
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request(NHS_NUMBER)

    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_not_called()
    mock_update_session.assert_not_called()


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_pds_error(
    mock_service,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
):
    # Arrange
    mock_pds_service_fetch.side_effect = PdsErrorException("PDS Error")

    # Act & Assert
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request(NHS_NUMBER)

    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_not_called()
    mock_update_session.assert_not_called()


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE), ("GP_ADMIN", EMPTY_ODS_CODE)),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_validation_error(
    mock_service,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
    validation_error,
):
    # Arrange
    mock_pds_service_fetch.side_effect = validation_error

    # Act & Assert
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request(NHS_NUMBER)

    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_not_called()
    mock_update_session.assert_not_called()


@pytest.mark.parametrize(
    "mock_service",
    (("GP_ADMIN", USER_VALID_ODS_CODE),),
    indirect=True,
)
def test_handle_search_patient_request_raise_error_when_user_not_authorised(
    mock_service,
    mock_patient_details,
    mock_pds_service_fetch,
    mock_check_if_user_authorise,
    mock_update_session,
):
    # Arrange
    mock_check_if_user_authorise.side_effect = UserNotAuthorisedException()

    # Act & Assert
    with pytest.raises(SearchPatientException):
        mock_service.handle_search_patient_request(NHS_NUMBER)

    mock_pds_service_fetch.assert_called_with(NHS_NUMBER)
    mock_check_if_user_authorise.assert_called_once()
    mock_update_session.assert_not_called()


@pytest.mark.parametrize(
    "user_role, user_ods, patient_ods, patient_active, arf_enabled, exception_expected",
    [
        # GP_ADMIN tests
        (
            RepositoryRole.GP_ADMIN.value,
            USER_VALID_ODS_CODE,
            USER_VALID_ODS_CODE,
            True,
            True,
            False,
        ),
        (
            RepositoryRole.GP_ADMIN.value,
            USER_VALID_ODS_CODE,
            USER_INVALID_ODS_CODE,
            True,
            True,
            True,
        ),
        (
            RepositoryRole.GP_ADMIN.value,
            USER_VALID_ODS_CODE,
            USER_VALID_ODS_CODE,
            False,
            True,
            False,
        ),
        (
            RepositoryRole.GP_ADMIN.value,
            USER_VALID_ODS_CODE,
            USER_VALID_ODS_CODE,
            False,
            False,
            False,
        ),
        # GP_CLINICAL tests
        (
            RepositoryRole.GP_CLINICAL.value,
            USER_VALID_ODS_CODE,
            USER_VALID_ODS_CODE,
            True,
            True,
            False,
        ),
        (
            RepositoryRole.GP_CLINICAL.value,
            USER_VALID_ODS_CODE,
            USER_INVALID_ODS_CODE,
            True,
            True,
            True,
        ),
        (
            RepositoryRole.GP_CLINICAL.value,
            USER_VALID_ODS_CODE,
            USER_VALID_ODS_CODE,
            False,
            True,
            True,
        ),
        # PCSE tests
        (
            RepositoryRole.PCSE.value,
            USER_VALID_ODS_CODE,
            USER_VALID_ODS_CODE,
            True,
            True,
            True,
        ),
        (
            RepositoryRole.PCSE.value,
            USER_VALID_ODS_CODE,
            USER_VALID_ODS_CODE,
            False,
            True,
            False,
        ),
        # Unknown role
        ("UNKNOWN_ROLE", USER_VALID_ODS_CODE, USER_VALID_ODS_CODE, True, True, True),
    ],
)
def test_check_authorization(
    user_role,
    user_ods,
    patient_ods,
    patient_active,
    arf_enabled,
    exception_expected,
    mock_feature_flag_service,
):
    # Arrange
    with patch(
        "services.search_patient_details_service.is_ods_code_active"
    ) as mock_is_active:
        mock_is_active.return_value = patient_active
        mock_feature_flag_service().get_feature_flags_by_flag.return_value = {
            "UPLOAD_ARF_WORKFLOW_ENABLED": arf_enabled
        }

        service = SearchPatientDetailsService(user_role, user_ods)

        # Act & Assert
        if exception_expected:
            with pytest.raises(UserNotAuthorisedException):
                service._check_authorization(patient_ods)
        else:
            # Should not raise exception
            service._check_authorization(patient_ods)
