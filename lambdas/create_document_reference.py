import os
import boto3
from botocore.exceptions import ClientError


def create_document_reference_handler(event, context):
    print("API Gateway event received - processing starts")
    s3_bucket_name = os.environ['DOCUMENT_STORE_BUCKET_NAME']
    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3', region_name='eu-west-2')

    try:
        response = s3_client.generate_presigned_post(s3_bucket_name,
                                                     Fields=None,
                                                     Conditions=None,
                                                     ExpiresIn=1800)
    except ClientError as e:
        print(e)
        return None

    # The response contains the presigned URL and required fields
    return response
