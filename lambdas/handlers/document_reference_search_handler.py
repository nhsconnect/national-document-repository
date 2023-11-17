import json
import os
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.document_reference import (DocumentReference,
                                       DocumentReferenceSearchResult)
from pydantic import ValidationError
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event, validate_patient_id)
from utils.exceptions import DynamoDbException, InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@ensure_environment_variables(names=["DYNAMODB_TABLE_LIST"])
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.VIEW_PATIENT.value
    nhs_number = extract_nhs_number_from_event(event)
    request_context.patient_nhs_no = nhs_number

    logger.info("Starting document reference search process")

    try:
        list_of_table_names = json.loads(os.environ["DYNAMODB_TABLE_LIST"])
    except JSONDecodeError as e:
        logger.error(str(e), {"Result": f"Unsuccessful viewing docs due to {str(e)}"})
        return ApiGatewayResponse(
            500,
            "An error occurred when parsing `DYNAMODB_TABLE_LIST` env variables",
            "GET",
        ).create_api_gateway_response()

    document_service = DocumentService()

    try:
        results: list[DocumentReference] = []
        for table_name in list_of_table_names:
            logger.info(f"Searching for results in {table_name}")
            documents = document_service.fetch_documents_from_table_with_filter(
                nhs_number,
                table_name,
                attr_filter={DocumentReferenceMetadataFields.DELETED.value: ""},
            )

            results += documents

    except ValidationError as e:
        logger.info(e, {"Result": f"Unsuccessful viewing docs due to {str(e)}"})
        return ApiGatewayResponse(
            500,
            "Failed to parse document reference from from DynamoDb response",
            "GET",
        ).create_api_gateway_response()
    except InvalidResourceIdException:
        return ApiGatewayResponse(
            500, "No data was requested to be returned in query", "GET"
        ).create_api_gateway_response()
    except ClientError as e:
        logger.error(
            f"Unable to connect to DynamoDB: {str(e)}",
            {"Result": f"Unsuccessful viewing docs due to {str(e)}"},
        )
        return ApiGatewayResponse(
            500, "An error occurred when searching for available documents", "GET"
        ).create_api_gateway_response()
    except DynamoDbException as e:
        logger.error(
            f"An error occurred when querying DynamoDB: {str(e)}",
            {"Result": f"Unsuccessful viewing docs due to {str(e)}"},
        )
        return ApiGatewayResponse(
            500,
            "An error occurred when searching for available documents",
            "GET",
        ).create_api_gateway_response()

    try:
        response = [
            dict(DocumentReferenceSearchResult.model_validate(dict(result)))
            for result in results
        ]
    except ValidationError as e:
        logger.info(e, {"Result": f"Unsuccessful viewing docs due to {str(e)}"})
        return ApiGatewayResponse(
            500,
            "Failed to parse document reference search results",
            "GET",
        ).create_api_gateway_response()
    logger.info("User is able to view docs", {"Result": "Successful viewing docs"})

    if not response:
        return ApiGatewayResponse(
            204, json.dumps([]), "GET"
        ).create_api_gateway_response()

    return ApiGatewayResponse(
        200, json.dumps(response), "GET"
    ).create_api_gateway_response()
