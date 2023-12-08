from handlers.authoriser_handler import lambda_handler
from utils.exceptions import AuthorisationException

MOCK_METHOD_ARN_PREFIX = "arn:aws:execute-api:eu-west-2:fake_arn:fake_api_endpoint/dev"
TEST_PUBLIC_KEY = "test_public_key"
DENY_ALL_POLICY = {
    "Statement": [
        {
            "Action": "execute-api:Invoke",
            "Effect": "Deny",
            "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/*/*"],
        }
    ],
    "Version": "2012-10-17",
}


def test_valid_gp_admin_token_return_allow_policy(set_env, context, mocker):
    expected_allow_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Allow",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchDocumentReferences"],
            }
        ],
        "Version": "2012-10-17",
    }
    mock_auth_service = mocker.patch(
        "services.authoriser_service.AuthoriserService.auth_request", return_value=True
    )
    auth_token = "valid_gp_admin_token"
    test_event = {
        "authorizationToken": auth_token,
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchDocumentReferences",
    }

    response = lambda_handler(event=test_event, context=context)

    assert response["policyDocument"] == expected_allow_policy
    mock_auth_service.assert_called_once()


def test_valid_pcse_token_return_allow_policy(set_env, mocker, context):
    expected_allow_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Allow",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient"],
            }
        ],
        "Version": "2012-10-17",
    }

    test_event = {
        "authorizationToken": "valid_pcse_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }
    mock_auth_service = mocker.patch(
        "services.authoriser_service.AuthoriserService.auth_request", return_value=True
    )

    response = lambda_handler(test_event, context=context)

    assert response["policyDocument"] == expected_allow_policy
    mock_auth_service.assert_called_once()


def test_valid_gp_admin_token_return_deny_policy(set_env, context, mocker):
    expected_allow_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Deny",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchDocumentReferences"],
            }
        ],
        "Version": "2012-10-17",
    }
    mock_auth_service = mocker.patch(
        "services.authoriser_service.AuthoriserService.auth_request", return_value=False
    )
    auth_token = "valid_gp_admin_token"
    test_event = {
        "authorizationToken": auth_token,
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchDocumentReferences",
    }

    response = lambda_handler(event=test_event, context=context)

    assert response["policyDocument"] == expected_allow_policy
    mock_auth_service.assert_called_once()


def test_valid_pcse_token_return_deny_policy(set_env, mocker, context):
    expected_allow_policy = {
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": "Deny",
                "Resource": [f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient"],
            }
        ],
        "Version": "2012-10-17",
    }

    test_event = {
        "authorizationToken": "valid_pcse_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }
    mock_auth_service = mocker.patch(
        "services.authoriser_service.AuthoriserService.auth_request", return_value=False
    )

    response = lambda_handler(test_event, context=context)

    assert response["policyDocument"] == expected_allow_policy
    mock_auth_service.assert_called_once()


def test_return_deny_all_policy_pcse_user_when_auth_exception(set_env, mocker, context):
    mock_auth_service = mocker.patch(
        "services.authoriser_service.AuthoriserService.auth_request",
        side_effect=AuthorisationException(),
    )

    test_event = {
        "authorizationToken": "valid_pcse_token",
        "methodArn": f"{MOCK_METHOD_ARN_PREFIX}/GET/SearchPatient",
    }

    response = lambda_handler(test_event, context=context)

    assert response["policyDocument"] == DENY_ALL_POLICY
    mock_auth_service.assert_called_once()
