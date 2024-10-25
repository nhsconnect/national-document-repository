# # test_edge_presign_service.py

# import pytest
# from botocore.exceptions import ClientError
# from services.edge_presign_service import EdgePresignService
# from tests.unit.enums.test_edge_presign_values import (
#     EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION,
#     EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES,
#     EXPECTED_EDGE_NO_CLIENT_ERROR_CODE,
#     EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE,
#     EXPECTED_ENVIRONMENT,
#     EXPECTED_SSM_PARAMETER_KEY,
#     FORMATTED_TABLE_NAME,
#     INVALID_DOMAIN,
#     TABLE_NAME,
#     VALID_DOMAIN,
# )
# from utils.lambda_exceptions import CloudFrontEdgeException


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

#     edge_service.attempt_url_update(uri_hash, VALID_DOMAIN)

#     mock_ssm_service_instance, mock_dynamo_service_instance = mock_edge_presign_service

#     mock_ssm_service_instance.get_ssm_parameter.assert_called_once_with(
#         EXPECTED_SSM_PARAMETER_KEY
#     )
#     mock_dynamo_service_instance.update_item.assert_called_once_with(
#         table_name=FORMATTED_TABLE_NAME,
#         key=uri_hash,
#         updated_fields={"IsRequested": True},
#         condition_expression=EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION,
#         expression_attribute_values=EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES,
#     )


# def test_attempt_url_update_client_error(mock_edge_presign_service):
#     edge_service = EdgePresignService()
#     mock_dynamo_service_instance = mock_edge_presign_service[1]
#     mock_dynamo_service_instance.update_item.side_effect = ClientError(
#         error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
#         operation_name="UpdateItem",
#     )

#     with pytest.raises(CloudFrontEdgeException) as exc_info:
#         edge_service.attempt_url_update("test_uri_hash", VALID_DOMAIN)

#     assert exc_info.value.status_code == 400
#     assert exc_info.value.message == EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE
#     assert exc_info.value.err_code == EXPECTED_EDGE_NO_CLIENT_ERROR_CODE


# def test_extract_environment_from_valid_domain():
#     result = EdgePresignService.extract_environment_from_domain(VALID_DOMAIN)
#     assert result == EXPECTED_ENVIRONMENT


# def test_extract_environment_from_invalid_domain():
#     result = EdgePresignService.extract_environment_from_domain(INVALID_DOMAIN)
#     assert result == ""


# def test_extend_table_name_with_environment():
#     result = EdgePresignService.extend_table_name(TABLE_NAME, EXPECTED_ENVIRONMENT)
#     assert result == FORMATTED_TABLE_NAME


# def test_extend_table_name_without_environment():
#     result = EdgePresignService.extend_table_name(TABLE_NAME, "")
#     assert result == TABLE_NAME
