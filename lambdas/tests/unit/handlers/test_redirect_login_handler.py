from unittest.mock import MagicMock, patch
import pytest
import boto3
from handlers import login_redirect_handler

@pytest.fixture
def mock_boto3_ssm():
    return MagicMock()


def test_got_302_with_correct_headers():
    with patch.object(boto3, "client", return_value=mock_boto3_ssm):
        mock_boto3_ssm.get_parameters.return_value = MOCK_RESPONSE
        login_redirect_handler.lambda_handler(event=None, context=None)
        pass
