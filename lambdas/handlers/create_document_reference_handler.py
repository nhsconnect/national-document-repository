import json
import logging
import os
import sys
import uuid

from botocore.exceptions import ClientError
from enums.supported_document_types import SupportedDocumentTypes
from models.nhs_document_reference import NHSDocumentReference
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from utils.lambda_response import ApiGatewayResponse

sys.path.append(os.path.join(os.path.dirname(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting document reference creation process")
    responses = {}
    body = json.loads(event["body"])
    if not body:
        response = ApiGatewayResponse(
            400, "Provided an empty request body", "POST"
        ).create_api_gateway_response()
        return response
    nhs_number = body["subject"]["identifier"]["value"]
    for document in body["content"][0]["attachment"]:
        document_type = SupportedDocumentTypes.get_from_field_name(document["docType"])
        if document_type is None:
            response = ApiGatewayResponse(
                400, "An error occurred processing the required document type", "POST"
            ).create_api_gateway_response()
            return response

        try:
            if document_type == SupportedDocumentTypes.LG:
                s3_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
                dynamo_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
            elif document_type == SupportedDocumentTypes.ARF:
                s3_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
                dynamo_table = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
            else:
                response = ApiGatewayResponse(
                    400, "Provided invalid document type", "POST"
                ).create_api_gateway_response()
                return response
        except KeyError as e:
            return ApiGatewayResponse(
                500,
                f"An error occurred due to missing environment variables: {str(e)}",
                "POST",
            ).create_api_gateway_response()

        logger.info("Provided document is supported")

        logger.info(f"S3 bucket in use: {s3_bucket_name}")
        logger.info(f"Dynamo table in use: {dynamo_table}")

        s3_object_key = str(uuid.uuid4())
        dynamo_service = DynamoDBService()
        s3_service = S3Service()
        new_document = NHSDocumentReference(
            nhs_number=nhs_number,
            s3_bucket_name=s3_bucket_name,
            reference_id=s3_object_key,
            content_type=document["contentType"],
            file_name=document["fileName"]
        )

        try:
            dynamo_service.post_item_service(dynamo_table, new_document.to_dict())

            s3_response = s3_service.create_document_presigned_url_handler(
                new_document.s3_bucket_name, new_document.nhs_number + "/" + new_document.id
            )
            responses[new_document.file_name] = s3_response

        except ClientError as e:
            logger.error(str(e))
            response = ApiGatewayResponse(
                500, "An error occurred when creating document reference", "POST"
            ).create_api_gateway_response()
            return response

    return ApiGatewayResponse(
        200, json.dumps(responses), "POST"
    ).create_api_gateway_response()
