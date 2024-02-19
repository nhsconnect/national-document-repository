import json

import pytest
from handlers.feature_flags_handler import lambda_handler
from tests.unit.conftest import MockError
from utils.lambda_exceptions import FeatureFlagsException
from utils.lambda_response import ApiGatewayResponse

test_all_feature_flags = {
    "testFeature1": True,
    "testFeature2": True,
    "testFeature3": False,
}


@pytest.fixture
def all_feature_flags_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {},
    }
    return api_gateway_proxy_event


@pytest.fixture
def filter_feature_flags_event():
    api_gateway_proxy_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"flagName": "testFeature1"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def mock_feature_flag_service(set_env, mocker):
    mocked_class = mocker.patch("handlers.feature_flags_handler.FeatureFlagService")
    mocked_instance = mocked_class.return_value
    yield mocked_instance


@pytest.fixture
def mock_service_all_feature_flags(mock_feature_flag_service):
    service = mock_feature_flag_service
    service.get_feature_flags.return_value = test_all_feature_flags
    yield service


def test_lambda_handler_all_flags_returns_200(
    all_feature_flags_event, context, mock_service_all_feature_flags
):
    expected = ApiGatewayResponse(
        200, json.dumps(test_all_feature_flags), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(all_feature_flags_event, context)

    assert expected == actual


def test_lambda_handler_all_flags_without_query_string_params_returns_200(
    event, context, mock_service_all_feature_flags
):
    expected = ApiGatewayResponse(
        200, json.dumps(test_all_feature_flags), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(event, context)

    assert expected == actual


def test_lambda_handler_with_filter_flags_returns_200(
    filter_feature_flags_event, context, mock_feature_flag_service
):
    feature_flags = {"testFeature1": True}
    mock_feature_flag_service.get_feature_flags_by_flag.return_value = feature_flags

    expected = ApiGatewayResponse(
        200, json.dumps(feature_flags), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(filter_feature_flags_event, context)

    assert expected == actual


def test_lambda_handler_handles_service_raises_exception(
    event, context, mock_feature_flag_service
):
    mock_feature_flag_service.get_feature_flags.side_effect = FeatureFlagsException(
        500, MockError.Error
    )

    expected = ApiGatewayResponse(
        500, json.dumps(MockError.Error.value), "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(event, context)

    assert expected == actual
