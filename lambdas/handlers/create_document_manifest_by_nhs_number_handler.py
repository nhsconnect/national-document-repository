from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_query_service import DynamoQueryService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.nhs_number_validator import validate_id

TABLE_NAME = "test table"
INDEX_NAME = "test index name"


def lambda_handler(event, context):
    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)
    except InvalidResourceIdException:
        return ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
    except KeyError:
        return ApiGatewayResponse(
            400, "Please supply an NHS number", "GET"
        ).create_api_gateway_response()
    documents = find_document_locations(nhs_number)
    if len(documents) == 0:
        return ApiGatewayResponse(204, "No documents found for given NHS number", "GET").create_api_gateway_response()

    return ApiGatewayResponse(200, "OK", "GET").create_api_gateway_response()


def find_document_locations(nhs_number):
    dynamo_query_service = DynamoQueryService(TABLE_NAME, INDEX_NAME)
    location_query_response = dynamo_query_service("NhsNumber", nhs_number,
                                                   [DynamoDocumentMetadataTableFields.LOCATION])

    document_locations = []
    for item in location_query_response["Items"]:
        document_locations.append(item["Location"])

    return document_locations
