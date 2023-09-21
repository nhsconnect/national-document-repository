import json
import logging
import os
import sys
import uuid

from botocore.exceptions import ClientError
from models.nhs_document_reference import NHSDocumentReference
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from enums.supported_document_types import SupportedDocumentTypes
from utils.lambda_response import ApiGatewayResponse

sys.path.append(os.path.join(os.path.dirname(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting document reference creation process")

    document_type_string = (event["queryStringParameters"]["documentType"]).upper()
    document_type = SupportedDocumentTypes.get_from_field_name(document_type_string);
    if document_type is None:
        logger.error(e)
        response = ApiGatewayResponse(400, "An error occured processing the required document type", "POST").create_api_gateway_response()
        return response
    
    logger.info("Provided document is supported")
    
    try:
        
        if (document_type == SupportedDocumentTypes.LG):
            s3_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
            dynamo_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        
        if (document_type == SupportedDocumentTypes.ARF):
            s3_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
            dynamo_table = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
         
        logger.info(f"S3 bucket in use: {s3_bucket_name}")
        logger.info(f"Dynamo table in use: {dynamo_table}")

        body = json.loads(event["body"])
        s3_object_key = str(uuid.uuid4())
        dynamo_service = DynamoDBService()
        s3_service = S3Service()

        new_document = NHSDocumentReference(
            file_location=f"s3://{s3_bucket_name}/{s3_object_key}",
            reference_id=s3_object_key,
            data=body,
        )

        dynamo_service.post_item_service(dynamo_table, new_document.to_dict())

        s3_response = s3_service.create_document_presigned_url_handler(
            s3_bucket_name, s3_object_key
        )

        return ApiGatewayResponse(
            200, json.dumps(s3_response), "POST"
        ).create_api_gateway_response()
    
    except KeyError as e:
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "POST"
        ).create_api_gateway_response()
    except ClientError as e:
        logger.error(str(e))
        response = ApiGatewayResponse(
            500, "An error occurred when creating document reference", "POST"
        ).create_api_gateway_response()
        return response

