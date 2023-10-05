import os
import pytest

from unittest.mock import MagicMock
from lambdas.services.LloydGeorgeManifestDynamoService import LloydGeorgeManifestDynamoService

@pytest.fixture
def mock_boto3_dynamo():
    return MagicMock()

def test_only_retrieves_documents_from_lloyd_george_table():
    expected_table = "expected_table_name"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = expected_table

    query_service = LloydGeorgeManifestDynamoService()
    query_service.query_lloyd_george_documents()

    mock_boto3_dynamo.assertCalledOnceWith(expected_table)

# def retrieves_all_documents_for_an_nhs_number():
