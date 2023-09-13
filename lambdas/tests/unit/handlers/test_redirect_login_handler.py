from handlers import login_redirect_handler
from tests.unit.helpers.ssm_responses import MOCK_MULTI_STRING_PARAMETERS_RESPONSE

from lambdas.utils.lambda_response import ApiGatewayResponse


def test_return_302_with_correct_headers(mocker, monkeypatch):
    mock_ssm_client = mocker.Mock()
    mock_oauth_client = mocker.Mock()

    mocker.patch("boto3.client", return_value=mock_ssm_client)
    mock_ssm_client.get_parameters.return_value=MOCK_MULTI_STRING_PARAMETERS_RESPONSE
    monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")

    mocker.patch("oauthlib.oauth2.Client", return_value=mock_oauth_client)
    return_url = "https://www.string_value_1.com?" \
                 "response_type=code&" \
                 "client_id=1122121212&" \
                 "redirect_uri=https%3A%2F%2Fdev.testexample.com%&" \
                 "state=test1state&" \
                 "scope=openid+profile+nationalrbacaccess+associatedorgs"
    mock_oauth_client.prepare_authorization_request.return_value = (return_url, "", "")
    response = login_redirect_handler.lambda_handler(event=None, context=None)
    location_header = {"Location": return_url}
    expected = ApiGatewayResponse(
        302, "", "GET"
    ).create_api_gateway_response(headers=location_header)
    assert response == expected

def test_return_500_when_boto3_client_failing():
    pass

def test_return_500_when_auth_client_failing():
    pass
def test_save_to_dynamo():
    pass