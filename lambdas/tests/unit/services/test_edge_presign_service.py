import pytest
from botocore.exceptions import ClientError
from services.edge_presign_service import EdgePresignService
from tests.unit.enums.test_edge_presign_values import (
    ENV,
    EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION,
    EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES,
    EXPECTED_EDGE_NO_CLIENT_ERROR_CODE,
    EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE,
    EXPECTED_SSM_PARAMETER_KEY,
    EXPECTED_SUCCESS_RESPONSE,
    NHS_DOMAIN,
    TABLE_NAME,
)
from utils.lambda_exceptions import CloudFrontEdgeException

# Instantiate the service for testing
edge_presign_service = EdgePresignService()


@pytest.fixture
def mock_dynamo_service(mocker):
    return mocker.patch.object(edge_presign_service, "dynamo_service", autospec=True)


@pytest.fixture
def mock_ssm_service(mocker):
    return mocker.patch.object(edge_presign_service, "ssm_service", autospec=True)


@pytest.fixture
def valid_origin_url():
    return f"https://{ENV}.{NHS_DOMAIN}"


def test_attempt_url_update_success(
    mock_dynamo_service, mock_ssm_service, valid_origin_url
):
    mock_dynamo_service.update_conditional.return_value = None
    mock_ssm_service.get_ssm_parameter.return_value = TABLE_NAME
    uri_hash = "valid_hash"

    # Action
    response = edge_presign_service.attempt_url_update(
        uri_hash=uri_hash, origin_url=valid_origin_url
    )

    # Assertions
    expected_table_name = f"{ENV}_{TABLE_NAME}"
    assert response == EXPECTED_SUCCESS_RESPONSE  # Success scenario returns None
    mock_ssm_service.get_ssm_parameter.assert_called_once_with(
        EXPECTED_SSM_PARAMETER_KEY
    )
    mock_dynamo_service.update_conditional.assert_called_once_with(
        table_name=expected_table_name,
        key=uri_hash,
        updated_fields={"IsRequested": True},
        condition_expression=EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION,
        expression_attribute_values=EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES,
    )


def test_attempt_url_update_client_error(
    mock_dynamo_service, mock_ssm_service, valid_origin_url
):
    mock_dynamo_service.update_conditional.side_effect = ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException"}}, "UpdateItem"
    )
    mock_ssm_service.get_ssm_parameter.return_value = TABLE_NAME
    uri_hash = "valid_hash"

    with pytest.raises(CloudFrontEdgeException) as exc_info:
        edge_presign_service.attempt_url_update(
            uri_hash=uri_hash, origin_url=valid_origin_url
        )

    # Assertions
    assert exc_info.value.status_code == 400
    assert exc_info.value.message == EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE
    assert exc_info.value.err_code == EXPECTED_EDGE_NO_CLIENT_ERROR_CODE


def test_extract_environment_from_url():
    url = f"https://{ENV}.{NHS_DOMAIN}/path/to/resource"
    expected_environment = ENV
    actual_environment = edge_presign_service.extract_environment_from_url(url)
    assert actual_environment == expected_environment

    # Invalid URL test
    url_invalid = f"https://{NHS_DOMAIN}/path/to/resource"
    expected_empty_result = ""
    actual_empty_result = edge_presign_service.extract_environment_from_url(url_invalid)
    assert actual_empty_result == expected_empty_result


def test_extend_table_name():
    base_table_name = TABLE_NAME
    expected_table_with_env = f"{ENV}_{base_table_name}"
    actual_table_with_env = edge_presign_service.extend_table_name(base_table_name, ENV)
    assert actual_table_with_env == expected_table_with_env

    expected_table_no_env = base_table_name
    actual_table_no_env = edge_presign_service.extend_table_name(base_table_name, "")
    assert actual_table_no_env == expected_table_no_env
