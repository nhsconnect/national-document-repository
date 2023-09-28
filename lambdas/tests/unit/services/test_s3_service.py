from services.s3_service import S3Service
from tests.unit.conftest import (MOCK_BUCKET, TEST_FILE_KEY, TEST_FILE_NAME,
                                 TEST_OBJECT_KEY)

MOCK_PRESIGNED_POST_RESPONSE = {
    "url": "https://ndr-dev-document-store.s3.amazonaws.com/",
    "fields": {
        "key": "0abed67c-0d0b-4a11-a600-a2f19ee61281",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "ASIAXYSUA44VTL5M5LWL/20230911/eu-west-2/s3/aws4_request",
        "x-amz-date": "20230911T084756Z",
        "x-amz-security-token": "test-security-token",
        "policy": "test-policy",
        "x-amz-signature": "b6afcf8b27fc883b0e0a25a789dd2ab272ea4c605a8c68267f73641d7471132f",
    },
}

MOCK_PRESIGNED_URL_RESPONSE = {
    "url": "https://ndr-dev-document-store.s3.amazonaws.com/",
    "fields": {
        "key": "0abed67c-0d0b-4a11-a600-a2f19ee61281",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "ASIAXYSUA44VTL5M5LWL/20230911/eu-west-2/s3/aws4_request",
        "x-amz-date": "20230911T084756Z",
        "x-amz-expires": "1800",
        "x-amz-signed-headers": "test-host",
        "x-amz-signature": "test-signature",
    },
}

TEST_DOWNLOAD_PATH = "test_path"
MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": 111111000}},
    "content": [{"attachment": {"contentType": "application/pdf"}}],
    "description": "test_filename.pdf",
}


def test_create_document_presigned_url(set_env, mocker):
    mock_generate_presigned_post = mocker.patch(
        "botocore.signers.generate_presigned_post"
    )

    mock_generate_presigned_post.return_value = MOCK_PRESIGNED_POST_RESPONSE

    service = S3Service()

    return_value = service.create_document_presigned_url_handler(
        MOCK_BUCKET, TEST_OBJECT_KEY
    )

    assert return_value == MOCK_PRESIGNED_POST_RESPONSE
    mock_generate_presigned_post.assert_called_once()


def test_create_zip_presigned_url(set_env, mocker):
    mock_generate_presigned_url = mocker.patch(
        "botocore.signers.generate_presigned_url"
    )

    mock_generate_presigned_url.return_value = MOCK_PRESIGNED_URL_RESPONSE

    service = S3Service()

    return_value = service.create_download_presigned_url(MOCK_BUCKET, TEST_FILE_KEY)

    assert return_value == MOCK_PRESIGNED_URL_RESPONSE
    mock_generate_presigned_url.assert_called_once()


def test_download_file(mocker):
    mocker.patch("boto3.client")
    service = S3Service()
    mock_download_file = mocker.patch.object(service.client, "download_file")
    service.download_file(MOCK_BUCKET, TEST_FILE_KEY, TEST_DOWNLOAD_PATH)

    mock_download_file.assert_called_once_with(
        MOCK_BUCKET, TEST_FILE_KEY, TEST_DOWNLOAD_PATH
    )


def test_upload_file(mocker):
    mocker.patch("boto3.client")
    service = S3Service()
    mock_upload_file = mocker.patch.object(service.client, "upload_file")

    service.upload_file(TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY)

    mock_upload_file.assert_called_once_with(TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY)


def test_upload_file_with_tags(mocker):
    mocker.patch("boto3.client")
    service = S3Service()
    mock_upload_file = mocker.patch.object(service.client, "upload_file")

    test_tags = {"mock_tag": 123, "apple": "red", "banana": "true"}

    service.upload_file_with_tags(TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY, test_tags)

    mock_upload_file.assert_called_once_with(TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY, {
        "Tagging": "mock_tag=123&apple=red&banana=true"
    })
