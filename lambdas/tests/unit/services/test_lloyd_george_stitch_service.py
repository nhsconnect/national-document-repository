import tempfile

import pytest
from boto3.dynamodb.conditions import Attr, ConditionBase
from botocore.exceptions import ClientError
from enums.supported_document_types import SupportedDocumentTypes
from enums.trace_status import TraceStatus
from models.document_reference import DocumentReference
from models.stitch_trace import StitchTrace
from pypdf.errors import PdfReadError
from services.document_service import DocumentService
from services.lloyd_george_generate_stitch_service import LloydGeorgeStitchService
from tests.unit.conftest import MOCK_LG_BUCKET, TEST_NHS_NUMBER, TEST_UUID
from utils.dynamo_utils import filter_uploaded_docs_and_recently_uploading_docs
from utils.lambda_exceptions import LGStitchServiceException


def build_lg_doc_ref_list(page_numbers: list[int]) -> list[DocumentReference]:
    total_page_number = len(page_numbers)
    return [build_lg_doc_ref(page_no, total_page_number) for page_no in page_numbers]


def build_lg_doc_ref(
    curr_page_number: int,
    total_page_number: int,
    uploaded: str = "True",
    uploading: str = "False",
) -> DocumentReference:
    file_name = (
        f"{curr_page_number}of{total_page_number}_"
        f"Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[30-12-2019].pdf"
    )
    return DocumentReference.model_validate(
        {
            "ID": "3d8683b9-1665-40d2-8499-6e8302d507ff",
            "ContentType": "type",
            "Created": "2023-08-23T13:38:04.095Z",
            "Deleted": "",
            "FileLocation": f"s3://{MOCK_LG_BUCKET}/{TEST_NHS_NUMBER}/{TEST_UUID}",
            "FileName": file_name,
            "NhsNumber": TEST_NHS_NUMBER,
            "VirusScannerResult": "Clean",
            "CurrentGpOds": "Y12345",
            "Uploaded": uploaded,
            "Uploading": uploading,
            "LastUpdated": 1704110400,
        },
    )


MOCK_CLIENT_ERROR = ClientError(
    {"Error": {"Code": "500", "Message": "test error"}}, "testing"
)
MOCK_LLOYD_GEORGE_DOCUMENT_REFS = build_lg_doc_ref_list(page_numbers=[1, 2, 3])
MOCK_TEMP_FOLDER = "/tmp"
MOCK_DOWNLOADED_LLOYD_GEORGE_FILES = [
    f"{MOCK_TEMP_FOLDER}/mock_downloaded_file{i}" for i in range(1, 3 + 1)
]
MOCK_STITCHED_FILE = "filename_of_stitched_lg_in_local_storage.pdf"
MOCK_STITCHED_FILE_ON_S3 = f"combined_files/{MOCK_STITCHED_FILE}"
MOCK_TOTAL_FILE_SIZE = 1024 * 256
MOCK_PRESIGNED_URL = (
    f"https://{MOCK_LG_BUCKET}.s3.amazonaws.com/{MOCK_STITCHED_FILE_ON_S3}"
)

MOCK_STITCH_TRACE_OBJECT = StitchTrace(nhs_number=TEST_NHS_NUMBER, expire_at=9999999)


@pytest.fixture
def stitch_service(set_env):
    yield LloydGeorgeStitchService(MOCK_STITCH_TRACE_OBJECT)


@pytest.fixture
def patched_stitch_service(set_env, mocker):
    mocker.patch.object(
        LloydGeorgeStitchService,
        "get_lloyd_george_record_for_patient",
        return_value=MOCK_LLOYD_GEORGE_DOCUMENT_REFS,
    )
    mocker.patch.object(
        LloydGeorgeStitchService,
        "download_lloyd_george_files",
        return_value=MOCK_DOWNLOADED_LLOYD_GEORGE_FILES,
    )
    mocker.patch("services.lloyd_george_generate_stitch_service.S3Service")
    mocker.patch("services.lloyd_george_generate_stitch_service.DocumentService")
    mocker.patch.object(
        LloydGeorgeStitchService,
        "upload_stitched_lg_record",
    )
    mocker.patch.object(
        LloydGeorgeStitchService,
        "update_trace_status",
    )
    mocker.patch.object(
        LloydGeorgeStitchService,
        "sort_documents_by_filenames",
        return_value=MOCK_LLOYD_GEORGE_DOCUMENT_REFS,
    )
    mocker.patch.object(
        LloydGeorgeStitchService,
        "get_most_recent_created_date",
    )
    yield LloydGeorgeStitchService(MOCK_STITCH_TRACE_OBJECT)


@pytest.fixture
def mock_fetch_doc_ref_by_type(mocker):
    def mocked_method(
        nhs_number: str, doc_type: str, query_filter: Attr | ConditionBase
    ):
        if nhs_number == TEST_NHS_NUMBER and doc_type == SupportedDocumentTypes.LG:
            return MOCK_LLOYD_GEORGE_DOCUMENT_REFS
        return []

    yield mocker.patch.object(
        DocumentService,
        "fetch_available_document_references_by_type",
        side_effect=mocked_method,
    )


@pytest.fixture
def mock_s3(mocker, mock_tempfile):
    mocked_instance = mocker.patch(
        "services.lloyd_george_generate_stitch_service.S3Service"
    ).return_value
    mocked_instance.create_download_presigned_url.return_value = MOCK_PRESIGNED_URL
    yield mocked_instance


@pytest.fixture
def mock_tempfile(mocker):
    mocker.patch("shutil.rmtree")
    yield mocker.patch.object(tempfile, "mkdtemp", return_value=MOCK_TEMP_FOLDER)


@pytest.fixture
def mock_stitch_pdf(mocker):
    yield mocker.patch(
        "services.lloyd_george_generate_stitch_service.stitch_pdf",
        return_value=MOCK_STITCHED_FILE,
    )


@pytest.fixture
def mock_get_total_file_size_in_bytes(mocker):
    yield mocker.patch.object(
        LloydGeorgeStitchService,
        "get_total_file_size_in_bytes",
        return_value=MOCK_TOTAL_FILE_SIZE,
    )


def test_stitch_lloyd_george_record_happy_path(
    mock_tempfile,
    mock_stitch_pdf,
    mock_get_total_file_size_in_bytes,
    patched_stitch_service,
):
    patched_stitch_service.get_most_recent_created_date.return_value = (
        "2023-08-23T13:38:04.095Z"
    )

    patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.update_trace_status.assert_called_with(
        TraceStatus.PROCESSING
    )
    patched_stitch_service.sort_documents_by_filenames.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    patched_stitch_service.download_lloyd_george_files.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_stitch_pdf.assert_called_with(
        MOCK_DOWNLOADED_LLOYD_GEORGE_FILES, MOCK_TEMP_FOLDER
    )
    mock_get_total_file_size_in_bytes.assert_called_once()
    patched_stitch_service.upload_stitched_lg_record.assert_called_once()
    patched_stitch_service.get_most_recent_created_date.assert_called_once()
    assert patched_stitch_service.stitch_trace_object.number_of_files == 3
    assert (
        patched_stitch_service.stitch_trace_object.total_file_size_in_byte
        == MOCK_TOTAL_FILE_SIZE
    )
    assert (
        patched_stitch_service.stitch_trace_object.file_last_updated
        == "2023-08-23T13:38:04.095Z"
    )


def test_stitch_lloyd_george_record_raise_404_error_if_no_record_for_patient(
    mock_tempfile,
    mock_stitch_pdf,
    mock_get_total_file_size_in_bytes,
    patched_stitch_service,
):

    patched_stitch_service.get_lloyd_george_record_for_patient.return_value = None

    with pytest.raises(LGStitchServiceException):
        patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.update_trace_status.assert_not_called()
    patched_stitch_service.sort_documents_by_filenames.assert_not_called()
    patched_stitch_service.download_lloyd_george_files.assert_not_called()
    mock_get_total_file_size_in_bytes.assert_not_called()
    patched_stitch_service.upload_stitched_lg_record.assert_not_called()
    patched_stitch_service.get_most_recent_created_date.assert_not_called()
    mock_stitch_pdf.assert_not_called()


def test_stitch_lloyd_george_record_raise_500_error_if_failed_to_get_dynamodb_record(
    mock_tempfile,
    mock_stitch_pdf,
    mock_get_total_file_size_in_bytes,
    patched_stitch_service,
):

    patched_stitch_service.get_lloyd_george_record_for_patient.side_effect = (
        MOCK_CLIENT_ERROR
    )

    with pytest.raises(LGStitchServiceException):
        patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.update_trace_status.assert_not_called()
    patched_stitch_service.sort_documents_by_filenames.assert_not_called()
    patched_stitch_service.download_lloyd_george_files.assert_not_called()
    mock_get_total_file_size_in_bytes.assert_not_called()
    patched_stitch_service.upload_stitched_lg_record.assert_not_called()
    patched_stitch_service.get_most_recent_created_date.assert_not_called()
    mock_stitch_pdf.assert_not_called()


def test_stitch_lloyd_george_record_raise_500_error_if_failed_to_download_lg_files(
    mock_tempfile,
    mock_stitch_pdf,
    mock_get_total_file_size_in_bytes,
    patched_stitch_service,
):
    patched_stitch_service.download_lloyd_george_files.side_effect = MOCK_CLIENT_ERROR

    with pytest.raises(LGStitchServiceException):
        patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.update_trace_status.assert_called_with(
        TraceStatus.PROCESSING
    )
    patched_stitch_service.sort_documents_by_filenames.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    patched_stitch_service.download_lloyd_george_files.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_get_total_file_size_in_bytes.assert_not_called()
    patched_stitch_service.upload_stitched_lg_record.assert_not_called()
    patched_stitch_service.get_most_recent_created_date.assert_not_called()
    mock_stitch_pdf.assert_not_called()


def test_stitch_lloyd_george_record_raise_500_error_if_failed_to_stitch_pdf(
    mock_tempfile,
    mock_stitch_pdf,
    mock_get_total_file_size_in_bytes,
    patched_stitch_service,
):
    mock_stitch_pdf.side_effect = PdfReadError()

    with pytest.raises(LGStitchServiceException) as e:
        patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.update_trace_status.assert_called_with(
        TraceStatus.PROCESSING
    )
    patched_stitch_service.sort_documents_by_filenames.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    patched_stitch_service.download_lloyd_george_files.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_get_total_file_size_in_bytes.assert_not_called()
    patched_stitch_service.upload_stitched_lg_record.assert_not_called()
    patched_stitch_service.get_most_recent_created_date.assert_not_called()

    assert e.value.status_code == 500
    assert e.value.message == "Unable to return stitched pdf file due to internal error"


def test_stitch_lloyd_george_record_raise_500_error_if_failed_to_upload_stitched_pdf(
    mock_tempfile,
    mock_stitch_pdf,
    mock_get_total_file_size_in_bytes,
    patched_stitch_service,
):
    mock_s3_error = ClientError({"error": "some S3 error"}, "s3:PutObject")
    patched_stitch_service.upload_stitched_lg_record.side_effect = mock_s3_error

    with pytest.raises(LGStitchServiceException) as e:
        patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.update_trace_status.assert_called_with(
        TraceStatus.PROCESSING
    )
    patched_stitch_service.sort_documents_by_filenames.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    patched_stitch_service.download_lloyd_george_files.assert_called_with(
        MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    )
    mock_get_total_file_size_in_bytes.assert_called_once()
    patched_stitch_service.upload_stitched_lg_record.assert_called_once()
    patched_stitch_service.get_most_recent_created_date.assert_called_once()

    assert e.value.status_code == 500
    assert e.value.message == "Unable to return stitched pdf file due to internal error"


def test_get_lloyd_george_record_for_patient(
    stitch_service, mock_fetch_doc_ref_by_type
):
    mock_filters = filter_uploaded_docs_and_recently_uploading_docs()

    expected = MOCK_LLOYD_GEORGE_DOCUMENT_REFS
    actual = stitch_service.get_lloyd_george_record_for_patient()

    assert actual == expected
    mock_fetch_doc_ref_by_type.assert_called_with(
        TEST_NHS_NUMBER, SupportedDocumentTypes.LG, query_filter=mock_filters
    )


def test_sort_documents_by_filenames_base_case(stitch_service):
    lg_not_in_order = build_lg_doc_ref_list([3, 1, 2])

    expected = build_lg_doc_ref_list([1, 2, 3])
    actual = stitch_service.sort_documents_by_filenames(lg_not_in_order)

    assert actual == expected


def test_sort_documents_by_filenames_for_more_than_10_files(stitch_service):
    lg_not_in_order = build_lg_doc_ref_list(
        [6, 7, 10, 11, 12, 1, 8, 3, 4, 5, 13, 9, 2, 14, 15]
    )

    expected = build_lg_doc_ref_list(list(range(1, 15 + 1)))
    actual = stitch_service.sort_documents_by_filenames(lg_not_in_order)

    assert actual == expected


def test_download_lloyd_george_files(mock_s3, stitch_service, mock_uuid):
    expected_file_path_on_s3 = f"{TEST_NHS_NUMBER}/{TEST_UUID}"
    expected_downloaded_file = f"/tmp/{mock_uuid}"

    expected = [expected_downloaded_file] * 3
    actual = stitch_service.download_lloyd_george_files(MOCK_LLOYD_GEORGE_DOCUMENT_REFS)

    assert actual == expected

    assert mock_s3.download_file.call_count == len(MOCK_LLOYD_GEORGE_DOCUMENT_REFS)
    mock_s3.download_file.assert_called_with(
        MOCK_LG_BUCKET, expected_file_path_on_s3, expected_downloaded_file
    )


def test_download_lloyd_george_files_raise_error_when_failed_to_download(
    mock_s3, stitch_service
):
    mock_error = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}},
        "S3:HeadObject",
    )
    mock_s3.download_file.side_effect = mock_error

    with pytest.raises(ClientError):
        stitch_service.download_lloyd_george_files(MOCK_LLOYD_GEORGE_DOCUMENT_REFS)


def test_get_most_recent_created_date(stitch_service):
    lg_record = build_lg_doc_ref_list(page_numbers=[1, 2, 3])
    lg_record[2].created = "2024-12-14T16:46:07.678657Z"

    expected = "2024-12-14T16:46:07.678657Z"
    actual = stitch_service.get_most_recent_created_date(lg_record)

    assert actual == expected


def test_get_total_file_size(mocker, stitch_service):
    mocker.patch("os.path.getsize", side_effect=[19000, 20000, 21000])

    expected = 60000
    actual = stitch_service.get_total_file_size_in_bytes(
        ["file1.pdf", "file2.pdf", "file3.pdf"]
    )

    assert actual == expected


def test_upload_stitched_lg_record_and_retrieve_presign_url(mock_s3, stitch_service):
    stitch_service.upload_stitched_lg_record(
        stitched_lg_record=MOCK_STITCHED_FILE,
        filename_on_bucket=MOCK_STITCHED_FILE_ON_S3,
    )

    mock_s3.upload_file_with_extra_args.assert_called_with(
        file_key=MOCK_STITCHED_FILE_ON_S3,
        file_name=MOCK_STITCHED_FILE,
        s3_bucket_name=MOCK_LG_BUCKET,
        extra_args={
            "Tagging": "autodelete=true",
            "ContentDisposition": "inline",
            "ContentType": "application/pdf",
        },
    )


def test_handle_stitch_request(patched_stitch_service, mocker):
    patched_stitch_service.stitch_lloyd_george_record = mocker.MagicMock()
    patched_stitch_service.update_stitch_job_complete = mocker.MagicMock()

    patched_stitch_service.handle_stitch_request()

    patched_stitch_service.stitch_lloyd_george_record.assert_called_once()
    patched_stitch_service.update_stitch_job_complete.assert_called_once()


def test_update_stitch_job_complete(patched_stitch_service):
    patched_stitch_service.update_stitch_job_complete()

    patched_stitch_service.document_service.dynamo_service.update_item.assert_called_with(
        "test_stitch_metadata",
        MOCK_STITCH_TRACE_OBJECT.id,
        MOCK_STITCH_TRACE_OBJECT.model_dump(by_alias=True, exclude={"id"}),
    )


def test_update_trace_status(stitch_service, mocker):
    stitch_service.document_service = mocker.MagicMock()

    stitch_service.update_trace_status(TraceStatus.FAILED)

    stitch_service.document_service.dynamo_service.update_item.assert_called_with(
        "test_stitch_metadata",
        MOCK_STITCH_TRACE_OBJECT.id,
        {"JobStatus": TraceStatus.FAILED},
    )
