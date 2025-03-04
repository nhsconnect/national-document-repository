import pytest
from msgpack.fallback import BytesIO


@pytest.fixture
def mock_download_fileobj():
    """
    Mock function to add as a side effect to handle calls to boto3.s3_client.download_fileobj

    Args:
        s3_object_data: A dictionary of s3 objects keys and
            the BytesIO object holding the byte data of the file you want to mock a download for
        Bucket: Passed to boto3.s3_client.download_fileobj
        Key: Passed to boto3.s3_client.download_fileobj
        Fileobj: Passed to boto3.s3_client.download_fileobj

    Returns:
        Return function to handle calls to boto3.s3_client.download_fileobj
    """

    def _mock_download_fileobj(
        s3_object_data: dict[str, BytesIO], Bucket: str, Key: str, Fileobj: BytesIO
    ):
        if Key in s3_object_data:
            Fileobj.write(s3_object_data[Key].read())
        Fileobj.seek(0)

    return _mock_download_fileobj
