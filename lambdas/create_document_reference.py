import os
import uuid
import boto3
from botocore.exceptions import ClientError

from lambdas.nhs_document_reference import NHSDocumentReference


def lambda_handler(event, context):
    print("API Gateway event received - processing starts")
    s3_bucket_name = os.environ['DOCUMENT_STORE_BUCKET_NAME']
    s3_object_key = str(uuid.uuid4())
    try:
        create_document_reference_object(s3_bucket_name, s3_object_key, event["body"])
        create_document_presigned_url_handler(s3_bucket_name, s3_object_key)
    except Exception as e:
        print(e)
        #create error response generator
        return e

def create_document_presigned_url_handler(s3_bucket_name, s3_object_key):
    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3', region_name='eu-west-2')

    try:
        response = s3_client.generate_presigned_post(s3_bucket_name,
                                                     s3_object_key,
                                                     Fields=None,
                                                     Conditions=None,
                                                     ExpiresIn=1800)
    except ClientError as e:
        print(e)
        return None

    # The response contains the presigned URL and required fields
    return response

def create_document_reference_object(s3_bucket_name, s3_object_key, document_request_body):
    s3_file_location = "s3://" + s3_bucket_name + "/" + s3_object_key
    new_document = NHSDocumentReference(file_location=s3_file_location,reference_id=s3_object_key, **document_request_body)
    print("Input document reference filename: ", new_document.file_name)
    create_document_reference_in_dynamo_db(new_document)

def create_document_reference_in_dynamo_db(new_document):
    dynamodb = boto3.resource('dynamodb')
    dynamodb_name = os.environ['DOCUMENT_STORE_DYNAMODB_NAME']
    table = dynamodb.Table(dynamodb_name)
    table.put_item(
        Item=new_document.to_dict()
    )

