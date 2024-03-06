import json

import pytest
from conftest import TEST_FILE_KEY, TEST_NHS_NUMBER
from handlers.upload_confirm_result_handler import lambda_handler
from utils.lambda_exceptions import UploadConfirmResultException
from utils.lambda_response import ApiGatewayResponse

MOCK_VALID_EVENT_BODY = {
    "patientId": TEST_NHS_NUMBER,
    "documents": {"LG": [TEST_FILE_KEY]},
}
MOCK_VALID_EVENT = {"body": json.dumps(MOCK_VALID_EVENT_BODY)}


@pytest.fixture
def mock_upload_confirm_result_service(mocker):
    mocked_class = mocker.patch(
        "handlers.upload_confirm_result_handler.UploadConfirmResultService"
    )
    mocked_instance = mocked_class.return_value
    yield mocked_instance


def test_upload_confirm_result_handler_success(
    set_env, context, mock_upload_confirm_result_service
):
    expected = ApiGatewayResponse(
        204, "Finished processing all documents", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_EVENT, context)

    assert expected == actual


def test_event_with_no_body_raises_exception(
    set_env, context, mock_upload_confirm_result_service
):
    with pytest.raises(UploadConfirmResultException):
        lambda_handler({}, context)
