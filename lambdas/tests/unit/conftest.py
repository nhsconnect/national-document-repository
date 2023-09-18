import pytest


@pytest.fixture
def set_env(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-2")
    monkeypatch.setenv("DOCUMENT_STORE_DYNAMODB_NAME", "test-doc-store-table")
    monkeypatch.setenv("DOCUMENT_STORE_BUCKET_NAME", "test-doc-store-bucket")
    monkeypatch.setenv("LLOYD_GEORGE_DYNAMODB_NAME", "test-lg-table")
    monkeypatch.setenv("ZIPPED_STORE_BUCKET_NAME", "test-zip-bucket")
    monkeypatch.setenv("ZIPPED_STORE_DYNAMODB_NAME", "test-zip-table")
