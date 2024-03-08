import pytest
from handlers.upload_confirm_result_handler import (
    lambda_handler,
    processing_event_details,
)
from helpers.data.upload_confirm_result import (
    MOCK_MISSING_BODY_EVENT,
    MOCK_MISSING_NHS_NUMBER_EVENT,
    MOCK_VALID_LG_EVENT,
)
from utils.lambda_exceptions import UploadConfirmResultException
from utils.lambda_response import ApiGatewayResponse


@pytest.fixture
def mock_upload_confirm_result_service(mocker):
    mocked_class = mocker.patch(
        "handlers.upload_confirm_result_handler.UploadConfirmResultService"
    )
    mocked_instance = mocked_class.return_value
    yield mocked_instance


def test_upload_confirm_result_handler_success_lg(
    set_env, context, mock_upload_confirm_result_service
):
    expected = ApiGatewayResponse(
        204, "Finished processing all documents", "POST"
    ).create_api_gateway_response()

    actual = lambda_handler(MOCK_VALID_LG_EVENT, context)

    assert expected == actual


def test_processing_event_details_event_with_invalid_body_raises_exception(
    set_env, context, mock_upload_confirm_result_service
):
    with pytest.raises(UploadConfirmResultException):
        processing_event_details(MOCK_MISSING_BODY_EVENT)


def test_processing_event_details_missing_nhs_number_raises_error():
    with pytest.raises(UploadConfirmResultException):
        processing_event_details(MOCK_MISSING_NHS_NUMBER_EVENT)


# def test_processing_event_details_invalid_nhs_number_raises_error():
#     with pytest.raises(UploadConfirmResultException):
#         processing_event_details(MOCK_INVALID_NHS_NUMBER_EVENT)
