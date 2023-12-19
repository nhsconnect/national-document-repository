import pytest

from enums.virus_scan_result import VirusScanResult
from repositories.bulk_upload.bulk_upload_s3_repository import BulkUploadS3Repository
from services.s3_service import S3Service
from tests.unit.helpers.data.bulk_upload.test_data import TEST_STAGING_METADATA
from utils.exceptions import TagNotFoundException, VirusScanNoResultException, DocumentInfectedException


@pytest.fixture
def repo_under_test(mocker, set_env):
    repo = BulkUploadS3Repository()
    mocker.patch.object(repo, "s3_repository")
    yield repo

@pytest.fixture
def mock_file_path_cache():
    mock_file_path_cache = {}
    for file in TEST_STAGING_METADATA.files:
        mock_file_path_cache[file.file_path] = file.file_path.lstrip("/")
    return mock_file_path_cache


def test_check_virus_result_raise_no_error_when_all_files_are_clean(
        repo_under_test, set_env, caplog, mock_file_path_cache
):

    repo_under_test.s3_repository.get_tag_value.return_value = VirusScanResult.CLEAN

    repo_under_test.check_virus_result(TEST_STAGING_METADATA, mock_file_path_cache)

    expected_log = f"Verified that all documents for patient {TEST_STAGING_METADATA.nhs_number} are clean."
    actual_log = caplog.records[-1].msg
    assert actual_log == expected_log

def test_check_virus_result_raise_VirusScanNoResultException_when_one_file_not_scanned(
        repo_under_test, set_env, mock_file_path_cache
):
    repo_under_test.s3_repository.get_tag_value.side_effect = [
        VirusScanResult.CLEAN,
        VirusScanResult.CLEAN,
        TagNotFoundException,  # the 3rd file is not scanned yet
    ]

    with pytest.raises(VirusScanNoResultException):
        repo_under_test.check_virus_result(TEST_STAGING_METADATA, mock_file_path_cache)


def test_check_virus_result_raise_DocumentInfectedException_when_one_file_was_infected(
        repo_under_test, set_env, mock_file_path_cache
):
    repo_under_test.s3_repository.get_tag_value.side_effect = [
        VirusScanResult.CLEAN,
        VirusScanResult.INFECTED,
        VirusScanResult.CLEAN,
    ]

    with pytest.raises(DocumentInfectedException):
        repo_under_test.check_virus_result(TEST_STAGING_METADATA)


def test_check_virus_result_raise_S3FileNotFoundException_when_one_file_not_exist_in_bucket(
        set_env, mocker
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    mock_s3_exception = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
        "GetObjectTagging",
    )

    service.s3_service.get_tag_value.side_effect = [
        VirusScanResult.CLEAN,
        VirusScanResult.CLEAN,
        mock_s3_exception,
    ]

    with pytest.raises(S3FileNotFoundException):
        service.check_virus_result(TEST_STAGING_METADATA)

def test_check_virus_result_raise_VirusScanFailedException_for_special_cases(
        set_env, mocker
):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.resolve_source_file_path(TEST_STAGING_METADATA)

    cases_to_test_for = [
        VirusScanResult.UNSCANNABLE,
        VirusScanResult.ERROR,
        VirusScanResult.INFECTED_ALLOWED,
        "some_other_unexpected_value",
    ]

    for tag_value in cases_to_test_for:
        service.s3_service.get_tag_value.return_value = tag_value
        with pytest.raises(VirusScanFailedException):
            service.check_virus_result(TEST_STAGING_METADATA)


def test_remove_ingested_file_from_source_bucket(set_env, service_under_test):
    service = BulkUploadService()

    mock_source_file_keys = [
        "9000000009/1of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
        "9000000009/2of2_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
    ]
    service.source_bucket_files_in_transaction = mock_source_file_keys

    expected_deletion_calls = [
        call(s3_bucket_name=MOCK_LG_STAGING_STORE_BUCKET, file_key=file_key)
        for file_key in mock_source_file_keys
    ]

    service_under_test.remove_ingested_file_from_source_bucket()

    service_under_test.s3_service.delete_object.assert_has_calls(expected_deletion_calls)

def test_rollback_transaction(set_env, mocker, mock_uuid):
    service = BulkUploadService()
    service.s3_service = mocker.MagicMock()
    service.dynamo_repository = mocker.MagicMock()

    service.dynamo_records_in_transaction = TEST_DOCUMENT_REFERENCE_LIST
    service.dest_bucket_files_in_transaction = [
        f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_1",
        f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_2",
    ]

    service.rollback_transaction()

    service.dynamo_repository.delete_item.assert_called_with(
        table_name=MOCK_LG_TABLE_NAME, key={"ID": mock_uuid}
    )
    assert service.dynamo_repository.delete_item.call_count == len(
        TEST_DOCUMENT_REFERENCE_LIST
    )

    service.s3_service.delete_object.assert_any_call(
        s3_bucket_name=MOCK_LG_BUCKET,
        file_key=f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_1",
    )
    service.s3_service.delete_object.assert_any_call(
        s3_bucket_name=MOCK_LG_BUCKET,
        file_key=f"{TEST_NHS_NUMBER_FOR_BULK_UPLOAD}/mock_uuid_2",
    )
    assert service.s3_service.delete_object.call_count == 2

def test_create_lg_records_and_copy_files_keep_track_of_successfully_ingested_files(
        set_env, mocker, mock_uuid, service_under_test
):
    service_under_test.convert_to_document_reference = mocker.MagicMock(
        return_value=TEST_DOCUMENT_REFERENCE
    )
    service_under_test.resolve_source_file_path(TEST_STAGING_METADATA)
    expected = [
        service_under_test.strip_leading_slash(file.file_path)
        for file in TEST_STAGING_METADATA.files
    ]

    service_under_test.create_lg_records_and_copy_files(TEST_STAGING_METADATA)

    actual = service_under_test.source_bucket_files_in_transaction

    assert actual == expected