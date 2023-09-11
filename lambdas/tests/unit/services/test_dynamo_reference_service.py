from models.nhs_document_reference import NHSDocumentReference
from services.dynamo_reference_service import DynamoReferenceService

MOCK_BUCKET = "test_s3_bucket"
MOCK_DYNAMODB = "test_dynamoDB_table"
TEST_OBJECT_KEY = "1234-4567-8912-HSDF-TEST"
TEST_DOCUMENT_LOCATION = f"s3://{MOCK_BUCKET}/{TEST_OBJECT_KEY}"
MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": 111111000}},
    "content": [{"attachment": {"contentType": "application/pdf"}}],
    "description": "test_filename.pdf",
}


def test_create_document_dynamo_reference_object():
    service = DynamoReferenceService(MOCK_DYNAMODB)
    test_document_object = service.create_document_dynamo_reference_object(
        MOCK_BUCKET, TEST_OBJECT_KEY, MOCK_EVENT_BODY
    )
    assert test_document_object.file_name == "test_filename.pdf"
    assert test_document_object.content_type == "application/pdf"
    assert test_document_object.nhs_number == 111111000
    assert test_document_object.file_location == TEST_DOCUMENT_LOCATION


def test_save_document_reference_in_dynamo_db(mocker):
    service = DynamoReferenceService(MOCK_DYNAMODB)
    mock_dynamo = mocker.patch("boto3.resource")
    mock_table = mocker.MagicMock()

    test_document_object = NHSDocumentReference(
        TEST_OBJECT_KEY, TEST_DOCUMENT_LOCATION, MOCK_EVENT_BODY
    )

    mock_dynamo.return_value.Table.return_value = mock_table

    service.save_document_reference_in_dynamo_db(test_document_object)
    mock_table.put_item.assert_called_once()
