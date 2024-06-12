import pytest
from handlers.data_collection_handler import lambda_handler
from services.data_collection_service import DataCollectionService
from utils.exceptions import MissingEnvVarException


def test_lambda_handler_call_underlying_service(mocker, context, set_env):
    mock_data_collection_service = mocker.patch(
        "handlers.data_collection_handler.DataCollectionService",
        spec=DataCollectionService,
    ).return_value

    lambda_handler(None, context)

    mock_data_collection_service.collect_all_data_and_write_to_dynamodb.assert_called_once()


def test_lambda_handler_check_for_env_vars(context):
    with pytest.raises(MissingEnvVarException) as error:
        lambda_handler(None, context)

    assert "An error occurred due to missing environment variable" in str(error.value)
