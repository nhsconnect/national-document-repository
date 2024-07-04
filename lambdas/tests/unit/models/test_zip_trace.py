from freezegun import freeze_time
from models.zip_trace import DocumentManifestZipTrace
from tests.unit.conftest import TEST_UUID
from unit.helpers.data.test_documents import create_test_lloyd_george_doc_store_refs


@freeze_time("2024-01-01T12:00:00Z")
def test_zip_trace_serializer(mock_uuid):
    test_doc_refs = create_test_lloyd_george_doc_store_refs()
    test_files_to_download = {
        test_doc_refs[0].file_location: test_doc_refs[0].file_name,
        test_doc_refs[1].file_location: test_doc_refs[1].file_name,
        test_doc_refs[2].file_location: test_doc_refs[2].file_name,
    }

    expected = {
        "ID": TEST_UUID,
        "JobId": TEST_UUID,
        "Created": "2024-01-01T12:00:00Z",
        "FilesToDownload": test_files_to_download,
        "Status": "Pending",
        "ZipFileLocation": "",
    }

    actual = DocumentManifestZipTrace(
        FilesToDownload=test_files_to_download
    ).model_dump(by_alias=True)

    assert actual == expected
