import json
from unittest.mock import ANY

import pytest
from botocore.exceptions import ClientError
from enums.supported_document_types import SupportedDocumentTypes
from handlers.create_document_reference_handler import lambda_handler
from tests.unit.conftest import (MOCK_ARF_BUCKET, MOCK_ARF_TABLE_NAME,
                                 MOCK_LG_BUCKET, MOCK_LG_TABLE_NAME,
                                 TEST_NHS_NUMBER, TEST_OBJECT_KEY)
from tests.unit.helpers.data.create_document_reference import (
    ARF_MOCK_EVENT_BODY, ARF_MOCK_RESPONSE, LG_AND_ARF_MOCK_RESPONSE,
    LG_MOCK_EVENT_BODY, LG_MOCK_RESPONSE, MOCK_EVENT_BODY, LG_MOCK_BAD_FILE_TYPE_EVENT_BODY,
    LG_MOCK_MISSING_FILES_EVENT_BODY, LG_MOCK_BAD_FILE_NAME_EVENT_BODY, LG_MOCK_DUPLICATE_FILES_EVENT_BODY)
from tests.unit.services.test_s3_service import MOCK_PRESIGNED_POST_RESPONSE
from utils.lambda_response import ApiGatewayResponse

TEST_DOCUMENT_LOCATION_ARF = f"s3://{MOCK_ARF_BUCKET}/{TEST_OBJECT_KEY}"
TEST_DOCUMENT_LOCATION_LG = f"s3://{MOCK_LG_BUCKET}/{TEST_OBJECT_KEY}"



@pytest.fixture
def both_type_event():
    return {"body": json.dumps(MOCK_EVENT_BODY)}


@pytest.fixture
def arf_type_event():
    return {"body": json.dumps(ARF_MOCK_EVENT_BODY)}


@pytest.fixture
def lg_type_event():
    return {"body": json.dumps(LG_MOCK_EVENT_BODY)}


def test_create_document_reference_valid_both_lg_and_arf_type_returns_200(
    set_env, both_type_event, context, mocker
):
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )

    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    expected = ApiGatewayResponse(
        200, json.dumps(LG_AND_ARF_MOCK_RESPONSE), "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(both_type_event, context)

    assert mock_presigned.call_count == 6
    assert actual == expected


def test_create_document_reference_valid_arf_type_returns_200(
    set_env, arf_type_event, context, mocker
):
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )

    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    expected = ApiGatewayResponse(
        200, json.dumps(ARF_MOCK_RESPONSE), "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)

    assert mock_presigned.call_count == 3
    assert actual == expected


def test_create_document_reference_valid_lg_type_returns_200(
    set_env, lg_type_event, context, mocker
):
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = SupportedDocumentTypes.LG
    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    expected = ApiGatewayResponse(
        200, json.dumps(LG_MOCK_RESPONSE), "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)

    assert mock_presigned.call_count == 3
    assert actual == expected


def test_create_document_reference_valid_arf_type_uses_arf_s3_bucket(
    set_env, arf_type_event, context, mocker
):
    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    lambda_handler(arf_type_event, context)

    assert mock_presigned.call_count == 3


def test_create_document_reference_valid_arf_type_adds_nhs_number_as_s3_folder(
    set_env, arf_type_event, context, mocker
):
    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")
    mock_uuid = mocker.patch("uuid.uuid4")
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    expected_uuid = "UUID_MOCK"
    expected_s3_location = TEST_NHS_NUMBER + "/" + expected_uuid
    mock_uuid.return_value = expected_uuid
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE
    lambda_handler(arf_type_event, context)

    mock_presigned.assert_called_with(MOCK_ARF_BUCKET, expected_s3_location)
    assert mock_presigned.call_count == 3


def test_create_document_reference_valid_arf_type_uses_arf_dynamo_table(
    set_env, arf_type_event, context, mocker
):
    mock_dynamo_request = mocker.patch(
        "services.dynamo_service.DynamoDBService.post_item_service"
    )
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE
    lambda_handler(arf_type_event, context)

    mock_dynamo_request.assert_called_with(MOCK_ARF_TABLE_NAME, ANY)
    assert mock_dynamo_request.call_count == 3


def test_create_document_reference_valid_lg_type_uses_lg_s3_bucket(
    set_env, lg_type_event, context, mocker
):
    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = SupportedDocumentTypes.LG
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE

    lambda_handler(lg_type_event, context)

    mock_presigned.assert_called_with(MOCK_LG_BUCKET, ANY)
    assert mock_presigned.call_count == 3


def test_create_document_reference_valid_lg_type_uses_lg_dynamo_table(
    set_env, lg_type_event, context, mocker
):
    mock_dynamo_request = mocker.patch(
        "services.dynamo_service.DynamoDBService.post_item_service"
    )
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = SupportedDocumentTypes.LG
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE
    lambda_handler(lg_type_event, context)

    mock_dynamo_request.assert_called_with(MOCK_LG_TABLE_NAME, ANY)
    assert mock_dynamo_request.call_count == 3


def test_create_document_reference_arf_type_dynamo_ClientError_returns_500(
    set_env, arf_type_event, context, mocker
):
    error = {"Error": {"Code": 500, "Message": "DynamoDB is down"}}
    exception = ClientError(error, "Query")

    mock_dynamo = mocker.patch(
        "services.dynamo_service.DynamoDBService.post_item_service"
    )
    mock_dynamo.side_effect = exception
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.return_value = MOCK_PRESIGNED_POST_RESPONSE
    expected = ApiGatewayResponse(
        500, "An error occurred when creating document reference", "POST"
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert actual == expected


def test_create_document_reference_arf_type_s3_ClientError_returns_500(
    set_env, arf_type_event, context, mocker
):
    error = {"Error": {"Code": 500, "Message": "S3 is down"}}
    exception = ClientError(error, "Query")

    mocker.patch("services.dynamo_service.DynamoDBService.post_item_service")
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )
    mock_presigned = mocker.patch(
        "services.s3_service.S3Service.create_document_presigned_url_handler"
    )
    mock_presigned.side_effect = exception
    expected = ApiGatewayResponse(
        500,
        "An error occurred when creating pre-signed url for document reference",
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert actual == expected

@pytest.mark.parametrize("event_body", [LG_MOCK_BAD_FILE_TYPE_EVENT_BODY, LG_MOCK_MISSING_FILES_EVENT_BODY, LG_MOCK_BAD_FILE_NAME_EVENT_BODY, LG_MOCK_DUPLICATE_FILES_EVENT_BODY])
def test_invalid_file_type_for_lg_return_400(set_env, context, event_body):
    expected = ApiGatewayResponse(
        400,
        "One or more if the files is not valid",
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler({"body": json.dumps(event_body)}, context)
    assert actual == expected

def test_create_document_reference_unknown_document_type_returns_400(
    set_env, arf_type_event, context, mocker
):
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = None
    expected = ApiGatewayResponse(
        400,
        "An error occurred processing the required document type",
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert actual == expected


arf_environment_variables = [
    "DOCUMENT_STORE_BUCKET_NAME",
    "DOCUMENT_STORE_DYNAMODB_NAME",
]
lg_environment_variables = ["LLOYD_GEORGE_BUCKET_NAME", "LLOYD_GEORGE_DYNAMODB_NAME"]


@pytest.mark.parametrize("environmentVariable", lg_environment_variables)
def test_lambda_handler_missing_environment_variables_type_lg_returns_400(
    set_env, monkeypatch, lg_type_event, environmentVariable, context, mocker
):
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = SupportedDocumentTypes.LG
    monkeypatch.delenv(environmentVariable)
    expected = ApiGatewayResponse(
        500,
        "An error occurred due to missing environment variables: '"
        + environmentVariable
        + "'",
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(lg_type_event, context)
    assert expected == actual


@pytest.mark.parametrize("environmentVariable", arf_environment_variables)
def test_lambda_handler_missing_environment_variables_type_arf_returns_400(
    set_env, monkeypatch, arf_type_event, environmentVariable, context, mocker
):
    mock_supported_document_get_from_field_name = mocker.patch(
        "enums.supported_document_types.SupportedDocumentTypes.get_from_field_name"
    )
    mock_supported_document_get_from_field_name.return_value = (
        SupportedDocumentTypes.ARF
    )
    monkeypatch.delenv(environmentVariable)
    expected = ApiGatewayResponse(
        500,
        "An error occurred due to missing environment variables: '"
        + environmentVariable
        + "'",
        "POST",
    ).create_api_gateway_response()
    actual = lambda_handler(arf_type_event, context)
    assert expected == actual
