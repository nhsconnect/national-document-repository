from unittest.mock import MagicMock

from handlers import login_redirect_handler
from tests.unit.helpers.ssm_responses import MOCK_MULTI_STRING_PARAMETERS_RESPONSE

from lambdas.utils.lambda_response import ApiGatewayResponse


def test_return_302_with_correct_headers(mocker, monkeypatch):
    mock_ssm_client = mocker.Mock()
    mock_oauth_client = mocker.Mock()
    mock_oauth_client2 = mocker.Mock()

    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")

    mocker.patch("boto3.client", return_value=mock_ssm_client)
    # mocker.patch("oauthlib.oauth2.Client.state", return_value="test1state", new_callable=mocker.PropertyMock)
    mocker.patch("oauthlib.oauth2.Client", return_value=mock_oauth_client2)
    mocker.patch("oauthlib.oauth2.WebApplicationClient", return_value=mock_oauth_client)
    mock_dynamo_client = mocker.patch("handlers.login_redirect_handler.save_state_in_dynamo_db")

    mock_ssm_client.get_parameters.return_value=MOCK_MULTI_STRING_PARAMETERS_RESPONSE

    return_url = "https://www.string_value_1.com?" \
                 "response_type=code&" \
                 "client_id=1122121212&" \
                 "redirect_uri=https%3A%2F%2Fwww.testexample.com%&" \
                 "state=test1state&" \
                 "scope=openid+profile+nationalrbacaccess+associatedorgs"
    mocker.patch("oauthlib.oauth2.Client.prepare_authorization_request", return_value=(return_url, "", ""))

    response = login_redirect_handler.lambda_handler(event=None, context=None)
    location_header = {"Location": return_url}
    expected = ApiGatewayResponse(
        302, "", "GET"
    ).create_api_gateway_response(headers=location_header)

    assert response == expected
    mock_dynamo_client.assert_called_with("test1state")

def test_return_500_when_boto3_client_failing():
    pass

def test_return_500_when_auth_client_failing():
    pass

def test_save_to_dynamo():
    pass

# monkeypatch.setenv("AUTH_DYNAMODB_NAME", "test_table")
# item = {"State": "test1state", "TimeToExist": 1834}
# mock_dynamo_client.post_item_service.return_value = ""
# mocker.patch("services.dynamo_services.DynamoDBService", return_value=mock_dynamo_client)
# mocker.patch("time.time", return_value=1234)
# mocker.patch("services.dynamo_services.DynamoDBService.post_item_service", return_value="")