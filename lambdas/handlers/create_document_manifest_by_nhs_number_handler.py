from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_query_service import DynamoQueryService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.nhs_number_validator import validate_id

TABLE_NAME = "test table"
INDEX_NAME = "test index name"


def lambda_handler(event, context):
    # Get and validate the NHS number
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

    # Find the locations of the docs for this patient
    documents = find_document_locations(nhs_number)
    if len(documents) == 0:
        return ApiGatewayResponse(204, "No documents found for given NHS number", "GET"
                                  ).create_api_gateway_response()

    return ApiGatewayResponse(200, "OK", "GET"
                              ).create_api_gateway_response()

    # Download all of these documents and zip them
    # Be wary of OutOfMemory errors

    # Upload the new Zip file to S3

    # Return the zip file pre-signed URL


def find_document_locations(nhs_number):
    dynamo_query_service = DynamoQueryService(TABLE_NAME, INDEX_NAME)
    location_query_response = dynamo_query_service("NhsNumber", nhs_number,
                                                   [DynamoDocumentMetadataTableFields.LOCATION])

    document_locations = []
    for item in location_query_response["Items"]:
        document_locations.append(item["Location"])

    return document_locations


def generate_zip_of_documents(locations: list):
    pass


def upload_to_s3(zip_file):
    pass
