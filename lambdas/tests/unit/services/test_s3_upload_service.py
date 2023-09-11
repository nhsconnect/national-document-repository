import os

import pytest

from services.s3_upload_service import S3UploadService

MOCK_PRESIGNED_POST_RESPONSE = {
    "url": "https://ndr-dev-document-store.s3.amazonaws.com/",
    "fields": {
        "key": "0abed67c-0d0b-4a11-a600-a2f19ee61281",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "ASIAXYSUA44VTL5M5LWL/20230911/eu-west-2/s3/aws4_request",
        "x-amz-date": "20230911T084756Z",
        "x-amz-security-token": "IQoJb3JpZ2luX2VjEBEaCWV1LXdlc3QtMiJHMEUCIQCclJOwERVB2YedLEBJ+qPE/SyrH8DH3mki8aZov2Kd5QIgSf3oh0ZjCZY5H0BQpUhyVQEPL2xOlNCDjQMaLpc0PR4q7QII6v//////////ARABGgw1MzM4MjU5MDY0NzUiDDJCWucUhstAJno6RSrBAtTLbMPabTepneY7Q4wcCNVhxvvhNGyAhS4e2/PepiiACWI9EqYfkDv/k/h1nkPCIrVg83ooY+sbEEbBbyP6n2vjLdgxMwU6HLL6fgb14fmLEMFpgGRUQFa0YX8D6XIRMyeNbelNwi+QzaN+EuVw5nVDElI06Wm+SWZbselpOtqkgVLiVp2D1eVkp67ErLrI+2LUe6EMi70/H+AaBmDTSv3YyPFnQB7Msktwbc0kYomtdL2NufWSK8yjmgDsGMn5XYsg7sOrTQq0Fj9oqerfOFW+hGZlqCFF9+cxJsrsiClUiIPoiKTCHwVE9ROwLxIppUcpZulqQ9KAe+NgW+RqQ6qSmrqMS4qo4jK5T9dRB8tA2PXCXVN0Ghs/RtCG3qpwByA7HonOqrwshLv0FXo0mf3MBD4eX847C20MSFykNxa6VzC5qPunBjqeAZINjnR1217GGtnjL0RlcTwMnPyFSEh5XH34UwOG0XO8Y29jm0Vessm97Idg9n1uHMex3ABOEnQJM0f5DyAdl9EF1xVm2jok3p9S058ufGLK/nA5bIciqWAdF7AfXJfdz2pQ9lhhdP+3DWkN9VWNXUpvF0xtdKZhcZWl5yj1MsRs7sPyLEslASM7h3lDPn7nvvq5piaSjvFd9K6Z3/C9",
        "policy": "eyJleHBpcmF0aW9uIjogIjIwMjMtMDktMTFUMDk6MTc6NTZaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAibmRyLWRldi1kb2N1bWVudC1zdG9yZSJ9LCB7ImtleSI6ICIwYWJlZDY3Yy0wZDBiLTRhMTEtYTYwMC1hMmYxOWVlNjEyODEifSwgeyJ4LWFtei1hbGdvcml0aG0iOiAiQVdTNC1ITUFDLVNIQTI1NiJ9LCB7IngtYW16LWNyZWRlbnRpYWwiOiAiQVNJQVhZU1VBNDRWVEw1TTVMV0wvMjAyMzA5MTEvZXUtd2VzdC0yL3MzL2F3czRfcmVxdWVzdCJ9LCB7IngtYW16LWRhdGUiOiAiMjAyMzA5MTFUMDg0NzU2WiJ9LCB7IngtYW16LXNlY3VyaXR5LXRva2VuIjogIklRb0piM0pwWjJsdVgyVmpFQkVhQ1dWMUxYZGxjM1F0TWlKSE1FVUNJUUNjbEpPd0VSVkIyWWVkTEVCSitxUEUvU3lySDhESDNta2k4YVpvdjJLZDVRSWdTZjNvaDBaakNaWTVIMEJRcFVoeVZRRVBMMnhPbE5DRGpRTWFMcGMwUFI0cTdRSUk2di8vLy8vLy8vLy9BUkFCR2d3MU16TTRNalU1TURZME56VWlEREpDV3VjVWhzdEFKbm82UlNyQkF0VExiTVBhYlRlcG5lWTdRNHdjQ05WaHh2dmhOR3lBaFM0ZTIvUGVwaWlBQ1dJOUVxWWZrRHYvay9oMW5rUENJclZnODNvb1krc2JFRWJCYnlQNm4ydmpMZGd4TXdVNkhMTDZmZ2IxNGZtTEVNRnBnR1JVUUZhMFlYOEQ2WElSTXllTmJlbE53aStRemFOK0V1Vnc1blZERWxJMDZXbStTV1pic2VscE90cWtnVkxpVnAyRDFlVmtwNjdFckxySSsyTFVlNkVNaTcwL0grQWFCbURUU3YzWXlQRm5RQjdNc2t0d2JjMGtZb210ZEwyTnVmV1NLOHlqbWdEc0dNbjVYWXNnN3NPclRRcTBGajlvcWVyZk9GVytoR1pscUNGRjkrY3hKc3JzaUNsVWlJUG9pS1RDSHdWRTlST3dMeElwcFVjcFp1bHFROUtBZStOZ1crUnFRNnFTbXJxTVM0cW80aks1VDlkUkI4dEEyUFhDWFZOMEdocy9SdENHM3Fwd0J5QTdIb25PcXJ3c2hMdjBGWG8wbWYzTUJENGVYODQ3QzIwTVNGeWtOeGE2VnpDNXFQdW5CanFlQVpJTmpuUjEyMTdHR3RuakwwUmxjVHdNblB5RlNFaDVYSDM0VXdPRzBYTzhZMjlqbTBWZXNzbTk3SWRnOW4xdUhNZXgzQUJPRW5RSk0wZjVEeUFkbDlFRjF4Vm0yam9rM3A5UzA1OHVmR0xLL25BNWJJY2lxV0FkRjdBZlhKZmR6MnBROWxoaGRQKzNEV2tOOVZXTlhVcHZGMHh0ZEtaaGNaV2w1eWoxTXNSczdzUHlMRXNsQVNNN2gzbERQbjdudnZxNXBpYVNqdkZkOUs2WjMvQzkifV19",
        "x-amz-signature": "b6afcf8b27fc883b0e0a25a789dd2ab272ea4c605a8c68267f73641d7471132f"
    }
}

REGION_NAME = "eu-west-2"
MOCK_BUCKET = "test_s3_bucket"
MOCK_DYNAMODB = "test_dynamoDB_table"
TEST_OBJECT_KEY = "1234-4567-8912-HSDF-TEST"
TEST_DOCUMENT_LOCATION = f"s3://{MOCK_BUCKET}/{TEST_OBJECT_KEY}"
MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": 111111000}},
    "content": [{"attachment": {"contentType": "application/pdf"}}],
    "description": "test_filename.pdf",
}

os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = MOCK_DYNAMODB


def test_create_presigned_url(mocker):
    mock_generate_presigned_post = mocker.patch(
        "botocore.signers.generate_presigned_post"
    )

    mock_generate_presigned_post.return_value = MOCK_PRESIGNED_POST_RESPONSE

    service = S3UploadService(MOCK_BUCKET)

    return_value = service.create_document_presigned_url_handler(
        TEST_OBJECT_KEY
    )

    assert return_value == MOCK_PRESIGNED_POST_RESPONSE
    mock_generate_presigned_post.assert_called_once()
