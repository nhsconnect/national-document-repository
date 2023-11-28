import pytest
from models.lambda_response import LambdaResponse, LambdaResponseError


@pytest.fixture
def lambda_response():
    return LambdaResponse(status=200, message="test message")


def test_lambda_response_build_response_with_errors(lambda_response):
    response = lambda_response.build_response()

    assert response.get("status") == 200
    assert response.get("message") == "test message"
    assert response.get("errors") is None


def test_lambda_response_build_response_without_errors(lambda_response):
    lambda_response.status = 400
    error = LambdaResponseError(type="test type", message="test error message")
    lambda_response.errors = [error]

    response = lambda_response.build_response()

    assert response.get("status") == 400
    assert response.get("message") == "test message"
    assert response.get("errors") == [error.model_dump()]
