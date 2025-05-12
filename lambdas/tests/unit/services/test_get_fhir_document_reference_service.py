import base64
import copy
import json

import pytest
from enums.lambda_error import LambdaError
from enums.snomed_codes import SnomedCodes
from services.get_fhir_document_reference_service import GetFhirDocumentReferenceService
from tests.unit.conftest import MOCK_LG_TABLE_NAME, TEST_CURRENT_GP_ODS, TEST_UUID
from tests.unit.helpers.data.test_documents import create_test_doc_store_refs
from utils.lambda_exceptions import GetFhirDocumentReferenceException

MOCK_USER_INFO = {
    "nhsid_useruid": TEST_UUID,
    "name": "TestUserOne Caius Mr",
    "nhsid_nrbac_roles": [
        {
            "person_orgid": "500000000000",
            "person_roleid": TEST_UUID,
            "org_code": "B9A5A",
            "role_name": '"Support":"Systems Support":"Systems Support Access Role"',
            "role_code": "S8001:G8005:R8000",
        },
        {
            "person_orgid": "500000000000",
            "person_roleid": "500000000000",
            "org_code": "B9A5A",
            "role_name": '"Primary Care Support England":"Systems Support Access Role"',
            "role_code": "S8001:G8005:R8015",
        },
        {
            "person_orgid": "500000000000",
            "person_roleid": "500000000000",
            "org_code": TEST_CURRENT_GP_ODS,
            "role_name": '"Primary Care Support England":"Systems Support Access Role"',
            "role_code": "S8001:G8005:R8008",
        },
    ],
    "given_name": "Caius",
    "family_name": "TestUserOne",
    "uid": "500000000000",
    "nhsid_user_orgs": [
        {"org_name": "NHSID DEV", "org_code": "A9A5A"},
        {"org_name": "Primary Care Support England", "org_code": "B9A5A"},
    ],
    "sub": "500000000000",
}

MOCK_FHIR_DOCUMENT = {
    "resourceType": "DocumentReference",
    "status": "current",
    "type": {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "16521000000101",
                "display": "Lloyd George record folder",
            }
        ]
    },
    "category": [
        {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "734163000",
                    "display": "Care plan",
                }
            ]
        }
    ],
    "subject": {
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": "9000000009",
        }
    },
    "author": [
        {
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "Y12345",
            }
        }
    ],
    "custodian": {
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "Y12345",
        }
    },
    "content": [
        {
            "attachment": {
                "contentType": "application/pdf",
                "language": "en-GB",
                "url": "https://fake-url.com",
                "title": "document.csv",
                "creation": "2024-01-01T12:00:00.000Z",
            },
            "format": {
                "system": "https://fhir.nhs.uk/England/CodeSystem/England-NRLFormatCode",
                "code": "urn:nhs-ic:unstructured",
                "display": "Unstructured Document",
            },
            "extension": [
                {
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/England/CodeSystem/England-NRLContentStability",
                                "code": "static",
                                "display": "Static",
                            }
                        ]
                    },
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-ContentStability",
                }
            ],
        }
    ],
    "context": {
        "practiceSetting": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "1060971000000108",
                    "display": "General practice service",
                }
            ]
        }
    },
}


@pytest.fixture
def patched_service(mocker, set_env, context):
    mocker.patch("services.base.s3_service.IAMService")
    mocker.patch("services.get_fhir_document_reference_service.S3Service")
    mocker.patch("services.get_fhir_document_reference_service.SSMService")
    mocker.patch("services.get_fhir_document_reference_service.DocumentService")
    service = GetFhirDocumentReferenceService()

    yield service


def test_get_document_reference_service(patched_service):
    (patched_service.document_service.fetch_documents_from_table.return_value) = (
        create_test_doc_store_refs()
    )

    actual = patched_service.get_document_references(
        "3d8683b9-1665-40d2-8499-6e8302d507ff", MOCK_LG_TABLE_NAME
    )
    assert actual == create_test_doc_store_refs()[0]


def test_handle_get_document_reference_request(patched_service, mocker, set_env):
    expected = create_test_doc_store_refs()[0]
    mock_document_ref = create_test_doc_store_refs()[0]
    mocker.patch.object(
        patched_service, "get_document_references", return_value=mock_document_ref
    )

    actual = patched_service.handle_get_document_reference_request(
        SnomedCodes.LLOYD_GEORGE.value.code, "test-id"
    )

    assert expected == actual


def test_get_document_reference_request_no_table_associated_to_snomed_code_throws_exception(
    patched_service,
):
    with pytest.raises(GetFhirDocumentReferenceException):
        patched_service.handle_get_document_reference_request("12345678", "test-id")


def test_get_presigned_url(patched_service, mocker):
    expected_url = "https://d12345.cloudfront.net/path/to/resource"

    patched_service.s3_service.create_download_presigned_url.return_value = (
        "https://example.com/path/to/resource"
    )
    mocker.patch(
        "services.get_fhir_document_reference_service.format_cloudfront_url"
    ).return_value = "https://d12345.cloudfront.net/path/to/resource"

    result = patched_service.get_presigned_url(
        "test-s3-bucket", "9000000009/test-key-123"
    )
    assert result == expected_url

    patched_service.s3_service.create_download_presigned_url.assert_called_once_with(
        s3_bucket_name="test-s3-bucket",
        file_key="9000000009/test-key-123",
    )


def test_get_document_references_empty_result(patched_service):
    # Test when no documents are found
    patched_service.document_service.fetch_documents_from_table.return_value = []

    with pytest.raises(GetFhirDocumentReferenceException) as exc_info:
        patched_service.get_document_references("test-id", MOCK_LG_TABLE_NAME)

    assert exc_info.value.error == LambdaError.DocumentReferenceNotFound
    assert exc_info.value.status_code == 404


def test_get_presigned_url_failure(patched_service, mocker):
    # Test when S3 service raises an exception
    patched_service.s3_service.create_download_presigned_url.side_effect = Exception(
        "S3 error"
    )

    with pytest.raises(Exception) as exc_info:
        patched_service.get_presigned_url("file-key", "bucket-name")

    assert str(exc_info.value) == "S3 error"
    patched_service.s3_service.create_download_presigned_url.assert_called_once()


def test_create_document_reference_fhir_response_with_presign_url_document_data(
    patched_service, mocker
):
    # Test creating FHIR response with different document data
    test_doc = create_test_doc_store_refs()[0]

    # Modify the document reference to test different values
    modified_doc = copy.deepcopy(test_doc)
    modified_doc.file_name = "different_file.pdf"
    modified_doc.created = "2023-05-15T10:30:00.000Z"
    patched_service.s3_service.get_file_size.return_value = 8000000
    patched_service.get_presigned_url = mocker.MagicMock(
        return_value="https://new-test-url.com"
    )
    result = patched_service.create_document_reference_fhir_response(modified_doc)

    result_json = json.loads(result)
    assert result_json["content"][0]["attachment"]["url"] == "https://new-test-url.com"
    assert result_json["content"][0]["attachment"]["title"] == "different_file.pdf"
    assert (
        result_json["content"][0]["attachment"]["creation"]
        == "2023-05-15T10:30:00.000Z"
    )


def test_create_document_reference_fhir_response_with_binary_document_data(
    patched_service,
):
    # Test creating FHIR response with different document data
    test_doc = create_test_doc_store_refs()[0]
    # Modify the document reference to test different values
    modified_doc = copy.deepcopy(test_doc)
    modified_doc.file_name = "different_file.pdf"
    modified_doc.created = "2023-05-15T10:30:00.000Z"
    patched_service.s3_service.get_file_size.return_value = 7999999
    mock_binary_file = b"binary data"
    patched_service.s3_service.get_binary_file.return_value = mock_binary_file

    result = patched_service.create_document_reference_fhir_response(modified_doc)
    result_json = json.loads(result)
    assert result_json["content"][0]["attachment"]["data"] == base64.b64encode(
        mock_binary_file
    ).decode("utf-8")
    assert result_json["content"][0]["attachment"]["title"] == "different_file.pdf"
    assert (
        result_json["content"][0]["attachment"]["creation"]
        == "2023-05-15T10:30:00.000Z"
    )
