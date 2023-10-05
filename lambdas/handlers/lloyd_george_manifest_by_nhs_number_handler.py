import logging
import os

from botocore.exceptions import ClientError
from lambdas.services import LloydGeorgeManifestDynamoService
from services.document_manifest_service import DocumentManifestService
from utils.exceptions import (DynamoDbException, InvalidResourceIdException,
                              ManifestDownloadException)
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting document manifest process")

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)


        zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        zip_trace_table_name = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]

        dynamo_service = LloydGeorgeManifestDynamoService

        logger.info("Retrieving lloyd george documents")
        documents = dynamo_service.query_lloyd_george_documents(nhs_number)

        if not documents:
            return ApiGatewayResponse(
                204, "No documents found for given NHS number", "GET"
            ).create_api_gateway_response()

        logger.info("Starting document manifest process")
        document_manifest_service = DocumentManifestService(
            nhs_number=nhs_number,
            documents=documents,
            zip_output_bucket=zip_output_bucket,
            zip_trace_table=zip_trace_table_name,
        )

        response = document_manifest_service.create_document_manifest_presigned_url()

        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except InvalidResourceIdException:
        return ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
    except KeyError as e:
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "GET"
        ).create_api_gateway_response()
    except ManifestDownloadException as e:
        return ApiGatewayResponse(
            500,
            f"{str(e)}",
            "GET",
        ).create_api_gateway_response()
    except DynamoDbException as e:
        return ApiGatewayResponse(
            500,
            f"An error occurred when searching for available documents: {str(e)}",
            "GET",
        ).create_api_gateway_response()
    except ClientError as e:
        logger.error(str(e))
        response = ApiGatewayResponse(
            500, "An error occurred when creating document manifest", "POST"
        ).create_api_gateway_response()
        return response
