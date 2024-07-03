from unittest.mock import call

import pytest
from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from freezegun import freeze_time
from services.document_manifest_service import DocumentManifestService
from tests.unit.conftest import MOCK_ZIP_TRACE_TABLE, TEST_NHS_NUMBER, TEST_UUID
from tests.unit.helpers.data.s3_responses import MOCK_PRESIGNED_URL_RESPONSE
from tests.unit.helpers.data.test_documents import (
    create_test_doc_store_refs,
    create_test_lloyd_george_doc_store_refs,
)
from utils.common_query_filters import UploadCompleted
from utils.lambda_exceptions import DocumentManifestServiceException

TEST_DOC_STORE_DOCUMENT_REFS = create_test_doc_store_refs()
TEST_LLOYD_GEORGE_DOCUMENT_REFS = create_test_lloyd_george_doc_store_refs()
TEST_DOC_REFERENCE_IDs = [
    "3d8683b9-1665-40d2-8499-6e8302d507ff",
    "4d8683b9-1665-40d2-8499-6e8302d507ff",
    "5d8683b9-1665-40d2-8499-6e8302d507ff",
]


@pytest.fixture
def manifest_service(mocker, set_env):
    mocker.patch("boto3.client")
    mocker.patch("services.base.iam_service.IAMService")

    service = DocumentManifestService(TEST_NHS_NUMBER)
    mocker.patch.object(service, "s3_service")
    mocker.patch.object(service, "dynamo_service")
    mocker.patch.object(service, "document_service")
    yield service


@pytest.fixture
def mock_document_service(mocker, manifest_service):
    mock_document_service = manifest_service.document_service
    mocker.patch.object(
        mock_document_service, "fetch_available_document_references_by_type"
    )
    yield mock_document_service


@pytest.fixture
def mock_s3_service(mocker, manifest_service):
    mock_s3_service = manifest_service.s3_service
    mocker.patch.object(mock_s3_service, "create_download_presigned_url")
    mock_s3_service.create_download_presigned_url.return_value = (
        MOCK_PRESIGNED_URL_RESPONSE
    )
    yield mock_s3_service


@pytest.fixture
def mock_dynamo_service(mocker, manifest_service):
    mock_dynamo_service = manifest_service.dynamo_service
    mocker.patch.object(mock_dynamo_service, "create_item")
    yield mock_dynamo_service


@pytest.fixture
def mock_filter_documents_by_reference(mocker, manifest_service):
    yield mocker.patch.object(manifest_service, "filter_documents_by_reference")


@pytest.fixture
def mock_handle_duplicate_document_filenames(mocker, manifest_service):
    yield mocker.patch.object(manifest_service, "handle_duplicate_document_filenames")


@pytest.fixture
def mock_write_zip_trace(mocker, manifest_service):
    yield mocker.patch.object(manifest_service, "write_zip_trace")


@pytest.fixture
def mock_query_filter(mocker):
    upload_query = UploadCompleted
    filter = mocker.patch("utils.common_query_filters.UploadCompleted")
    filter.return_value = upload_query
    yield filter.return_value


def test_create_document_manifest_job_raises_exception(
    manifest_service, mock_document_service
):
    mock_document_service.fetch_available_document_references_by_type.return_value = []

    with pytest.raises(DocumentManifestServiceException) as e:
        manifest_service.create_document_manifest_job([SupportedDocumentTypes.ARF])

    assert e.value == DocumentManifestServiceException(404, LambdaError.ManifestNoDocs)


def test_create_document_manifest_job_for_arf(
    manifest_service,
    mock_query_filter,
    mock_document_service,
    mock_filter_documents_by_reference,
    mock_handle_duplicate_document_filenames,
    mock_uuid,
    mock_write_zip_trace,
):
    mock_document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOC_STORE_DOCUMENT_REFS
    )
    mock_handle_duplicate_document_filenames.return_value = TEST_DOC_STORE_DOCUMENT_REFS
    mock_write_zip_trace.return_value = TEST_UUID

    expected = TEST_UUID

    response = manifest_service.create_document_manifest_job(
        doc_types=[SupportedDocumentTypes.ARF]
    )

    mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.ARF,
        query_filter=mock_query_filter,
    )
    mock_filter_documents_by_reference.assert_not_called()
    mock_write_zip_trace.assert_called_once_with(
        {
            TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_name,
        }
    )
    assert response == expected


def test_create_document_manifest_job_for_lg(
    manifest_service,
    mock_query_filter,
    mock_document_service,
    mock_filter_documents_by_reference,
    mock_handle_duplicate_document_filenames,
    mock_uuid,
    mock_write_zip_trace,
):
    mock_document_service.fetch_available_document_references_by_type.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_handle_duplicate_document_filenames.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_write_zip_trace.return_value = TEST_UUID
    expected = TEST_UUID

    response = manifest_service.create_document_manifest_job(
        doc_types=[SupportedDocumentTypes.LG]
    )

    mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.LG,
        query_filter=mock_query_filter,
    )
    mock_filter_documents_by_reference.assert_not_called()
    mock_write_zip_trace.assert_called_once_with(
        {
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_name,
        }
    )
    assert response == expected


def test_create_document_manifest_job_for_both(
    manifest_service,
    mock_query_filter,
    mock_document_service,
    mock_filter_documents_by_reference,
    mock_handle_duplicate_document_filenames,
    mock_uuid,
    mock_write_zip_trace,
):
    manifest_service.document_service.fetch_available_document_references_by_type.side_effect = [
        TEST_LLOYD_GEORGE_DOCUMENT_REFS,
        TEST_DOC_STORE_DOCUMENT_REFS,
    ]
    mock_handle_duplicate_document_filenames.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS + TEST_DOC_STORE_DOCUMENT_REFS
    )
    mock_write_zip_trace.return_value = TEST_UUID

    expected = TEST_UUID
    expected_calls = [
        call(
            nhs_number=TEST_NHS_NUMBER,
            doc_type=SupportedDocumentTypes.LG,
            query_filter=mock_query_filter,
        ),
        call(
            nhs_number=TEST_NHS_NUMBER,
            doc_type=SupportedDocumentTypes.ARF,
            query_filter=mock_query_filter,
        ),
    ]

    response = manifest_service.create_document_manifest_job(
        doc_types=[SupportedDocumentTypes.LG, SupportedDocumentTypes.ARF]
    )

    mock_document_service.fetch_available_document_references_by_type.assert_has_calls(
        expected_calls
    )
    mock_filter_documents_by_reference.assert_not_called()
    mock_write_zip_trace.assert_called_once_with(
        {
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_name,
        }
    )
    assert response == expected


def test_create_document_manifest_job_for_arf_with_doc_references(
    manifest_service,
    mock_query_filter,
    mock_document_service,
    mock_filter_documents_by_reference,
    mock_handle_duplicate_document_filenames,
    mock_uuid,
    mock_write_zip_trace,
):
    mock_document_service.fetch_available_document_references_by_type.return_value = (
        TEST_DOC_STORE_DOCUMENT_REFS
    )
    mock_filter_documents_by_reference.return_value = TEST_DOC_STORE_DOCUMENT_REFS
    mock_handle_duplicate_document_filenames.return_value = TEST_DOC_STORE_DOCUMENT_REFS
    mock_write_zip_trace.return_value = TEST_UUID

    expected = TEST_UUID

    response = manifest_service.create_document_manifest_job(
        doc_types=[SupportedDocumentTypes.ARF],
        selected_document_references=TEST_DOC_REFERENCE_IDs,
    )

    mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.ARF,
        query_filter=mock_query_filter,
    )
    mock_filter_documents_by_reference.assert_called_once_with(
        documents=TEST_DOC_STORE_DOCUMENT_REFS,
        selected_document_references=TEST_DOC_REFERENCE_IDs,
    )
    mock_write_zip_trace.assert_called_once_with(
        {
            TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_name,
        }
    )
    assert response == expected


def test_create_document_manifest_job_for_lg_with_doc_references(
    manifest_service,
    mock_query_filter,
    mock_document_service,
    mock_filter_documents_by_reference,
    mock_handle_duplicate_document_filenames,
    mock_uuid,
    mock_write_zip_trace,
):
    mock_document_service.fetch_available_document_references_by_type.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_filter_documents_by_reference.return_value = TEST_LLOYD_GEORGE_DOCUMENT_REFS
    mock_handle_duplicate_document_filenames.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_write_zip_trace.return_value = TEST_UUID

    expected = TEST_UUID

    response = manifest_service.create_document_manifest_job(
        doc_types=[SupportedDocumentTypes.LG],
        selected_document_references=TEST_DOC_REFERENCE_IDs,
    )

    mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
        nhs_number=TEST_NHS_NUMBER,
        doc_type=SupportedDocumentTypes.LG,
        query_filter=mock_query_filter,
    )
    mock_filter_documents_by_reference.assert_called_once_with(
        documents=TEST_LLOYD_GEORGE_DOCUMENT_REFS,
        selected_document_references=TEST_DOC_REFERENCE_IDs,
    )
    mock_write_zip_trace.assert_called_once_with(
        {
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_name,
        }
    )
    assert response == expected


def test_create_document_manifest_job_for_both_with_doc_references(
    manifest_service,
    mock_query_filter,
    mock_document_service,
    mock_filter_documents_by_reference,
    mock_handle_duplicate_document_filenames,
    mock_uuid,
    mock_write_zip_trace,
):
    manifest_service.document_service.fetch_available_document_references_by_type.side_effect = [
        TEST_LLOYD_GEORGE_DOCUMENT_REFS,
        TEST_DOC_STORE_DOCUMENT_REFS,
    ]
    mock_filter_documents_by_reference.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS + TEST_DOC_STORE_DOCUMENT_REFS
    )
    mock_handle_duplicate_document_filenames.return_value = (
        TEST_LLOYD_GEORGE_DOCUMENT_REFS + TEST_DOC_STORE_DOCUMENT_REFS
    )
    mock_write_zip_trace.return_value = TEST_UUID

    expected = TEST_UUID
    expected_calls = [
        call(
            nhs_number=TEST_NHS_NUMBER,
            doc_type=SupportedDocumentTypes.LG,
            query_filter=mock_query_filter,
        ),
        call(
            nhs_number=TEST_NHS_NUMBER,
            doc_type=SupportedDocumentTypes.ARF,
            query_filter=mock_query_filter,
        ),
    ]

    response = manifest_service.create_document_manifest_job(
        doc_types=[SupportedDocumentTypes.LG, SupportedDocumentTypes.ARF],
        selected_document_references=TEST_DOC_REFERENCE_IDs,
    )

    mock_document_service.fetch_available_document_references_by_type.assert_has_calls(
        expected_calls
    )
    mock_filter_documents_by_reference.assert_called_once_with(
        documents=TEST_LLOYD_GEORGE_DOCUMENT_REFS + TEST_DOC_STORE_DOCUMENT_REFS,
        selected_document_references=TEST_DOC_REFERENCE_IDs,
    )
    mock_write_zip_trace.assert_called_once_with(
        {
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
            .file_name,
            TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[0]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[1]
            .file_name,
            TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_location: TEST_DOC_STORE_DOCUMENT_REFS[2]
            .file_name,
        }
    )
    assert response == expected


def test_filter_documents_by_reference_valid_multiple(manifest_service):
    expected = TEST_DOC_STORE_DOCUMENT_REFS[:-1]

    response = manifest_service.filter_documents_by_reference(
        documents=TEST_DOC_STORE_DOCUMENT_REFS,
        selected_document_references=TEST_DOC_REFERENCE_IDs[:-1],
    )

    assert expected == response


def test_filter_documents_by_reference_valid_singular(manifest_service):
    expected = [TEST_DOC_STORE_DOCUMENT_REFS[0]]

    response = manifest_service.filter_documents_by_reference(
        documents=TEST_DOC_STORE_DOCUMENT_REFS,
        selected_document_references=[TEST_DOC_REFERENCE_IDs[0]],
    )

    assert expected == response


def test_filter_documents_by_reference_raises_exception(manifest_service):
    with pytest.raises(DocumentManifestServiceException) as e:
        manifest_service.filter_documents_by_reference(
            documents=TEST_DOC_STORE_DOCUMENT_REFS,
            selected_document_references=["invalid_reference"],
        )

    assert e.value == DocumentManifestServiceException(
        400, LambdaError.ManifestFilterDocumentReferences
    )


def test_handle_duplicate_document_filenames(manifest_service):
    test_docs = TEST_LLOYD_GEORGE_DOCUMENT_REFS
    test_docs[0].file_name = "test.pdf"
    test_docs[1].file_name = "test.pdf"
    test_docs[2].file_name = "test.pdf"

    response = manifest_service.handle_duplicate_document_filenames(test_docs)

    assert response[0].file_name == "test.pdf"
    assert response[1].file_name == "test(2).pdf"
    assert response[2].file_name == "test(3).pdf"


@freeze_time("2024-01-01T12:00:00Z")
def test_write_zip_trace_valid(manifest_service, mock_dynamo_service, mock_uuid):
    test_docs = {
        TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
        .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[0]
        .file_name,
        TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
        .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[1]
        .file_name,
        TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
        .file_location: TEST_LLOYD_GEORGE_DOCUMENT_REFS[2]
        .file_name,
    }

    manifest_service.write_zip_trace(test_docs)

    mock_dynamo_service.create_item.assert_called_with(
        MOCK_ZIP_TRACE_TABLE,
        {
            "ID": TEST_UUID,
            "JobId": TEST_UUID,
            "Created": "2024-01-01T12:00:00Z",
            "FilesToDownload": test_docs,
            "Status": "Pending",
            "ZipFileLocation": "",
        },
    )


# def test_create_document_manifest_presigned_url_doc_store(
#     mock_service, mock_s3_service, mock_document_service
# ):
#     mock_document_service.fetch_available_document_references_by_type.return_value = (
#         TEST_DOC_STORE_DOCUMENT_REFS
#     )
#
#     response = mock_service.create_document_manifest_presigned_url(
#         [SupportedDocumentTypes.ARF]
#     )
#     assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
#     assert response == MOCK_PRESIGNED_URL_RESPONSE
#     mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
#         nhs_number=TEST_NHS_NUMBER,
#         doc_type=SupportedDocumentTypes.ARF,
#         query_filter=UploadCompleted,
#     )
#     mock_s3_service.create_download_presigned_url.assert_called_once_with(
#         s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET, file_key=mock_service.zip_file_name
#     )
#
#
# def test_create_document_manifest_presigned_url_lloyd_george(
#     mock_service, mock_s3_service, mock_document_service
# ):
#     mock_service.document_service.fetch_available_document_references_by_type.return_value = (
#         TEST_LLOYD_GEORGE_DOCUMENT_REFS
#     )
#
#     response = mock_service.create_document_manifest_presigned_url(
#         [SupportedDocumentTypes.LG]
#     )
#
#     assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
#     assert response == MOCK_PRESIGNED_URL_RESPONSE
#     mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
#         nhs_number=TEST_NHS_NUMBER,
#         doc_type=SupportedDocumentTypes.LG,
#         query_filter=UploadCompleted,
#     )
#     mock_s3_service.create_download_presigned_url.assert_called_once_with(
#         s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET, file_key=mock_service.zip_file_name
#     )
#
#
# def test_create_document_manifest_presigned_url_lloyd_george_with_file_ref(
#     mock_service, mock_s3_service, mock_document_service
# ):
#     mock_service.document_service.fetch_available_document_references_by_type.return_value = (
#         TEST_LLOYD_GEORGE_DOCUMENT_REFS
#     )
#
#     response = mock_service.create_document_manifest_presigned_url(
#         [SupportedDocumentTypes.LG], ["test_file_ref"]
#     )
#     mock_filter_doc_by_ref = (
#         UploadCompleted
#         & DynamoQueryFilterBuilder()
#         .add_condition(
#             attribute=str(DocumentReferenceMetadataFields.ID.value),
#             attr_operator=AttributeOperator.EQUAL,
#             filter_value="test_file_ref",
#         )
#         .build()
#     )
#     assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
#     assert response == MOCK_PRESIGNED_URL_RESPONSE
#     mock_document_service.fetch_available_document_references_by_type.assert_called_once_with(
#         nhs_number=TEST_NHS_NUMBER,
#         doc_type=SupportedDocumentTypes.LG,
#         query_filter=mock_filter_doc_by_ref,
#     )
#     mock_s3_service.create_download_presigned_url.assert_called_once_with(
#         s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET, file_key=mock_service.zip_file_name
#     )
#
#
# def test_create_document_manifest_presigned_url_all(
#     mock_service, mock_s3_service, mock_document_service
# ):
#     mock_service.document_service.fetch_available_document_references_by_type.side_effect = [
#         TEST_LLOYD_GEORGE_DOCUMENT_REFS,
#         TEST_DOC_STORE_DOCUMENT_REFS,
#     ]
#
#     response = mock_service.create_document_manifest_presigned_url(
#         [SupportedDocumentTypes.LG, SupportedDocumentTypes.ARF]
#     )
#
#     assert mock_service.zip_file_name == f"patient-record-{TEST_NHS_NUMBER}.zip"
#     assert response == MOCK_PRESIGNED_URL_RESPONSE
#     mock_document_service.fetch_available_document_references_by_type.assert_has_calls(
#         [
#             call(
#                 nhs_number=TEST_NHS_NUMBER,
#                 doc_type=SupportedDocumentTypes.LG,
#                 query_filter=UploadCompleted,
#             ),
#             call(
#                 nhs_number=TEST_NHS_NUMBER,
#                 doc_type=SupportedDocumentTypes.ARF,
#                 query_filter=UploadCompleted,
#             ),
#         ]
#     )
#
#     mock_s3_service.create_download_presigned_url.assert_called_once_with(
#         s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET, file_key=mock_service.zip_file_name
#     )
#
#
# def test_create_document_manifest_presigned_raises_exception_when_validation_error(
#     mock_service, validation_error
# ):
#     mock_service.document_service.fetch_available_document_references_by_type.side_effect = (
#         validation_error
#     )
#
#     with pytest.raises(DocumentManifestServiceException):
#         mock_service.create_document_manifest_presigned_url(
#             [SupportedDocumentTypes.LG, SupportedDocumentTypes.ARF]
#         )
#
#
# def test_create_document_manifest_presigned_raises_exception_when_not_all_files_uploaded(
#     mock_service, validation_error
# ):
#     mock_service.document_service.fetch_available_document_references_by_type.return_value = TEST_LLOYD_GEORGE_DOCUMENT_REFS[
#         0:1
#     ]
#
#     with pytest.raises(DocumentManifestServiceException):
#         mock_service.create_document_manifest_presigned_url([SupportedDocumentTypes.LG])
#
#
# def test_create_document_manifest_presigned_raises_exception_when_documents_empty(
#     mock_service,
# ):
#     mock_service.document_service.fetch_available_document_references_by_type.return_value = (
#         []
#     )
#
#     with pytest.raises(DocumentManifestServiceException):
#         mock_service.create_document_manifest_presigned_url(
#             [SupportedDocumentTypes.LG, SupportedDocumentTypes.ARF]
#         )
#
#
# def test_download_documents_to_be_zipped_handles_duplicate_file_names(mock_service):
#     mock_service.documents = TEST_LLOYD_GEORGE_DOCUMENT_REFS
#
#     mock_service.documents[0].file_name = "test.pdf"
#     mock_service.documents[1].file_name = "test.pdf"
#     mock_service.documents[2].file_name = "test.pdf"
#
#     mock_service.download_documents_to_be_zipped(TEST_LLOYD_GEORGE_DOCUMENT_REFS)
#
#     assert mock_service.documents[0].file_name == "test.pdf"
#     assert mock_service.documents[1].file_name == "test(2).pdf"
#     assert mock_service.documents[2].file_name == "test(3).pdf"
#
#
# def test_download_documents_to_be_zipped_calls_download_file(
#     mock_service, mock_s3_service
# ):
#     mock_service.download_documents_to_be_zipped(TEST_LLOYD_GEORGE_DOCUMENT_REFS)
#
#     assert mock_s3_service.download_file.call_count == 3
#
#
# def test_download_documents_to_be_zipped_creates_download_path(
#     mock_service, mock_s3_service
# ):
#     expected_download_path = os.path.join(
#         mock_service.temp_downloads_dir, TEST_DOC_STORE_DOCUMENT_REFS[0].file_name
#     )
#     expected_document_file_key = TEST_DOC_STORE_DOCUMENT_REFS[0].get_file_key()
#
#     mock_service.download_documents_to_be_zipped([TEST_DOC_STORE_DOCUMENT_REFS[0]])
#     mock_s3_service.download_file.assert_called_with(
#         MOCK_BUCKET, expected_document_file_key, expected_download_path
#     )
#
#
# def test_upload_zip_file(mock_service, mock_s3_service, mock_dynamo_service):
#     expected_upload_path = os.path.join(
#         mock_service.temp_output_dir, mock_service.zip_file_name
#     )
#     mock_service.upload_zip_file()
#
#     mock_s3_service.upload_file.assert_called_with(
#         file_name=expected_upload_path,
#         s3_bucket_name=MOCK_ZIP_OUTPUT_BUCKET,
#         file_key=mock_service.zip_file_name,
#     )
#
#     mock_dynamo_service.create_item.assert_called_once()
