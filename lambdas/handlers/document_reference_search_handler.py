import logging
import os

from botocore.exceptions import ClientError

from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_query_service import DynamoQueryService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.nhs_number_validator import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)
    except InvalidResourceIdException:
        return ApiGatewayResponse(400, "Invalid NHS number", "GET")
    except KeyError:
        return ApiGatewayResponse(400, "Please supply an NHS number", "GET")

    dynamo_service = DynamoQueryService(table_name, 'NhsNumberIndex')

    try:
        response = dynamo_service('NhsNumber', nhs_number, [DynamoDocumentMetadataTableFields.CREATED, DynamoDocumentMetadataTableFields.FILE_NAME])
    except InvalidResourceIdException:
        return ApiGatewayResponse(400, "No data was requested to be returned in query", "GET")
    except ClientError:
        return ApiGatewayResponse(500, "An error occurred searching for available documents", "GET")

    if response is not None and 'Items' in response:
        results = response['Items']
    else:
        logger.error(f"Unrecognised response from DynamoDB: {response!r}")
        return ApiGatewayResponse(500, "Unrecognised response when searching for available documents", "GET")

    return ApiGatewayResponse(200, results, "GET")
