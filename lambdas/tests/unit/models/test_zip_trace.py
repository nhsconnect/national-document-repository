from freezegun import freeze_time
from models.zip_trace import DocumentManifestZipTrace
from tests.unit.conftest import TEST_NHS_NUMBER, TEST_UUID
from tests.unit.helpers.data.test_documents import (
    create_test_lloyd_george_doc_store_refs,
)


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
        "JobStatus": "Pending",
        "ZipFileLocation": "",
        "NhsNumber": TEST_NHS_NUMBER,
    }

    actual = DocumentManifestZipTrace(
        files_to_download=test_files_to_download, nhs_number=TEST_NHS_NUMBER
    ).model_dump(by_alias=True)

    assert actual == expected
