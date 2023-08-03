import os
import uuid
import boto3
from botocore.exceptions import ClientError
import logging
from lambdas.nhs_document_reference import NHSDocumentReference

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("API Gateway event received - processing starts")
    s3_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
    logger.info("S3 bucket in use: ", s3_bucket_name)
    s3_object_key = str(uuid.uuid4())
    try:
        document_object = create_document_reference_object(
            s3_bucket_name, s3_object_key, event["body"]
        )
        create_document_reference_in_dynamo_db(document_object)
        response = create_document_presigned_url_handler(s3_bucket_name, s3_object_key)
    except Exception as e:
        logger.error(e)
        # create error response generator
        return e
    return response


def create_document_presigned_url_handler(s3_bucket_name, s3_object_key):
    # Generate a presigned S3 POST URL
    s3_client = boto3.client("s3", region_name="eu-west-2")

    try:
        response = s3_client.generate_presigned_post(
            s3_bucket_name, s3_object_key, Fields=None, Conditions=None, ExpiresIn=1800
        )
    except ClientError as e:
        logger.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response


def create_document_reference_object(
    s3_bucket_name, s3_object_key, document_request_body
):
    s3_file_location = "s3://" + s3_bucket_name + "/" + s3_object_key
    logger.info("Input document reference location: ", s3_file_location)
    new_document = NHSDocumentReference(
        file_location=s3_file_location,
        reference_id=s3_object_key,
        data=document_request_body,
    )
    logger.info("Input document reference filename: ", new_document.file_name)
    return new_document


def create_document_reference_in_dynamo_db(new_document):
    dynamodb = boto3.resource("dynamodb")
    dynamodb_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    logger.info("Saving DocumentReference to DynamoDB: ", dynamodb_name)
    table = dynamodb.Table(dynamodb_name)
    table.put_item(Item=new_document.to_dict())
