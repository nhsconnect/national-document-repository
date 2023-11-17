import os

from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from pydantic import ValidationError
from services.document_manifest_service import DocumentManifestService
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_document_type import (extract_document_type,
                                                     validate_document_type)
from utils.decorators.validate_patient_id import validate_patient_id
from utils.exceptions import DynamoDbException, ManifestDownloadException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@validate_document_type
@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "ZIPPED_STORE_BUCKET_NAME",
        "ZIPPED_STORE_DYNAMODB_NAME",
    ]
)
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.DOWNLOAD_RECORD.value

    logger.info("Starting document manifest process")

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        doc_type = extract_document_type(event["queryStringParameters"]["docType"])
        request_context.patient_nhs_no = nhs_number

        zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        zip_trace_table_name = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]
        # zip_trace_ttl = os.environ["DOCUMENT_ZIP_TRACE_TTL_IN_DAYS"]

        dynamo_service = DocumentService()
        documents = dynamo_service.fetch_available_document_references_by_type(
            nhs_number, doc_type
        )

        if not documents:
            return ApiGatewayResponse(
                204, "No documents found for given NHS number and document type", "GET"
            ).create_api_gateway_response()

        logger.info("Starting document manifest process")
        document_manifest_service = DocumentManifestService(
            nhs_number=nhs_number,
            documents=documents,
            zip_output_bucket=zip_output_bucket,
            zip_trace_table=zip_trace_table_name,
        )

        response = document_manifest_service.create_document_manifest_presigned_url()
        logger.audit_splunk_info(
            "User has downloaded Lloyd George records",
            {"Result": "Successful download"},
        )

        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except ValidationError as e:
        logger.info(e, {"Result": f"Unsuccessful download due to {str(e)}"})
        return ApiGatewayResponse(
            500,
            "Failed to parse document reference from from DynamoDb response",
            "GET",
        ).create_api_gateway_response()
    except ManifestDownloadException as e:
        logger.error(str(e), {"Result": f"Unsuccessful download due to {str(e)}"})
        return ApiGatewayResponse(
            500,
            f"{str(e)}",
            "GET",
        ).create_api_gateway_response()
    except DynamoDbException as e:
        logger.error(str(e), {"Result": f"Unsuccessful download due to {str(e)}"})
        return ApiGatewayResponse(
            500,
            f"An error occurred when searching for available documents: {str(e)}",
            "GET",
        ).create_api_gateway_response()
    except ClientError as e:
        logger.error(str(e), {"Result": f"Unsuccessful download due to {str(e)}"})
        response = ApiGatewayResponse(
            500, "An error occurred when creating document manifest", "GET"
        ).create_api_gateway_response()
        return response
