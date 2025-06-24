import tempfile
from io import BytesIO

import pytest
from boto3.dynamodb.conditions import Attr, ConditionBase
from botocore.exceptions import ClientError
from enums.supported_document_types import SupportedDocumentTypes
from enums.trace_status import TraceStatus
from models.document_reference import DocumentReference
from models.stitch_trace import StitchTrace
from pypdf import PdfWriter
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
MOCK_STITCHED_STREAM = BytesIO(
    b"%PDF-1.4\n%filename_of_stitched_lg_in_local_storage.pdf\n%%EOF"
)
MOCK_STITCHED_FILE_ON_S3 = f"combined_files/{MOCK_STITCHED_FILE}"
MOCK_TOTAL_FILE_SIZE = 1024 * 256
MOCK_PRESIGNED_URL = (
    f"https://{MOCK_LG_BUCKET}.s3.amazonaws.com/{MOCK_STITCHED_FILE_ON_S3}"
)

MOCK_STITCH_TRACE_OBJECT = StitchTrace(nhs_number=TEST_NHS_NUMBER, expire_at=9999999)


@pytest.fixture
def single_mock_doc():
    return build_lg_doc_ref_list([1])[0]


@pytest.fixture
def multiple_mock_docs():
    return build_lg_doc_ref_list([1, 2, 3])


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


@pytest.fixture
def mock_stream_and_stitch_documents(mocker):
    mocker.patch.object(
        LloydGeorgeStitchService,
        "stream_and_stitch_documents",
        return_value=MOCK_STITCHED_STREAM,
    )


@pytest.fixture
def mock_get_file_key_from_s3_url(mocker):
    return mocker.patch(
        "services.lloyd_george_generate_stitch_service.get_file_key_from_s3_url",
        side_effect=lambda url: url.split("/")[-1],
    )


def test_update_stitch_job_complete(stitch_service, mocker):
    stitch_service.document_service = mocker.MagicMock()

    stitch_service.update_stitch_job_complete()

    stitch_service.document_service.dynamo_service.update_item.assert_called_with(
        table_name="test_stitch_metadata",
        key_pair={"ID": MOCK_STITCH_TRACE_OBJECT.id},
        updated_fields=MOCK_STITCH_TRACE_OBJECT.model_dump(
            by_alias=True, exclude={"id"}
        ),
    )


def test_stitch_lloyd_george_record_raises_404_if_no_docs(patched_stitch_service):
    patched_stitch_service.get_lloyd_george_record_for_patient.return_value = []
    with pytest.raises(LGStitchServiceException) as e:
        patched_stitch_service.stitch_lloyd_george_record()
    assert e.value.status_code == 404


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


def test_sort_documents_by_filenames_base_case(stitch_service, multiple_mock_docs):
    lg_not_in_order = build_lg_doc_ref_list([3, 1, 2])

    expected = multiple_mock_docs
    actual = stitch_service.sort_documents_by_filenames(lg_not_in_order)

    assert actual == expected


def test_sort_documents_by_filenames_for_more_than_10_files(stitch_service):
    lg_not_in_order = build_lg_doc_ref_list(
        [6, 7, 10, 11, 12, 1, 8, 3, 4, 5, 13, 9, 2, 14, 15]
    )

    expected = build_lg_doc_ref_list(list(range(1, 15 + 1)))
    actual = stitch_service.sort_documents_by_filenames(lg_not_in_order)

    assert actual == expected


def test_sort_documents_by_filenames_logs_error_on_failure(
    stitch_service, mocker, single_mock_doc
):
    bad_doc = single_mock_doc
    bad_doc.file_name = "not_a_valid_format.pdf"

    mock_logger = mocker.patch("services.lloyd_george_generate_stitch_service.logger")

    with pytest.raises(LGStitchServiceException):
        stitch_service.sort_documents_by_filenames([bad_doc])

    mock_logger.error.assert_called_once()


def test_get_most_recent_created_date(stitch_service):
    lg_record = build_lg_doc_ref_list(page_numbers=[1, 2, 3])
    lg_record[2].created = "2024-12-14T16:46:07.678657Z"

    expected = "2024-12-14T16:46:07.678657Z"
    actual = stitch_service.get_most_recent_created_date(lg_record)

    assert actual == expected


def test_upload_stitched_lg_record_and_retrieve_presign_url(mock_s3, stitch_service):
    stitch_service.upload_stitched_lg_record(
        stitched_lg_stream=MOCK_STITCHED_STREAM,
        filename_on_bucket=MOCK_STITCHED_FILE_ON_S3,
    )
    mock_s3.upload_file_obj.assert_called_with(
        file_obj=MOCK_STITCHED_STREAM,
        s3_bucket_name=MOCK_LG_BUCKET,
        file_key=MOCK_STITCHED_FILE_ON_S3,
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


def test_update_trace_status(stitch_service, mocker):
    stitch_service.document_service = mocker.MagicMock()

    stitch_service.update_trace_status(TraceStatus.FAILED)

    stitch_service.document_service.dynamo_service.update_item.assert_called_with(
        table_name="test_stitch_metadata",
        key_pair={"ID": MOCK_STITCH_TRACE_OBJECT.id},
        updated_fields={"JobStatus": TraceStatus.FAILED},
    )


def create_mock_pdf_stream() -> BytesIO:
    buffer = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(buffer)
    buffer.seek(0)
    return buffer


def test_stream_and_stitch_documents(stitch_service, mocker, multiple_mock_docs):
    mock_get_file_key = mocker.patch(
        "services.lloyd_george_generate_stitch_service.get_file_key_from_s3_url",
        return_value="mocked_file_key.pdf",
    )

    mock_s3_service = mocker.Mock()
    mock_s3_service.stream_s3_object_to_memory.side_effect = [
        create_mock_pdf_stream(),
        create_mock_pdf_stream(),
        create_mock_pdf_stream(),
    ]

    stitch_service.s3_service = mock_s3_service
    stitch_service.lloyd_george_bucket_name = MOCK_LG_BUCKET

    documents = multiple_mock_docs

    result = stitch_service.stream_and_stitch_documents(documents)

    assert isinstance(result, BytesIO)
    result.seek(0)
    assert result.read(4) == b"%PDF"
    assert mock_s3_service.stream_s3_object_to_memory.call_count == 3
    assert mock_get_file_key.call_count == 3


def test_prepare_documents_for_stitching(
    patched_stitch_service, mocker, multiple_mock_docs
):
    mock_documents = multiple_mock_docs

    mock_update_trace_status = mocker.patch.object(
        patched_stitch_service, "update_trace_status"
    )
    mock_sort_documents = mocker.patch.object(
        patched_stitch_service, "sort_documents_by_filenames"
    )
    mock_get_recent_date = mocker.patch.object(
        patched_stitch_service, "get_most_recent_created_date"
    )

    patched_stitch_service.prepare_documents_for_stitching(mock_documents)

    mock_update_trace_status.assert_called_once_with(TraceStatus.PROCESSING)
    mock_sort_documents.assert_called_once_with(mock_documents)
    mock_get_recent_date.assert_called_once()


def test_stitch_lloyd_george_record(patched_stitch_service, mocker, multiple_mock_docs):
    mock_docs = multiple_mock_docs
    patched_stitch_service.get_lloyd_george_record_for_patient = mocker.Mock(
        return_value=mock_docs
    )
    patched_stitch_service.prepare_documents_for_stitching = mocker.Mock()
    patched_stitch_service.stream_and_stitch_documents = mocker.Mock()
    patched_stitch_service.upload_stitched_lg_record = mocker.Mock()

    mock_stream = BytesIO(b"%PDF-1.4\nmock\n%%EOF")
    patched_stitch_service.stream_and_stitch_documents.return_value = mock_stream

    patched_stitch_service.stitch_file_name = "test_file"
    patched_stitch_service.combined_file_folder = "combined_files"
    patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.prepare_documents_for_stitching.assert_called_once_with(
        mock_docs
    )
    patched_stitch_service.stream_and_stitch_documents.assert_called_once()
    patched_stitch_service.upload_stitched_lg_record.assert_called_once()


def test_stitch_lloyd_george_record_single_file(
    patched_stitch_service, mocker, single_mock_doc
):
    mock_doc = single_mock_doc
    patched_stitch_service.get_lloyd_george_record_for_patient = mocker.Mock(
        return_value=[mock_doc]
    )
    patched_stitch_service.prepare_documents_for_stitching = mocker.Mock()
    patched_stitch_service.get_total_file_size_in_bytes = mocker.Mock(return_value=1234)

    patched_stitch_service.stream_and_stitch_documents = mocker.Mock()

    # Act
    patched_stitch_service.stitch_lloyd_george_record()

    patched_stitch_service.get_lloyd_george_record_for_patient.assert_called_once()
    patched_stitch_service.prepare_documents_for_stitching.assert_called_once_with(
        [mock_doc]
    )
    patched_stitch_service.get_total_file_size_in_bytes.assert_called_once_with(
        document=mock_doc
    )

    patched_stitch_service.stream_and_stitch_documents.assert_not_called()


def test_get_total_file_size_in_bytes(stitch_service, mocker, single_mock_doc):
    mock_doc = single_mock_doc
    mock_s3_service = mocker.Mock()
    stitch_service.s3_service = mock_s3_service

    stitch_service.get_total_file_size_in_bytes(document=mock_doc)

    mock_s3_service.get_file_size.assert_called_once_with(
        mock_doc.get_file_bucket(), mock_doc.get_file_key()
    )


def test_fetch_pdf_calls_expected_methods(stitch_service, mocker, single_mock_doc):
    mock_get_file_key = mocker.patch(
        "services.lloyd_george_generate_stitch_service.get_file_key_from_s3_url"
    )
    mock_stream_s3 = mocker.patch.object(
        stitch_service.s3_service, "stream_s3_object_to_memory"
    )
    mocker.patch("services.lloyd_george_generate_stitch_service.pikepdf.Pdf.open")

    stitch_service.fetch_pdf(single_mock_doc)

    assert mock_get_file_key.called
    assert mock_stream_s3.called
