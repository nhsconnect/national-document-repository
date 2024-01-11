import os
from unittest.mock import patch

import pytest
from handlers.search_patient_details_handler import lambda_handler
from utils.lambda_exceptions import SearchPatientException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def patch_env_vars():
    env_vars = {
        "PDS_FHIR_IS_STUBBED": "1",
        "SSM_PARAM_JWT_TOKEN_PUBLIC_KEY": "mock_public_key",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture()
def mocked_context(mocker):
    mocked_context = mocker.MagicMock()
    mocked_context.authorization = {
        "selected_organisation": {"org_ods_code": "Y12345"},
        "repository_role": "GP_ADMIN",
    }
    yield mocker.patch(
        "handlers.search_patient_details_handler.request_context", mocked_context
    )


def test_lambda_handler_valid_id_returns_200(
    valid_id_event_with_auth_header, context, mocker, mocked_context
):
    patient_details = """{"givenName":["Jane"],"familyName":"Smith","birthDate":"2010-10-22",
        "postalCode":"LS1 6AE","nhsNumber":"9000000009","superseded":false,
        "restricted":false,"generalPracticeOds":"Y12345","active":true}"""

    mocker.patch(
        "handlers.search_patient_details_handler.SearchPatientDetailsService.handle_search_patient_request",
        return_value=patient_details,
    )
    expected = ApiGatewayResponse(
        200, patient_details, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_with_auth_header, context)

    assert expected == actual


def test_lambda_handler_invalid_id_returns_400(invalid_id_event, context):
    expected = ApiGatewayResponse(
        400, "Invalid NHS number", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(invalid_id_event, context)

    assert expected == actual


def test_lambda_handler_valid_id_not_in_pds_returns_404(
    valid_id_event_with_auth_header, context, mocker, mocked_context
):
    mocker.patch(
        "handlers.search_patient_details_handler.SearchPatientDetailsService.handle_search_patient_request",
        side_effect=SearchPatientException(
            404, "Patient does not exist for given NHS number"
        ),
    )

    expected = ApiGatewayResponse(
        404, "Patient does not exist for given NHS number", "GET", "ERR_PATIENT"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_with_auth_header, context)

    assert expected == actual


def test_lambda_handler_missing_id_in_query_params_returns_400(
    missing_id_event, context
):
    expected = ApiGatewayResponse(
        400, "An error occurred due to missing key: 'patientId'", "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(missing_id_event, context)

    assert expected == actual


def test_lambda_handler_missing_auth_returns_400(
    valid_id_event_with_auth_header, context, mocker
):
    mocked_context = mocker.MagicMock()
    mocked_context.authorization = {"selected_organisation": {"org_ods_code": ""}}
    mocker.patch(
        "handlers.search_patient_details_handler.request_context", mocked_context
    )
    expected = ApiGatewayResponse(
        400, "Missing user details", "GET", "ERR_SEARCH"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_with_auth_header, context)

    assert expected == actual
