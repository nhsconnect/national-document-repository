from unittest.mock import MagicMock

import pytest
from enums.document_status import DocumentStatus
from enums.supported_document_types import SupportedDocumentTypes
from enums.virus_scan_result import VirusScanResult
from models.document_reference import DocumentReference
from services.get_document_upload_status import GetDocumentUploadStatusService


@pytest.fixture
def mock_document_service():
    mock_service = MagicMock()
    return mock_service


@pytest.fixture
def get_document_upload_status_service(mock_document_service):
    service = GetDocumentUploadStatusService()
    service.document_service = mock_document_service
    return service


@pytest.fixture
def sample_document_references():
    doc1 = DocumentReference(
        id="doc-id-1",
        nhs_number="1234567890",
        file_name="test_file1.pdf",
        doc_status="final",
        virus_scanner_result=VirusScanResult.CLEAN,
    )

    doc2 = DocumentReference(
        id="doc-id-2",
        nhs_number="1234567890",
        file_name="test_file2.pdf",
        doc_status="final",
        virus_scanner_result=VirusScanResult.CLEAN,
    )

    doc3 = DocumentReference(
        id="doc-id-3",
        nhs_number="9876543210",  # Different NHS number
        file_name="test_file3.pdf",
        doc_status="final",
        virus_scanner_result=VirusScanResult.CLEAN,
    )

    doc4 = DocumentReference(
        id="doc-id-4",
        nhs_number="1234567890",
        file_name="test_file4.pdf",
        doc_status=DocumentStatus.CANCELLED.display,
        virus_scanner_result=VirusScanResult.INFECTED,
        deleted="",
    )

    doc5 = DocumentReference(
        id="doc-id-5",
        nhs_number="1234567890",
        file_name="test_file5.pdf",
        doc_status="preliminary",
        virus_scanner_result=VirusScanResult.CLEAN,
        deleted="2023-01-01T12:00:00.000Z",  # Deleted document
    )

    return [doc1, doc2, doc3, doc4, doc5]


def test_get_document_references_by_id_found_documents(
    get_document_upload_status_service,
    mock_document_service,
    sample_document_references,
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-1", "doc-id-2"]
    mock_document_service.get_batch_document_references_by_id.return_value = (
        sample_document_references[:2]
    )

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    mock_document_service.get_batch_document_references_by_id.assert_called_once_with(
        document_ids, SupportedDocumentTypes.LG
    )
    assert len(result) == 2
    assert result["doc-id-1"]["status"] == "final"
    assert result["doc-id-2"]["status"] == "final"
    assert "error_code" not in result["doc-id-1"]
    assert "error_code" not in result["doc-id-2"]


def test_get_document_references_by_id_not_found_documents(
    get_document_upload_status_service,
    mock_document_service,
    sample_document_references,
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-1", "non-existent-id"]
    mock_document_service.get_batch_document_references_by_id.return_value = [
        sample_document_references[0]
    ]

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    assert len(result) == 2
    assert result["doc-id-1"]["status"] == "final"
    assert result["non-existent-id"]["status"] == DocumentStatus.NOT_FOUND.display
    assert "error_code" not in result["doc-id-1"]
    assert result["non-existent-id"]["error_code"] == DocumentStatus.NOT_FOUND.code


def test_get_document_references_by_id_access_denied(
    get_document_upload_status_service,
    mock_document_service,
    sample_document_references,
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-3"]
    mock_document_service.get_batch_document_references_by_id.return_value = [
        sample_document_references[2]
    ]

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    assert len(result) == 1
    assert result["doc-id-3"]["status"] == DocumentStatus.FORBIDDEN.display
    assert result["doc-id-3"]["error_code"] == DocumentStatus.FORBIDDEN.code


def test_get_document_references_by_id_infected_document(
    get_document_upload_status_service,
    mock_document_service,
    sample_document_references,
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-4"]
    mock_document_service.get_batch_document_references_by_id.return_value = [
        sample_document_references[3]
    ]

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    assert len(result) == 1
    assert result["doc-id-4"]["status"] == DocumentStatus.INFECTED.display
    assert result["doc-id-4"]["error_code"] == DocumentStatus.INFECTED.code


def test_get_document_references_by_id_cancelled_document(
    get_document_upload_status_service, mock_document_service
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-cancelled"]

    # Create a cancelled document that is not infected
    cancelled_doc = DocumentReference(
        id="doc-id-cancelled",
        nhs_number="1234567890",
        file_name="cancelled_file.pdf",
        doc_status=DocumentStatus.CANCELLED.display,
        virus_scanner_result=VirusScanResult.ERROR,
    )

    mock_document_service.get_batch_document_references_by_id.return_value = [
        cancelled_doc
    ]

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    assert len(result) == 1
    assert result["doc-id-cancelled"]["status"] == DocumentStatus.CANCELLED.display
    assert result["doc-id-cancelled"]["error_code"] == DocumentStatus.CANCELLED.code


def test_get_document_references_by_id_deleted_document(
    get_document_upload_status_service,
    mock_document_service,
    sample_document_references,
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-5"]
    mock_document_service.get_batch_document_references_by_id.return_value = [
        sample_document_references[4]
    ]

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    assert len(result) == 0


def test_get_document_references_by_id_multiple_mixed_statuses(
    get_document_upload_status_service,
    mock_document_service,
    sample_document_references,
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-1", "doc-id-3", "doc-id-4", "doc-id-5", "non-existent-id"]
    mock_document_service.get_batch_document_references_by_id.return_value = [
        sample_document_references[0],
        sample_document_references[2],
        sample_document_references[3],
        sample_document_references[4],
    ]

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    assert len(result) == 4
    assert result["doc-id-1"]["status"] == "final"
    assert "error_code" not in result["doc-id-1"]

    assert result["doc-id-3"]["status"] == DocumentStatus.FORBIDDEN.display
    assert result["doc-id-3"]["error_code"] == DocumentStatus.FORBIDDEN.code

    assert result["doc-id-4"]["status"] == DocumentStatus.INFECTED.display
    assert result["doc-id-4"]["error_code"] == DocumentStatus.INFECTED.code

    assert result["non-existent-id"]["status"] == DocumentStatus.NOT_FOUND.display
    assert result["non-existent-id"]["error_code"] == DocumentStatus.NOT_FOUND.code

    assert "doc-id-5" not in result


def test_get_document_references_by_id_no_results(
    get_document_upload_status_service, mock_document_service
):
    nhs_number = "1234567890"
    document_ids = ["doc-id-6"]
    mock_document_service.get_batch_document_references_by_id.return_value = []

    result = get_document_upload_status_service.get_document_references_by_id(
        nhs_number, document_ids
    )

    mock_document_service.get_batch_document_references_by_id.assert_called_once_with(
        document_ids, SupportedDocumentTypes.LG
    )
    assert result["doc-id-6"]["status"] == DocumentStatus.NOT_FOUND.display
    assert result["doc-id-6"]["error_code"] == DocumentStatus.NOT_FOUND.code
