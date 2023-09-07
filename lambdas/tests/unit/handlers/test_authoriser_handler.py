import jwt

import lambdas.handlers.authoriser_handler as auth_lambda


def test_token():
    test_json = {
        "test" : "test2",
        "user_role" : "GP"
    }
    private_key = b"teststetst"
    token = jwt.encode(test_json, private_key, algorithm="RS256")
    event = {'authorizationToken' : token}
    response = auth_lambda.lambda_handler(event=event)
    assert test_json == response
