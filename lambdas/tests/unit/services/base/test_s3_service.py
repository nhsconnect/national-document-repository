import pytest
from botocore.exceptions import ClientError
from services.base.s3_service import S3Service
from tests.unit.conftest import (
    MOCK_BUCKET,
    TEST_FILE_KEY,
    TEST_FILE_NAME,
    TEST_NHS_NUMBER,
    TEST_OBJECT_KEY,
)
from tests.unit.helpers.data.s3_responses import MOCK_PRESIGNED_URL_RESPONSE
from utils.exceptions import TagNotFoundException

TEST_DOWNLOAD_PATH = "test_path"
MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": 111111000}},
    "content": [{"attachment": {"contentType": "application/pdf"}}],
    "description": "test_filename.pdf",
}


@pytest.fixture
def mock_service(mocker, set_env):
    mocker.patch("boto3.client")
    mocker.patch("services.base.iam_service.IAMService")
    service = S3Service(custom_aws_role="mock_arn_custom_role")
    yield service


@pytest.fixture()
def mock_client(mocker, mock_service):
    client = mocker.patch.object(mock_service, "client")
    yield client


@pytest.fixture()
def mock_custom_client(mocker, mock_service):
    client = mocker.patch.object(mock_service, "custom_client")
    yield client


def test_create_upload_presigned_url(mock_service, mock_custom_client):
    mock_custom_client.generate_presigned_post.return_value = (
        MOCK_PRESIGNED_URL_RESPONSE
    )
    response = mock_service.create_upload_presigned_url(MOCK_BUCKET, TEST_OBJECT_KEY)

    assert response == MOCK_PRESIGNED_URL_RESPONSE
    mock_custom_client.generate_presigned_post.assert_called_once()


def test_create_download_presigned_url(mock_service, mock_custom_client):
    mock_custom_client.generate_presigned_url.return_value = MOCK_PRESIGNED_URL_RESPONSE

    response = mock_service.create_download_presigned_url(MOCK_BUCKET, TEST_FILE_KEY)

    assert response == MOCK_PRESIGNED_URL_RESPONSE
    mock_custom_client.generate_presigned_url.assert_called_once()


def test_download_file(mock_service, mock_client):
    mock_service.download_file(MOCK_BUCKET, TEST_FILE_KEY, TEST_DOWNLOAD_PATH)

    mock_client.download_file.assert_called_once_with(
        MOCK_BUCKET, TEST_FILE_KEY, TEST_DOWNLOAD_PATH
    )


def test_upload_file(mock_service, mock_client):
    mock_service.upload_file(TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY)

    mock_client.upload_file.assert_called_with(
        TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY
    )


def test_upload_file_with_extra_args(mock_service, mock_client):
    test_extra_args = {"mock_tag": 123, "apple": "red", "banana": "true"}

    mock_service.upload_file_with_extra_args(
        TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY, test_extra_args
    )

    mock_client.upload_file.assert_called_with(
        TEST_FILE_NAME, MOCK_BUCKET, TEST_FILE_KEY, test_extra_args
    )


def test_copy_across_bucket(mock_service, mock_client):
    mock_service.copy_across_bucket(
        source_bucket="bucket_to_copy_from",
        source_file_key=TEST_FILE_KEY,
        dest_bucket="bucket_to_copy_to",
        dest_file_key=f"{TEST_NHS_NUMBER}/{TEST_OBJECT_KEY}",
    )

    mock_client.copy_object.assert_called_once_with(
        Bucket="bucket_to_copy_to",
        Key=f"{TEST_NHS_NUMBER}/{TEST_OBJECT_KEY}",
        CopySource={"Bucket": "bucket_to_copy_from", "Key": TEST_FILE_KEY},
    )


def test_delete_object(mock_service, mock_client):
    mock_service.delete_object(s3_bucket_name=MOCK_BUCKET, file_key=TEST_FILE_NAME)

    mock_client.delete_object_assert_called_once_with(
        Bucket=MOCK_BUCKET, Key=TEST_FILE_NAME
    )


def test_create_object_tag(mock_service, mock_client):
    test_tag_key = "tag_key"
    test_tag_value = "tag_name"

    mock_service.create_object_tag(
        s3_bucket_name=MOCK_BUCKET,
        file_key=TEST_FILE_NAME,
        tag_key=test_tag_key,
        tag_value=test_tag_value,
    )

    mock_client.put_object_tagging.assert_called_once_with(
        Bucket=MOCK_BUCKET,
        Key=TEST_FILE_NAME,
        Tagging={"TagSet": [{"Key": test_tag_key, "Value": test_tag_value}]},
    )


def test_get_tag_value(mock_service, mock_client):
    test_tag_key = "tag_key"
    test_tag_value = "tag_name"

    mock_response = {
        "VersionId": "mock_version",
        "TagSet": [
            {"Key": test_tag_key, "Value": test_tag_value},
            {"Key": "some_other_unrelated_tag", "Value": "abcd1234"},
        ],
    }

    mock_client.get_object_tagging.return_value = mock_response

    actual = mock_service.get_tag_value(
        s3_bucket_name=MOCK_BUCKET, file_key=TEST_FILE_NAME, tag_key=test_tag_key
    )
    expected = test_tag_value
    assert actual == expected

    mock_client.get_object_tagging.assert_called_once_with(
        Bucket=MOCK_BUCKET,
        Key=TEST_FILE_NAME,
    )


def test_get_tag_value_raises_error_when_specified_tag_is_missing(
    mock_service, mock_client
):
    test_tag_key = "tag_key"

    mock_response = {
        "VersionId": "mock_version",
        "TagSet": [
            {"Key": "some_other_unrelated_tag", "Value": "abcd1234"},
        ],
    }

    mock_client.get_object_tagging.return_value = mock_response

    with pytest.raises(TagNotFoundException):
        mock_service.get_tag_value(
            s3_bucket_name=MOCK_BUCKET, file_key=TEST_FILE_NAME, tag_key=test_tag_key
        )


def test_file_exist_on_s3_return_true_if_object_exists(mock_service, mock_client):
    mock_response = {
        "ResponseMetadata": {
            "RequestId": "mock_req",
            "HostId": "",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {},
            "RetryAttempts": 0,
        },
        "ETag": '"eb2996dae99afd8308e4c97bdb6a4178"',
        "ContentType": "application/pdf",
        "Metadata": {},
    }

    mock_client.head_object.return_value = mock_response

    expected = True
    actual = mock_service.file_exist_on_s3(
        s3_bucket_name=MOCK_BUCKET, file_key=TEST_FILE_NAME
    )
    assert actual == expected

    mock_client.head_object.assert_called_once_with(
        Bucket=MOCK_BUCKET,
        Key=TEST_FILE_NAME,
    )


def test_file_exist_on_s3_return_false_if_object_does_not_exist(
    mock_service, mock_client
):
    mock_error = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}},
        "S3:HeadObject",
    )

    mock_client.head_object.side_effect = mock_error

    expected = False
    actual = mock_service.file_exist_on_s3(
        s3_bucket_name=MOCK_BUCKET, file_key=TEST_FILE_NAME
    )

    assert actual == expected

    mock_client.head_object.assert_called_with(
        Bucket=MOCK_BUCKET,
        Key=TEST_FILE_NAME,
    )


def test_file_exist_on_s3_raises_client_error_if_unexpected_response(
    mock_service, mock_client
):
    mock_error = ClientError(
        {"Error": {"Code": "500", "Message": "Internal Server Error"}},
        "S3:HeadObject",
    )

    mock_client.head_object.side_effect = mock_error

    with pytest.raises(ClientError):
        mock_service.file_exist_on_s3(
            s3_bucket_name=MOCK_BUCKET, file_key=TEST_FILE_NAME
        )

    mock_client.head_object.assert_called_with(
        Bucket=MOCK_BUCKET,
        Key=TEST_FILE_NAME,
    )


def test_s3_service_singleton_instance(mocker):
    mocker.patch("boto3.client")

    instance_1 = S3Service()
    instance_2 = S3Service()

    assert instance_1 is instance_2
