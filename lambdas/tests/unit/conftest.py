import pytest
import json

REGION_NAME = "eu-west-2"

MOCK_TABLE_NAME = "test-table"
MOCK_BUCKET = "test_s3_bucket"

MOCK_ARF_TABLE_NAME = "test_arf_dynamoDB_table"
MOCK_LG_TABLE_NAME = "test_lg_dynamoDB_table"
MOCK_ARF_BUCKET = "test_arf_s3_bucket"
MOCK_LG_BUCKET = "test_lg_s3_bucket"
MOCK_ZIP_OUTPUT_BUCKET = "test_s3_output_bucket"
MOCK_ZIP_TRACE_TABLE = "test_zip_table"

TEST_NHS_NUMBER = "1111111111"
TEST_OBJECT_KEY = "1234-4567-8912-HSDF-TEST"
TEST_FILE_KEY = "test_file_key"
TEST_FILE_NAME = "test.pdf"
TEST_VIRUS_SCANNER_RESULT = "not_scanned"
TEST_DOCUMENT_LOCATION = f"s3://{MOCK_BUCKET}/{TEST_OBJECT_KEY}"


@pytest.fixture
def set_env(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", REGION_NAME)
    monkeypatch.setenv("DOCUMENT_STORE_DYNAMODB_NAME", MOCK_ARF_TABLE_NAME)
    monkeypatch.setenv("DOCUMENT_STORE_BUCKET_NAME", MOCK_ARF_BUCKET)
    monkeypatch.setenv("LLOYD_GEORGE_BUCKET_NAME", MOCK_LG_BUCKET)
    monkeypatch.setenv("LLOYD_GEORGE_DYNAMODB_NAME", MOCK_LG_TABLE_NAME)
    monkeypatch.setenv("DYNAMODB_TABLE_LIST", json.dumps([MOCK_ARF_TABLE_NAME, MOCK_LG_TABLE_NAME]))
    monkeypatch.setenv("ZIPPED_STORE_BUCKET_NAME", MOCK_ZIP_OUTPUT_BUCKET)
    monkeypatch.setenv("ZIPPED_STORE_DYNAMODB_NAME", MOCK_ZIP_TRACE_TABLE)
