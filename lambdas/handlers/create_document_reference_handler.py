import json
import logging
import os
import sys
import uuid

from services.dynamo_reference_service import DynamoReferenceService
from services.s3_upload_service import S3UploadService
from utils.lambda_response import ApiGatewayResponse

sys.path.append(os.path.join(os.path.dirname(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("API Gateway event received - processing starts")
    s3_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
    dynamo_table = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    logger.info(f"S3 bucket in use: {s3_bucket_name}")
    logger.info(f"Dynamo table in use: {dynamo_table}")
    body = json.loads(event["body"])
    dynamo_reference_service = DynamoReferenceService(dynamo_table)
    s3_upload_service = S3UploadService(s3_bucket_name)

    try:
        s3_object_key = str(uuid.uuid4())
        document_object = dynamo_reference_service.create_document_dynamo_reference_object(s3_bucket_name,
                                                                                           s3_object_key, body)
        dynamo_reference_service.save_document_reference_in_dynamo_db(document_object)

        s3_response = s3_upload_service.create_document_presigned_url_handler(s3_object_key)
    except Exception as e:
        logger.error(e)
        response = ApiGatewayResponse(400, e, "POST").create_api_gateway_response()
        return response
    return ApiGatewayResponse(
        200, json.dumps(s3_response), "POST"
    ).create_api_gateway_response()
