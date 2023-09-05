import json
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
    document_store_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
    list_of_table_names = [document_store_table_name, lloyd_george_table_name]

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

    dynamo_service_for_tables = {
        table_name: DynamoQueryService(table_name, "NhsNumberIndex")
        for table_name in list_of_table_names
    }

    try:
        responses = []
        for dynamo_service in dynamo_service_for_tables.values():
            response = dynamo_service(
                "NhsNumber",
                nhs_number,
                [
                    DynamoDocumentMetadataTableFields.CREATED,
                    DynamoDocumentMetadataTableFields.FILE_NAME,
                ],
            )
            if response is None or ("Items" not in response):
                logger.error(f"Unrecognised response from DynamoDB: {response!r}")
                return ApiGatewayResponse(
                    500,
                    "Unrecognised response when searching for available documents",
                    "GET",
                ).create_api_gateway_response()

            responses += response["Items"]

    except InvalidResourceIdException:
        return ApiGatewayResponse(
            500, "No data was requested to be returned in query", "GET"
        ).create_api_gateway_response()
    except ClientError:
        return ApiGatewayResponse(
            500, "An error occurred searching for available documents", "GET"
        ).create_api_gateway_response()

    if len(responses) == 0:
        return ApiGatewayResponse(204, "", "GET").create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(responses), "GET"
    ).create_api_gateway_response()
