from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_query_service import DynamoQueryService

TABLE_NAME = "test table"
INDEX_NAME = "test index name"


def lambda_handler(event, context):
    pass


def find_document_locations(nhs_number):
    dynamo_query_service = DynamoQueryService(TABLE_NAME, INDEX_NAME)
    location_query_response = dynamo_query_service("NhsNumber", nhs_number,
                                                   [DynamoDocumentMetadataTableFields.LOCATION])

    document_locations = []
    for item in location_query_response["Items"]:
        document_locations.append(item["Location"])

    return document_locations
