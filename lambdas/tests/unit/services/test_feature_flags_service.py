import pytest
import requests_mock
from services.feature_flags_service import FeatureFlagService
from utils.lambda_exceptions import FeatureFlagsException

test_url = (
    "http://localhost:2772/applications/A1234/environments/B1234/configurations/C1234"
)

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
def mock_feature_flag_service(set_env):
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

    expected = {
        "status_code": 500,
        "message": "Failed to parse JSON from AppConfig response",
        "err_code": "FFL_5001",
    }

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.request_app_config_data(test_url)

    assert e.value.__dict__ == expected


def test_request_app_config_data_400_raises_not_found_exception(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=err_response, status_code=400)

    expected = {
        "status_code": 404,
        "message": "Feature flag/s may not exist in AppConfig profile",
        "err_code": "FFL_4001",
    }

    with pytest.raises(FeatureFlagsException) as e:
        mock_feature_flag_service.request_app_config_data(test_url)

    assert e.value.__dict__ == expected


def test_request_app_config_data_catch_all_raises_failure_exception(
    mock_requests, mock_feature_flag_service
):
    mock_requests.get(test_url, json=err_response, status_code=500)

    expected = {
        "status_code": 500,
        "message": "Failed to retrieve feature flag/s from AppConfig profile",
        "err_code": "FFL_5002",
    }

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
