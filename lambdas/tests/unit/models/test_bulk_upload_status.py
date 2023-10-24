
from models.bulk_upload_status import (FailedUpload, SuccessfulUpload,
                                       UploadStatus)

MOCK_DATA_COMPLETE_UPLOAD = {
    "ID": "719ca7a7-9c30-48f3-a472-c3daaf30d548",
    "nhs_number": "9000000009",
    "timestamp": "1698146661",
    "upload_status": "complete",
    "file_location_in_bucket": "s3://lloyd-george-bucket/9000000009/test-key-123",
}

MOCK_DATA_FAILED_UPLOAD = {
    "ID": "719ca7a7-9c30-48f3-a472-c3daaf30e975",
    "nhs_number": "9000000025",
    "timestamp": "169814650",
    "upload_status": "failed",
    "failure_reason": "File name not matching Lloyd George naming convention",
    "file_path_of_failed_file": "s3://staging-bucket/9000000025/invalid_filename.pdf",
}


def test_parse_json_into_successful_upload():
    actual = UploadStatus.validate_python(MOCK_DATA_COMPLETE_UPLOAD)
    expected = SuccessfulUpload(
        ID="719ca7a7-9c30-48f3-a472-c3daaf30d548",
        nhs_number="9000000009",
        timestamp="1698146661",
        upload_status="complete",
        file_location_in_bucket="s3://lloyd-george-bucket/9000000009/test-key-123",
    )

    assert isinstance(actual, SuccessfulUpload)
    assert actual == expected


def test_parse_json_into_failed_upload():
    actual = UploadStatus.validate_python(MOCK_DATA_FAILED_UPLOAD)
    expected = FailedUpload(
        ID="719ca7a7-9c30-48f3-a472-c3daaf30e975",
        nhs_number="9000000025",
        timestamp="169814650",
        upload_status="failed",
        failure_reason="File name not matching Lloyd George naming convention",
        file_path_of_failed_file="/9000000025/invalid_filename.pdf",
    )

    assert isinstance(actual, FailedUpload)
    assert actual == expected
