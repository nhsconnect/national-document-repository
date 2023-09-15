from botocore.exceptions import ClientError
from handlers import login_redirect_handler
from oauthlib.oauth2 import InsecureTransportError
from tests.unit.helpers.ssm_responses import MOCK_MULTI_STRING_PARAMETERS_RESPONSE

from lambdas.utils.lambda_response import ApiGatewayResponse

RETURN_URL = "https://www.string_value_1.com?" \
              "response_type=code&" \
              "client_id=1122121212&" \
              "redirect_uri=https%3A%2F%2Fwww.testexample.com%&" \
              "state=test1state&" \
              "scope=openid+profile+nationalrbacaccess+associatedorgs"

class FakeWebAppClient:
    def __init__(self, *arg, **kwargs):
        self.state = "test1state"

    def prepare_authorization_request(self, *args, **kwargs):
        return RETURN_URL, "", ""

class FakeDynamoDBService:
    def __init__(self, dynamodb_name, *arg, **kwargs):
        self.dynamodb_name = dynamodb_name

    def post_item_service(self, *args, **kwargs):
        return None
def test_prepare_redirect_response_return_302_with_correct_headers(mocker, monkeypatch):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
    mock_dynamo_service = mocker.patch("handlers.login_redirect_handler.save_state_in_dynamo_db")
    mock_ssm_service = mocker.patch("handlers.login_redirect_handler.get_ssm_parameters", return_value=MOCK_MULTI_STRING_PARAMETERS_RESPONSE)

    response = login_redirect_handler.prepare_redirect_response(FakeWebAppClient)
    location_header = {"Location": RETURN_URL}

    expected = ApiGatewayResponse(
        302, "", "GET"
    ).create_api_gateway_response(headers=location_header)

    assert response == expected
    mock_dynamo_service.assert_called_with("test1state")
    mock_ssm_service.assert_called_once()

def test_prepare_redirect_response_return_500_when_boto3_client_failing(mocker, monkeypatch):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
    mock_dynamo_service = mocker.patch("handlers.login_redirect_handler.save_state_in_dynamo_db")
    mock_ssm_service = mocker.patch("handlers.login_redirect_handler.get_ssm_parameters",
                                    side_effect=ClientError({'Error': {'code' : 500, 'message' : 'mocked error'}}, 'test'))
    response = login_redirect_handler.prepare_redirect_response(FakeWebAppClient)

    expected = ApiGatewayResponse(
        500, "Server error", "GET"
    ).create_api_gateway_response()

    assert response == expected
    mock_dynamo_service.assert_not_called()
    mock_ssm_service.assert_called_once()

def test_prepare_redirect_response_return_500_when_auth_client_failing(mocker, monkeypatch):
    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
    mock_dynamo_service = mocker.patch("handlers.login_redirect_handler.save_state_in_dynamo_db")
    mock_ssm_service = mocker.patch("handlers.login_redirect_handler.get_ssm_parameters",
                                    side_effect=InsecureTransportError())
    response = login_redirect_handler.prepare_redirect_response(FakeWebAppClient)

    expected = ApiGatewayResponse(
        500, "Server error", "GET"
    ).create_api_gateway_response()

    assert response == expected
    mock_dynamo_service.assert_not_called()
    mock_ssm_service.assert_called_once()

# def test_save_to_dynamo(mocker, monkeypatch):
#     monkeypatch.setenv("AUTH_DYNAMODB_NAME", "test_table")
#     mock_dynamo_service = mocker.patch("DynamoDBService")
#     mock_dynamo_service.return_value = FakeDynamoDBService
#     mocker.patch("time.time", return_value=1238)
#     expected_item = {"State": 'test', "TimeToExist": 1838}
#
#     login_redirect_handler.save_state_in_dynamo_db('test')
#
#     mock_dynamo_service.assert_called_with("test_table")
#     mock_dynamo_service.post_item_service.assert_called_once()
#     mock_dynamo_service.post_item_service.assert_called_with(expected_item)
def test_get_ssm_parameters(mocker):
    mock_ssm_client = mocker.Mock()
    mocker.patch("boto3.client", return_value=mock_ssm_client)
    mock_ssm_client.get_parameters.return_value=MOCK_MULTI_STRING_PARAMETERS_RESPONSE
    response = login_redirect_handler.get_ssm_parameters()

    expected = MOCK_MULTI_STRING_PARAMETERS_RESPONSE

    assert response == expected
