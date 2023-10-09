import os

import boto3
import pytest

from unittest.mock import MagicMock, patch

from pytest_mock import mocker

from enums.supported_document_types import SupportedDocumentTypes
from helpers.data.dynamo_responses import MOCK_EMPTY_RESPONSE
from lambdas.services.manifest_dynamo_service import ManifestDynamoService


@pytest.fixture
def nhs_number():
    return "9000000009"


def test_only_retrieves_documents_from_lloyd_george_table(nhs_number):
    expected_table = "expected_table_name"
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = expected_table
    os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = "no-table"

    with patch.object(boto3, "resource", return_value=MagicMock()) as mock_dynamo:
        mock_table = MagicMock()
        mock_dynamo.return_value.Table.return_value = mock_table
        mock_table.query.return_value = MOCK_EMPTY_RESPONSE
        result = ManifestDynamoService().discover_uploaded_documents(nhs_number, SupportedDocumentTypes.LG)

        mock_dynamo.return_value.Table.assert_called_with(expected_table)

        assert len(result) == 0

# def retrieves_all_documents_for_an_nhs_number():
