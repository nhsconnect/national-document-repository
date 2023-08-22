from dataclasses import dataclass

import pytest
from handlers.search_patient_details_handler import lambda_handler
from requests.models import Response
from tests.unit.pds_data.utils import load_pds_data


@pytest.fixture
def event_valid_id():
    api_gateway_proxy_event = {
        "queryStringParameters": {"patientId": "9000000009"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def event_invalid_id():
    api_gateway_proxy_event = {
        "queryStringParameters": {"patientId": "900000000900"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def event_missing_id():
    api_gateway_proxy_event = {
        "queryStringParameters": {"invalid": "9000000009"},
    }
    return api_gateway_proxy_event


@pytest.fixture
def context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        aws_request_id: str = "88888888-4444-4444-4444-121212121212"
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:123456789101:function:test"
        )

    return LambdaContext()


def test_lambda_handler_valid_id_returns_200(event_valid_id, context, mocker):
    response = Response()
    response.status_code = 200
    response._content = load_pds_data()[0]

    mocker.patch(
        "services.pds_api_service.PdsApiService.fake_pds_request", return_value=response
    )

    actual = lambda_handler(event_valid_id, context)

    expected = {
        "body": '{"givenName":["Jane"],"familyName":"Smith","birthDate":"2010-10-22",'
        '"postalCode":"LS1 6AE","nhsNumber":"9000000009","superseded":false,'
        '"restricted":false}',
        "headers": {
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/fhir+json",
        },
        "isBase64Encoded": False,
        "statusCode": 200,
    }

    assert expected == actual


def test_lambda_handler_invalid_id_returns_400(event_invalid_id, context, mocker):
    response = Response()
    response.status_code = 400

    mocker.patch(
        "services.pds_api_service.PdsApiService.fake_pds_request", return_value=response
    )

    actual = lambda_handler(event_invalid_id, context)

    expected = {
        "body": "Invalid NHS number.",
        "headers": {
            "Content-Type": "application/fhir+json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "isBase64Encoded": False,
        "statusCode": 400,
    }

    assert expected == actual


def test_lambda_handler_valid_id_not_in_pds_returns_404(
    event_valid_id, context, mocker
):
    response = Response()
    response.status_code = 404

    mocker.patch(
        "services.pds_api_service.PdsApiService.fake_pds_request", return_value=response
    )

    actual = lambda_handler(event_valid_id, context)

    expected = {
        "body": "Patient does not exist for given NHS number.",
        "headers": {
            "Content-Type": "application/fhir+json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "isBase64Encoded": False,
        "statusCode": 404,
    }

    assert expected == actual


def test_lambda_handler_missing_id_in_query_params_returns_400(
    event_missing_id, context, mocker
):
    response = Response()
    response.status_code = 400

    mocker.patch(
        "services.pds_api_service.PdsApiService.fake_pds_request", return_value=response
    )

    actual = lambda_handler(event_missing_id, context)

    expected = {
        "body": "No NHS number found in request parameters.",
        "headers": {
            "Content-Type": "application/fhir+json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "isBase64Encoded": False,
        "statusCode": 400,
    }

    assert expected == actual
