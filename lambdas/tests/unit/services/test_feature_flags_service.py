import pytest
import requests_mock
from enums.lambda_error import LambdaError
from services.feature_flags_service import FeatureFlagService
from tests.unit.conftest import TEST_UUID
from utils.constants.ssm import UPLOAD_PILOT_ODS_ALLOWED_LIST
from utils.lambda_exceptions import FeatureFlagsException, LambdaException
from utils.request_context import request_context

from lambdas.enums.feature_flags import FeatureFlags

test_url = (
    "http://localhost:2772/applications/A1234/environments/B1234/configurations/C1234"
)

empty_response = {}

err_response = {
    "Details": {"InvalidParameters": {"testFeature": {"Problem": "NoSuchFlag"}}},
    "Message": "Configuration data missing one or more flag values",
    "Reason": "InvalidParameters",
}

success_200_with_filter_reponse = {"enabled": True}

success_200_all_response = {
    "testFeature1": {"enabled": True},
    "testFeature2": {"enabled": True},
    "testFeature3": {"enabled": False},
}


@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as mock:
        yield mock


@pytest.fixture
def setup_request_context():
    request_context.authorization = {
        "ndr_session_id": TEST_UUID,
        "nhs_user_id": "test-user-id",
        "selected_organisation": {"org_ods_code": "test-ods-code"},
    }
    yield
    request_context.authorization = {}


@pytest.fixture
def mock_feature_flag_service(set_env, mocker, setup_request_context):
    mocker.patch("services.feature_flags_service.SSMService")
    yield FeatureFlagService()


def test_request_app_config_data_valid_response_returns_data(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=success_200_all_response, status_code=200)

    expected = success_200_all_response
    actual = mock_feature_flag_service.request_app_config_data(test_url)

    assert actual == expected


def test_request_app_config_data_invalid_json_raises_exception(
    mock_requests, mock_feature_flag_service
):
    invalid_json = "invalid:"
    mock_requests.get(test_url, text=invalid_json, status_code=500)

    expected = LambdaException(500, LambdaError.FeatureFlagParseError)

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.request_app_config_data(test_url)

    assert e.value.__dict__ == expected.__dict__


def test_request_app_config_data_400_raises_not_found_exception(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=err_response, status_code=400)

    expected = LambdaException(404, LambdaError.FeatureFlagNotFound).__dict__

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.request_app_config_data(test_url)

    assert e.value.__dict__ == expected


def test_request_app_config_data_catch_all_raises_failure_exception(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=err_response, status_code=500)

    expected = LambdaException(500, LambdaError.FeatureFlagFailure).__dict__

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.request_app_config_data(test_url)

    assert e.value.__dict__ == expected


def test_get_feature_flags_returns_all_flags(mock_requests, mock_feature_flag_service):
    mock_requests.get(test_url, json=success_200_all_response, status_code=200)
    mock_feature_flag_service.request_app_config_data.return_value = (
        success_200_all_response
    )

    expected = {"testFeature1": True, "testFeature2": True, "testFeature3": False}

    actual = mock_feature_flag_service.get_feature_flags()

    assert expected == actual


def test_get_feature_flags_no_flags_returns_empty(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=empty_response, status_code=200)
    mock_feature_flag_service.request_app_config_data.return_value = empty_response

    expected = {}

    actual = mock_feature_flag_service.get_feature_flags()

    assert expected == actual


def test_get_feature_flags_invalid_raises_exception(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=err_response, status_code=200)
    mock_feature_flag_service.request_app_config_data.return_value = err_response
    expected = LambdaException(500, LambdaError.FeatureFlagParseError).__dict__

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.get_feature_flags()

    assert e.value.__dict__ == expected


def test_get_feature_flags_by_flag_returns_single_flag(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=success_200_with_filter_reponse, status_code=200)
    mock_feature_flag_service.request_app_config_data.return_value = (
        success_200_with_filter_reponse
    )

    expected = {"testFeature1": True}

    actual = mock_feature_flag_service.get_feature_flags_by_flag("testFeature1")

    assert expected == actual


def test_get_feature_flags_by_flag_no_flag_raises_exception(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=empty_response, status_code=200)
    mock_feature_flag_service.request_app_config_data.return_value = empty_response

    expected = LambdaException(500, LambdaError.FeatureFlagParseError).__dict__

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.get_feature_flags_by_flag("testFeature1")

    assert e.value.__dict__ == expected


def test_get_feature_flags_by_flag_invalid_raises_exception(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=err_response, status_code=200)
    mock_feature_flag_service.request_app_config_data.return_value = err_response

    expected = LambdaException(500, LambdaError.FeatureFlagParseError).__dict__

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.get_feature_flags_by_flag("testFeature1")

    assert e.value.__dict__ == expected


def test_get_allowed_list_of_ods_codes_for_upload_pilot(mock_feature_flag_service):
    expected_codes = ["ODS1", "ODS2"]
    mock_feature_flag_service.ssm_service.get_ssm_parameter.return_value = "ODS1,ODS2"

    actual_codes = (
        mock_feature_flag_service.get_allowed_list_of_ods_codes_for_upload_pilot()
    )

    assert actual_codes == expected_codes
    mock_feature_flag_service.ssm_service.get_ssm_parameter.assert_called_with(
        UPLOAD_PILOT_ODS_ALLOWED_LIST
    )


def test_get_allowed_list_of_ods_codes_for_upload_pilot_no_codes_found(
    mock_feature_flag_service, caplog
):
    mock_feature_flag_service.ssm_service.get_ssm_parameter.return_value = []

    result = mock_feature_flag_service.get_allowed_list_of_ods_codes_for_upload_pilot()

    assert result == []
    assert "No ODS codes found in allowed list for Upload Pilot" in caplog.text


@pytest.mark.parametrize(
    "auth_context, expected_result",
    [
        ({"selected_organisation": {"org_ods_code": "ODS1"}}, True),
        ({"selected_organisation": {"org_ods_code": "ODS3"}}, False),
        ({}, False),
        ({"selected_organisation": {}}, False),
        (None, False),
    ],
)
def test_check_if_ods_code_is_in_pilot(
    mocker, mock_feature_flag_service, auth_context, expected_result
):
    mock_context = mocker.MagicMock()
    mock_context.authorization = auth_context
    mocker.patch("services.feature_flags_service.request_context", mock_context)
    mocker.patch.object(
        mock_feature_flag_service,
        "get_allowed_list_of_ods_codes_for_upload_pilot",
        return_value=["ODS1", "ODS2"],
    )

    assert mock_feature_flag_service.check_if_ods_code_is_in_pilot() is expected_result


@pytest.mark.parametrize(
    "app_config_response, pilot_status, expected_flag_value",
    [
        ({"enabled": False}, True, False),
        ({"enabled": True}, False, False),
        ({"enabled": True}, True, True),
    ],
)
def test_get_feature_flags_overwrites_upload_flag(
    mocker,
    mock_feature_flag_service,
    app_config_response,
    pilot_status,
    expected_flag_value,
):
    mocker.patch.object(
        mock_feature_flag_service,
        "check_if_ods_code_is_in_pilot",
        return_value=pilot_status,
    )
    mocker.patch.object(
        mock_feature_flag_service,
        "request_app_config_data",
        return_value={
            FeatureFlags.UPLOAD_LLOYD_GEORGE_WORKFLOW_ENABLED.value: app_config_response,
            FeatureFlags.UPLOAD_LAMBDA_ENABLED.value: app_config_response,
            "some_other_flag": {"enabled": True},
        },
    )

    flags = mock_feature_flag_service.get_feature_flags()

    assert (
        flags[FeatureFlags.UPLOAD_LLOYD_GEORGE_WORKFLOW_ENABLED.value]
        is expected_flag_value
    )
    assert flags[FeatureFlags.UPLOAD_LAMBDA_ENABLED.value] is expected_flag_value
    assert flags["some_other_flag"] is True


@pytest.mark.parametrize(
    "pilot_status, expected_flag_value, feature_flag_enabled_value",
    [
        (True, True, True),
        (False, False, False),
        (False, False, True),
        (True, False, False),
    ],
)
def test_get_feature_flags_by_flag_overwrites_upload_flag(
    mocker,
    mock_feature_flag_service,
    pilot_status,
    expected_flag_value,
    feature_flag_enabled_value,
):
    flag_name = FeatureFlags.UPLOAD_LLOYD_GEORGE_WORKFLOW_ENABLED
    mocker.patch.object(
        mock_feature_flag_service,
        "check_if_ods_code_is_in_pilot",
        return_value=pilot_status,
    )
    mocker.patch.object(
        mock_feature_flag_service,
        "request_app_config_data",
        return_value={"enabled": feature_flag_enabled_value},
    )

    flags = mock_feature_flag_service.get_feature_flags_by_flag(flag_name)

    assert flags[flag_name] is expected_flag_value


def test_get_feature_flags_by_flag_for_non_upload_flag(
    mocker, mock_feature_flag_service
):
    flag_name = "some_other_flag"
    mocker.patch.object(mock_feature_flag_service, "check_if_ods_code_is_in_pilot")
    mocker.patch.object(
        mock_feature_flag_service,
        "request_app_config_data",
        return_value={"enabled": True},
    )

    flags = mock_feature_flag_service.get_feature_flags_by_flag(flag_name)

    assert flags[flag_name] is True
    mock_feature_flag_service.check_if_ods_code_is_in_pilot.assert_not_called()
