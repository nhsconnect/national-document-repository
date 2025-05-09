import json
import os
from enum import Enum
from unittest.mock import patch

import pytest
from handlers.search_patient_details_handler import lambda_handler
from models.pds_models import PatientDetails
from utils.lambda_exceptions import SearchPatientException
from utils.lambda_response import ApiGatewayResponse


class MockError(Enum):
    Error = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }


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
    set_env,
    valid_id_event_with_auth_header,
    context,
    mocker,
    mocked_context,
):
    patient_details_object = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="LS1 6AE",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
        generalPracticeOds="Y12345",
        active=True,
        deceased=False,
        deathNotificationStatus=None,
    )
    patient_details = patient_details_object.model_dump_json(
        by_alias=True,
        exclude={
            "death_notification_status",
            "general_practice_ods",
        },
    )
    mocked_service = mocker.MagicMock()
    mocker.patch(
        "handlers.search_patient_details_handler.SearchPatientDetailsService",
        return_value=mocked_service,
    )

    mocked_service.handle_search_patient_request.return_value = patient_details_object
    expected = ApiGatewayResponse(
        200, patient_details, "GET"
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_with_auth_header, context)

    assert actual == expected


def test_lambda_handler_invalid_id_returns_400(invalid_id_event, context):
    nhs_number = invalid_id_event["queryStringParameters"]["patientId"]
    body = json.dumps(
        {
            "message": f"Invalid patient number {nhs_number}",
            "err_code": "PN_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(invalid_id_event, context)

    assert expected == actual


def test_lambda_handler_valid_id_not_in_pds_returns_404(
    set_env, valid_id_event_with_auth_header, context, mocker, mocked_context
):
    mocker.patch(
        "handlers.search_patient_details_handler.SearchPatientDetailsService.handle_search_patient_request",
        side_effect=SearchPatientException(404, MockError.Error),
    )

    expected = ApiGatewayResponse(
        404,
        json.dumps(MockError.Error.value),
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_with_auth_header, context)

    assert expected == actual


def test_lambda_handler_missing_id_in_query_params_returns_400(
    set_env, missing_id_event, context
):
    body = json.dumps(
        {
            "message": "An error occurred due to missing key",
            "err_code": "PN_4002",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(400, body, "GET").create_api_gateway_response()

    actual = lambda_handler(missing_id_event, context)

    assert expected == actual


def test_lambda_handler_missing_auth_returns_400(
    set_env, valid_id_event_with_auth_header, context, mocker
):
    mocked_context = mocker.MagicMock()
    mocked_context.authorization = {"selected_organisation": {"org_ods_code": ""}}
    mocker.patch(
        "handlers.search_patient_details_handler.request_context", mocked_context
    )
    body = json.dumps(
        {
            "message": "Missing user details",
            "err_code": "SP_4001",
            "interaction_id": "88888888-4444-4444-4444-121212121212",
        }
    )
    expected = ApiGatewayResponse(
        400,
        body,
        "GET",
    ).create_api_gateway_response()

    actual = lambda_handler(valid_id_event_with_auth_header, context)

    assert expected == actual
