import json
import logging
import os

from botocore.exceptions import ClientError
from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_services import DynamoDBService
from utils.exceptions import DynamoDbException, InvalidResourceIdException
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
        table_name: DynamoDBService(table_name)
        for table_name in list_of_table_names
    }

    try:
        results = []
        for dynamo_service in dynamo_service_for_tables.values():
            response = dynamo_service.query_service(
                "NhsNumberIndex",
                "NhsNumber",
                nhs_number,
                [
                    DynamoDocumentMetadataTableFields.CREATED,
                    DynamoDocumentMetadataTableFields.FILE_NAME,
                    DynamoDocumentMetadataTableFields.VIRUS_SCAN_RESULT,
                ],
            )
            if response is None or ("Items" not in response):
                logger.error(f"Unrecognised response from DynamoDB: {response!r}")
                return ApiGatewayResponse(
                    500,
                    "Unrecognised response when searching for available documents",
                    "GET",
                ).create_api_gateway_response()

            results += response["Items"]

    except InvalidResourceIdException:
        return ApiGatewayResponse(
            500, "No data was requested to be returned in query", "GET"
        ).create_api_gateway_response()
    except ClientError as e:
        logger.error(f"Unable to connect to DynamoDB: str({e})")
        return ApiGatewayResponse(
            500, "An error occurred when searching for available documents", "GET"
        ).create_api_gateway_response()
    except DynamoDbException as e:
        return ApiGatewayResponse(
            500,
            f"An error occurred when searching for available documents: {str(e)}",
            "GET",
        ).create_api_gateway_response()

    response = [decapitalise_keys(result) for result in results]

    if not results or not response:
        return ApiGatewayResponse(
            204, json.dumps([]), "GET"
        ).create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(response), "GET"
    ).create_api_gateway_response()


def decapitalise_keys(values):
    data = {}
    for key, value in values.items():
        data[key[0].lower() + key[1:]] = value
    return data
