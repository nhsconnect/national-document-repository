from datetime import datetime

from models.bulk_upload_status import (FailedUpload, SuccessfulUpload,
                                       UploadStatus, UploadStatusList)

MOCK_DATA_COMPLETE_UPLOAD = {
    "ID": "719ca7a7-9c30-48f3-a472-c3daaf30d548",
    "NhsNumber": "9000000009",
    "Timestamp": "1698146661",
    "Date": "2023-10-24",
    "UploadStatus": "complete",
    "FilePath": "/9000000009/1of1_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[25-12-2019]",
}

MOCK_DATA_FAILED_UPLOAD = {
    "ID": "719ca7a7-9c30-48f3-a472-c3daaf30e975",
    "NhsNumber": "9000000025",
    "Timestamp": "1698109408",
    "Date": "2023-10-24",
    "UploadStatus": "failed",
    "FailureReason": "File name not matching Lloyd George naming convention",
    "FilePath": "/9000000025/invalid_filename.pdf",
}


def test_parse_json_into_successful_upload():
    expected = SuccessfulUpload(
        ID="719ca7a7-9c30-48f3-a472-c3daaf30d548",
        nhs_number="9000000009",
        timestamp="1698146661",
        date="2023-10-24",
        upload_status="complete",
        file_path="/9000000009/1of1_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[25-12-2019]",
    )

    actual = UploadStatus.validate_python(MOCK_DATA_COMPLETE_UPLOAD)

    assert isinstance(actual, SuccessfulUpload)
    assert actual == expected


def test_parse_json_into_failed_upload():
    expected = FailedUpload(
        ID="719ca7a7-9c30-48f3-a472-c3daaf30e975",
        nhs_number="9000000025",
        timestamp="1698109408",
        date="2023-10-24",
        upload_status="failed",
        failure_reason="File name not matching Lloyd George naming convention",
        file_path="/9000000025/invalid_filename.pdf",
    )

    actual = UploadStatus.validate_python(MOCK_DATA_FAILED_UPLOAD)

    assert isinstance(actual, FailedUpload)
    assert actual == expected


def test_parsing_a_list_of_record():
    items = [
        MOCK_DATA_COMPLETE_UPLOAD,
        MOCK_DATA_FAILED_UPLOAD,
        MOCK_DATA_COMPLETE_UPLOAD,
    ]

    actual = UploadStatusList.validate_python(items)

    assert isinstance(actual[0], SuccessfulUpload)
    assert isinstance(actual[1], FailedUpload)
    assert isinstance(actual[2], SuccessfulUpload)


def test_ids_and_timestamp_are_auto_populated_if_not_given(mocker):
    mocker.patch(
        "models.bulk_upload_status.now", return_value=datetime(2023, 10, 20, 10, 25)
    )
    mocker.patch("uuid.uuid4", return_value="mocked_uuid")

    upload_status = SuccessfulUpload(
        nhs_number="9000000009",
        file_path="/9000000009/1of1_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[25-12-2019]",
    )

    assert upload_status.date == "2023-10-20"
    assert upload_status.timestamp == "1697793900.0"
    assert upload_status.id == "mocked_uuid"
    assert upload_status.upload_status == "complete"
    print(upload_status.model_dump())

    upload_status_failed = FailedUpload(
        nhs_number="9000000009",
        failure_reason="File name not matching Lloyd George name convention",
        file_path="/9000000009/1of1_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[25-12-2019]",
    )

    assert upload_status_failed.date == "2023-10-20"
    assert upload_status_failed.timestamp == "1697793900.0"
    assert upload_status_failed.id == "mocked_uuid"
    assert upload_status_failed.upload_status == "failed"
