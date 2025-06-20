import json

import pytest
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.snomed_codes import SnomedCodes
from models.fhir.R4.fhir_document_reference import (
    DocumentReference as FhirDocumentReference,
)
from services.post_fhir_document_reference_service import (
    PostFhirDocumentReferenceService,
)
from tests.unit.conftest import (
    EXPECTED_PARSED_PATIENT_BASE_CASE as mock_pds_patient_details,
)
from utils.exceptions import PatientNotFoundException
from utils.lambda_exceptions import CreateDocumentRefException


@pytest.fixture
def mock_pds_service_fetch(mocker):
    mock_service_object = mocker.MagicMock()
    mocker.patch(
        "services.post_fhir_document_reference_service.get_pds_service",
        return_value=mock_service_object,
    )
    mock_service_object.fetch_patient_details.return_value = mock_pds_patient_details


@pytest.fixture
def mock_service(set_env, mocker, mock_pds_service_fetch):
    mock_s3 = mocker.patch("services.post_fhir_document_reference_service.S3Service")
    mock_dynamo = mocker.patch(
        "services.post_fhir_document_reference_service.DynamoDBService"
    )
    service = PostFhirDocumentReferenceService()
    service.s3_service = mock_s3.return_value
    service.dynamo_service = mock_dynamo.return_value

    yield service


@pytest.fixture
def valid_fhir_doc():
    return json.dumps(
        {
            "resourceType": "DocumentReference",
            "docStatus": "final",
            "status": "current",
            "subject": {
                "identifier": {
                    "system": "https://fhir.nhs.uk/Id/nhs-number",
                    "value": "9000000009",
                }
            },
            "type": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": SnomedCodes.LLOYD_GEORGE.value.code,
                        "display": SnomedCodes.LLOYD_GEORGE.value.display_name,
                    }
                ]
            },
            "custodian": {
                "identifier": {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "A12345",
                }
            },
            "author": [
                {
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "A12345",
                    }
                }
            ],
            "content": [
                {
                    "attachment": {
                        "contentType": "application/pdf",
                        "language": "en-GB",
                        "title": "test-file.pdf",
                        "creation": "2023-01-01T12:00:00Z",
                    }
                }
            ],
        }
    )


@pytest.fixture
def valid_fhir_doc_with_binary(valid_fhir_doc):
    doc = json.loads(valid_fhir_doc)
    doc["content"][0]["attachment"][
        "data"
    ] = "SGVsbG8gV29ybGQ="  # Base64 encoded "Hello World"
    return json.dumps(doc)


def test_process_fhir_document_reference_with_presigned_url(
    mock_service, valid_fhir_doc
):
    presigned_url = {
        "url": "https://test-bucket.s3.amazonaws.com/test-key",
        "fields": {},
    }
    mock_service.s3_service.create_upload_presigned_url.return_value = presigned_url

    result = mock_service.process_fhir_document_reference(valid_fhir_doc)

    # Assert
    assert isinstance(result, str)
    result_json = json.loads(result)
    assert result_json["resourceType"] == "DocumentReference"
    assert result_json["content"][0]["attachment"]["url"] == presigned_url["url"]

    # Verify
    mock_service.s3_service.create_upload_presigned_url.assert_called_once()
    mock_service.dynamo_service.create_item.assert_called_once()
    mock_service.s3_service.upload_file_obj.assert_not_called()


def test_process_fhir_document_reference_with_binary(
    mock_service, valid_fhir_doc_with_binary
):
    """Test a happy path with binary data in the request."""
    # Execute
    result = mock_service.process_fhir_document_reference(valid_fhir_doc_with_binary)

    # Assert
    assert isinstance(result, str)
    result_json = json.loads(result)
    assert result_json["resourceType"] == "DocumentReference"

    # Verify
    mock_service.s3_service.upload_file_obj.assert_called_once()
    mock_service.dynamo_service.create_item.assert_called_once()
    mock_service.s3_service.create_upload_presigned_url.assert_not_called()


def test_validation_error(mock_service):
    """Test handling of an invalid FHIR document."""
    # Execute & Assert
    with pytest.raises(CreateDocumentRefException) as excinfo:
        mock_service.process_fhir_document_reference("{invalid json}")

    assert excinfo.value.status_code == 400
    assert excinfo.value.error == LambdaError.CreateDocNoParse


@pytest.mark.parametrize(
    "modify_doc, expected_error",
    [
        # Missing NHS number (wrong system)
        (
            lambda doc: {
                **doc,
                "type": {"coding": [{"system": "wrong-system", "code": "9000000009"}]},
            },
            LambdaError.CreateDocInvalidType,
        ),
        # Invalid document type
        (
            lambda doc: {
                **doc,
                "type": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "invalid-code",
                            "display": "Invalid",
                        }
                    ]
                },
            },
            LambdaError.CreateDocInvalidType,
        ),
        # Missing document type
        (lambda doc: {**doc, "type": {"coding": []}}, LambdaError.CreateDocInvalidType),
    ],
)
def test_document_validation_errors(
    mock_service, valid_fhir_doc, modify_doc, expected_error
):
    """Test validation error scenarios."""
    # Setup
    doc = json.loads(valid_fhir_doc)
    modified_doc = FhirDocumentReference(**modify_doc(doc))

    # Execute & Assert
    with pytest.raises(CreateDocumentRefException) as e:
        mock_service._determine_document_type(modified_doc)

    assert e.value.status_code == 400
    assert e.value.error == expected_error


def test_dynamo_error(mock_service, valid_fhir_doc):
    """Test handling of DynamoDB error."""
    # Setup
    mock_service.dynamo_service.create_item.side_effect = ClientError(
        {"Error": {"Code": "InternalServerError", "Message": "Test error"}},
        "CreateItem",
    )

    # Execute & Assert
    with pytest.raises(CreateDocumentRefException) as excinfo:
        mock_service.process_fhir_document_reference(valid_fhir_doc)

    assert excinfo.value.status_code == 500
    assert excinfo.value.error == LambdaError.CreateDocUpload


def test_pds_error(mock_service, valid_fhir_doc, mocker):
    """Test handling of PDS error."""

    mock_service._check_nhs_number_with_pds = mocker.MagicMock()
    mock_service._check_nhs_number_with_pds.side_effect = CreateDocumentRefException(
        400, LambdaError.MockError
    )
    with pytest.raises(CreateDocumentRefException) as excinfo:
        mock_service.process_fhir_document_reference(valid_fhir_doc)
    assert excinfo.value.status_code == 400
    assert excinfo.value.error == LambdaError.MockError


def test_s3_presigned_url_error(mock_service, valid_fhir_doc):
    """Test handling of S3 presigned URL error."""
    # Setup
    mock_service.s3_service.create_upload_presigned_url.side_effect = ClientError(
        {"Error": {"Code": "InternalServerError", "Message": "Test error"}},
        "CreatePresignedUrl",
    )

    # Execute & Assert
    with pytest.raises(CreateDocumentRefException) as excinfo:
        mock_service.process_fhir_document_reference(valid_fhir_doc)

    assert excinfo.value.status_code == 500
    assert excinfo.value.error == LambdaError.CreateDocPresign


def test_s3_upload_error(mock_service, valid_fhir_doc_with_binary):
    """Test handling of S3 upload error."""
    # Setup
    mock_service.s3_service.upload_file_obj.side_effect = ClientError(
        {"Error": {"Code": "InternalServerError", "Message": "Test error"}}, "PutObject"
    )

    # Execute & Assert
    with pytest.raises(CreateDocumentRefException) as excinfo:
        mock_service.process_fhir_document_reference(valid_fhir_doc_with_binary)

    assert excinfo.value.status_code == 500
    assert excinfo.value.error == LambdaError.CreateDocPresign


def test_check_nhs_number_with_pds_raise_error(mock_service, mocker):
    """Test handling of PDS error."""
    mock_service_object = mocker.MagicMock()
    mocker.patch(
        "services.post_fhir_document_reference_service.get_pds_service",
        return_value=mock_service_object,
    )
    mock_service_object.fetch_patient_details.side_effect = PatientNotFoundException(
        "test test"
    )
    with pytest.raises(CreateDocumentRefException) as excinfo:
        mock_service._check_nhs_number_with_pds("9000000009")
    assert excinfo.value.status_code == 400
