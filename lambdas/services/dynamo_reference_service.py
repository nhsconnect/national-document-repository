import logging
import uuid

import boto3
from botocore.exceptions import ClientError
from models.nhs_document_reference import NHSDocumentReference

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoReferenceService:
    s3_object_key = str(uuid.uuid4())

    def __init__(self, dynamo_table_name):
        self.dynamo_table_name = dynamo_table_name

    # Previously Create Document Reference Object
    # Creates the necessary data to upload to Dynamo DocumentReferenceMetadata table
    def create_document_dynamo_reference_object(
        self, s3_bucket_name, s3_object_key: str, document_request_body
    ) -> NHSDocumentReference:
        s3_file_location = f"s3://{s3_bucket_name}/{s3_object_key}"
        logger.info(f"Input document reference location: {s3_file_location}")

        new_document = NHSDocumentReference(
            file_location=s3_file_location,
            reference_id=s3_object_key,
            data=document_request_body,
        )

        logger.info(f"Input document reference filename: {new_document.file_name}")
        return new_document

    def save_document_reference_in_dynamo_db(self, new_document: NHSDocumentReference):
        try:
            dynamodb = boto3.resource("dynamodb")
            logger.info(
                f"Saving DocumentReference to DynamoDB: {self.dynamo_table_name}"
            )
            table = dynamodb.Table(self.dynamo_table_name)
            table.put_item(Item=new_document.to_dict())
        except ClientError as e:
            logger.error("Unable to connect to DB")
            logger.error(e)
