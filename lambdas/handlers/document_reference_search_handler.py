import json
import logging
import os
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.dynamo_service import DynamoDBService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event, validate_patient_id)
from utils.exceptions import DynamoDbException, InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import camelize_dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@validate_patient_id
@ensure_environment_variables(names=["DYNAMODB_TABLE_LIST"])
def lambda_handler(event, context):
    logger.info("Starting document reference search process")
    nhs_number = extract_nhs_number_from_event(event)

    try:
        list_of_table_names = json.loads(os.environ["DYNAMODB_TABLE_LIST"])
    except JSONDecodeError as e:
        logger.error(str(e))
        return ApiGatewayResponse(
            500,
            "An error occurred when parsing `DYNAMODB_TABLE_LIST` env variables",
            "GET",
        ).create_api_gateway_response()

    dynamo_service = DynamoDBService()

    try:
        results = []
        for table_name in list_of_table_names:
            logger.info(f"Searching for results in {table_name}")
            response = dynamo_service.query_with_requested_fields(
                table_name=table_name,
                index_name="NhsNumberIndex",
                search_key="NhsNumber",
                search_condition=nhs_number,
                requested_fields=[
                    DocumentReferenceMetadataFields.CREATED,
                    DocumentReferenceMetadataFields.FILE_NAME,
                    DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT,
                ],
                filtered_fields={
                    DocumentReferenceMetadataFields.DELETED.field_name: ""
                },
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
        logger.error(f"Unable to connect to DynamoDB: {str(e)}")
        return ApiGatewayResponse(
            500, "An error occurred when searching for available documents", "GET"
        ).create_api_gateway_response()
    except DynamoDbException as e:
        logger.error(f"An error occurred when querying DynamoDB: {str(e)}")
        return ApiGatewayResponse(
            500,
            "An error occurred when searching for available documents",
            "GET",
        ).create_api_gateway_response()

    response = [camelize_dict(result) for result in results]

    if not results or not response:
        return ApiGatewayResponse(
            204, json.dumps([]), "GET"
        ).create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(response), "GET"
    ).create_api_gateway_response()
