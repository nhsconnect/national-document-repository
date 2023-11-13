import json
from unittest import mock

import pytest

REGION_NAME = "eu-west-2"

MOCK_TABLE_NAME = "test-table"
MOCK_BUCKET = "test_s3_bucket"

MOCK_ARF_TABLE_NAME_ENV_NAME = "DOCUMENT_STORE_DYNAMODB_NAME"
MOCK_ARF_BUCKET_ENV_NAME = "DOCUMENT_STORE_BUCKET_NAME"

MOCK_LG_TABLE_NAME_ENV_NAME = "LLOYD_GEORGE_DYNAMODB_NAME"
MOCK_LG_BUCKET_ENV_NAME = "LLOYD_GEORGE_BUCKET_NAME"

MOCK_ZIP_OUTPUT_BUCKET_ENV_NAME = "ZIPPED_STORE_BUCKET_NAME"
MOCK_ZIP_TRACE_TABLE_ENV_NAME = "ZIPPED_STORE_DYNAMODB_NAME"

MOCK_LG_STAGING_STORE_BUCKET_ENV_NAME = "STAGING_STORE_BUCKET_NAME"
MOCK_LG_METADATA_SQS_QUEUE_ENV_NAME = "METADATA_SQS_QUEUE_URL"
MOCK_LG_INVALID_SQS_QUEUE_ENV_NAME = "INVALID_SQS_QUEUE_URL"
MOCK_LG_BULK_UPLOAD_DYNAMO_ENV_NAME = "BULK_UPLOAD_DYNAMODB_NAME"

MOCK_AUTH_STATE_TABLE_NAME_ENV_NAME = "AUTH_STATE_TABLE_NAME"
MOCK_AUTH_SESSION_TABLE_NAME_ENV_NAME = "AUTH_SESSION_TABLE_NAME"
MOCK_OIDC_CALLBACK_URL_ENV_NAME = "OIDC_CALLBACK_URL"
MOCK_OIDC_ISSUER_URL_ENV_NAME = "OIDC_ISSUER_URL"
MOCK_OIDC_TOKEN_URL_ENV_NAME = "OIDC_TOKEN_URL"
MOCK_OIDC_USER_INFO_URL_ENV_NAME = "OIDC_USER_INFO_URL"
MOCK_OIDC_JWKS_URL_ENV_NAME = "OIDC_JWKS_URL"
MOCK_OIDC_CLIENT_ID_ENV_NAME = "OIDC_CLIENT_ID"
MOCK_OIDC_CLIENT_SECRET_ENV_NAME = "OIDC_CLIENT_SECRET"
MOCK_WORKSPACE_ENV_NAME = "WORKSPACE"
MOCK_JWT_PUBLIC_KEY_NAME = "SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"

MOCK_ARF_TABLE_NAME = "test_arf_dynamoDB_table"
MOCK_LG_TABLE_NAME = "test_lg_dynamoDB_table"
MOCK_BULK_REPORT_TABLE_NAME = "test_report_dynamoDB_table"
MOCK_ARF_BUCKET = "test_arf_s3_bucket"
MOCK_LG_BUCKET = "test_lg_s3_bucket"
MOCK_ZIP_OUTPUT_BUCKET = "test_s3_output_bucket"
MOCK_ZIP_TRACE_TABLE = "test_zip_table"
MOCK_LG_STAGING_STORE_BUCKET = "test_staging_bulk_store"
MOCK_LG_METADATA_SQS_QUEUE = "test_bulk_upload_metadata_queue"
MOCK_LG_INVALID_SQS_QUEUE = "INVALID_SQS_QUEUE_URL"

TEST_NHS_NUMBER = "9000000009"
TEST_OBJECT_KEY = "1234-4567-8912-HSDF-TEST"
TEST_FILE_KEY = "test_file_key"
TEST_FILE_NAME = "test.pdf"
TEST_VIRUS_SCANNER_RESULT = "not_scanned"
TEST_DOCUMENT_LOCATION = f"s3://{MOCK_BUCKET}/{TEST_OBJECT_KEY}"

AUTH_STATE_TABLE_NAME = "test_state_table"
AUTH_SESSION_TABLE_NAME = "test_session_table"
OIDC_CALLBACK_URL = "https://fake-url.com"
OIDC_ISSUER_URL = "https://fake-url.com"
OIDC_TOKEN_URL = "https://fake-url.com"
OIDC_USER_INFO_URL = "https://fake-url.com"
OIDC_JWKS_URL = "https://fake-url.com"
OIDC_CLIENT_ID = "client-id"
OIDC_CLIENT_SECRET = "client-secret-shhhhhh"
WORKSPACE = "dev"
JWT_PUBLIC_KEY = "mock_public_key"


@pytest.fixture
def set_env(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", REGION_NAME)
    monkeypatch.setenv(MOCK_ARF_TABLE_NAME_ENV_NAME, MOCK_ARF_TABLE_NAME)
    monkeypatch.setenv(MOCK_ARF_BUCKET_ENV_NAME, MOCK_ARF_BUCKET)
    monkeypatch.setenv(MOCK_LG_TABLE_NAME_ENV_NAME, MOCK_LG_TABLE_NAME)
    monkeypatch.setenv(MOCK_LG_BUCKET_ENV_NAME, MOCK_LG_BUCKET)
    monkeypatch.setenv(
        "DYNAMODB_TABLE_LIST", json.dumps([MOCK_ARF_TABLE_NAME, MOCK_LG_TABLE_NAME])
    )
    monkeypatch.setenv(MOCK_ZIP_OUTPUT_BUCKET_ENV_NAME, MOCK_ZIP_OUTPUT_BUCKET)
    monkeypatch.setenv(MOCK_ZIP_TRACE_TABLE_ENV_NAME, MOCK_ZIP_TRACE_TABLE)
    monkeypatch.setenv(
        MOCK_LG_STAGING_STORE_BUCKET_ENV_NAME, MOCK_LG_STAGING_STORE_BUCKET
    )
    monkeypatch.setenv(MOCK_LG_METADATA_SQS_QUEUE_ENV_NAME, MOCK_LG_METADATA_SQS_QUEUE)
    monkeypatch.setenv(MOCK_LG_INVALID_SQS_QUEUE_ENV_NAME, MOCK_LG_INVALID_SQS_QUEUE)
    monkeypatch.setenv(MOCK_AUTH_STATE_TABLE_NAME_ENV_NAME, AUTH_STATE_TABLE_NAME)
    monkeypatch.setenv(MOCK_AUTH_SESSION_TABLE_NAME_ENV_NAME, AUTH_SESSION_TABLE_NAME)
    monkeypatch.setenv(MOCK_OIDC_CALLBACK_URL_ENV_NAME, OIDC_CALLBACK_URL)
    monkeypatch.setenv(MOCK_OIDC_CLIENT_ID_ENV_NAME, OIDC_CLIENT_ID)
    monkeypatch.setenv(MOCK_WORKSPACE_ENV_NAME, WORKSPACE)
    monkeypatch.setenv(MOCK_LG_BULK_UPLOAD_DYNAMO_ENV_NAME, MOCK_BULK_REPORT_TABLE_NAME)
    monkeypatch.setenv(MOCK_OIDC_ISSUER_URL_ENV_NAME, OIDC_USER_INFO_URL)
    monkeypatch.setenv(MOCK_OIDC_TOKEN_URL_ENV_NAME, OIDC_TOKEN_URL)
    monkeypatch.setenv(MOCK_OIDC_USER_INFO_URL_ENV_NAME, OIDC_USER_INFO_URL)
    monkeypatch.setenv(MOCK_OIDC_JWKS_URL_ENV_NAME, OIDC_JWKS_URL)
    monkeypatch.setenv(MOCK_OIDC_CLIENT_SECRET_ENV_NAME, OIDC_CLIENT_SECRET)
    monkeypatch.setenv(MOCK_JWT_PUBLIC_KEY_NAME, JWT_PUBLIC_KEY)


@pytest.fixture(scope="session", autouse=True)
def logger_mock():
    with mock.patch("utils.audit_logging_setup.SensitiveAuditService.emit") as _fixture:
        yield _fixture
