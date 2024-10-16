# from unittest.mock import Mock

# import pytest
# from botocore.exceptions import ClientError
# from services.edge_presign_service import EdgePresignService
# from tests.unit.enums.test_edge_presign_values import (
#     ENV,
#     EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION,
#     EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES,
#     EXPECTED_EDGE_NO_CLIENT_ERROR_CODE,
#     EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE,
#     EXPECTED_SSM_PARAMETER_KEY,
#     MISSING_ORIGIN_EVENT_MODEL,
#     NHS_DOMAIN,
#     TABLE_NAME,
#     VALID_EVENT_MODEL,
# )
# from utils.lambda_exceptions import CloudFrontEdgeException


# def mock_context():
#     context = Mock()
#     context.aws_request_id = "fake_request_id"
#     return context


# @pytest.fixture
# def valid_event():
#     return VALID_EVENT_MODEL


# @pytest.fixture
# def missing_origin_event():
#     return MISSING_ORIGIN_EVENT_MODEL


# @pytest.fixture
# def mock_edge_presign_service(mocker):
#     mock_ssm_service = mocker.patch("services.edge_presign_service.SSMService")
#     mock_ssm_service_instance = mock_ssm_service.return_value
#     mock_ssm_service_instance.get_ssm_parameter.return_value = TABLE_NAME

#     mock_dynamo_service = mocker.patch("services.edge_presign_service.DynamoDBService")
#     mock_dynamo_service_instance = mock_dynamo_service.return_value
#     mock_dynamo_service_instance.update_item.return_value = None

#     return mock_ssm_service_instance, mock_dynamo_service_instance


# def test_attempt_url_update_success(mock_edge_presign_service):
#     edge_service = EdgePresignService()
#     uri_hash = "test_uri_hash"
#     origin_url = f"https://{ENV}.{NHS_DOMAIN}"

#     edge_service.attempt_url_update(uri_hash, origin_url)

#     mock_ssm_service_instance = mock_edge_presign_service[0]
#     mock_dynamo_service_instance = mock_edge_presign_service[1]

#     mock_ssm_service_instance.get_ssm_parameter.assert_called_once_with(
#         EXPECTED_SSM_PARAMETER_KEY
#     )

#     mock_dynamo_service_instance.update_item.assert_called_once_with(
#         table_name=f"{ENV}_{TABLE_NAME}",
#         key=uri_hash,
#         updated_fields={"IsRequested": True},
#         condition_expression=EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION,
#         expression_attribute_values=EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES,
#     )


# def test_attempt_url_update_client_error(mock_edge_presign_service):
#     edge_service = EdgePresignService()

#     edge_service.dynamo_service.update_item.side_effect = ClientError(
#         error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
#         operation_name="UpdateItem",
#     )

#     with pytest.raises(CloudFrontEdgeException) as exc_info:
#         edge_service.attempt_url_update("test_uri_hash", f"https://{ENV}.{NHS_DOMAIN}")

#     assert exc_info.value.status_code == 400
#     assert exc_info.value.message == EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE
#     assert exc_info.value.err_code == EXPECTED_EDGE_NO_CLIENT_ERROR_CODE


# def test_attempt_url_update_invalid_origin(mock_edge_presign_service):
#     edge_service = EdgePresignService()

#     result = edge_service.extract_environment_from_url("invalid_url")

#     expected_empty_result = ""

#     assert result == expected_empty_result
