import csv
import os
import boto3
from botocore.exceptions import ClientError

from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service

s3_resource = boto3.resource('s3')

def lambda_handler(event, context):
    db_service = DynamoDBService()
    s3_service = S3Service()
    staging_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
    report_data = get_dynamo_data(db_service)
    current_report = get_current_report(s3_service, 'reports')
    write_items_to_csv(report_data)
    s3_resource.Bucket(staging_bucket_name).upload_file(TEMP_FILENAME, OUTPUT_KEY)

def get_dynamo_data(db_service):
    bulk_upload_table_name = os.getenv("BULK_UPLOAD_DYNAMODB")
    db_response = db_service.scan_table(bulk_upload_table_name)
    last_key = db_response['LastEvaluatedKey']
    items = db_response['Items']
    while last_key:
        db_response = db_service.scan_table(bulk_upload_table_name, exclusive_start_key=last_key)
        last_key = db_response['LastEvaluatedKey']
        items.append(db_response['Items'])
    return items

def write_items_to_csv(items: list, csv_file_path: str):
   with open(csv_file_path, 'a') as output_file:
        field_names = items[0].keys()
        dict_writer_object = csv.DictWriter(output_file, fieldnames=field_names)
        for item in items:
            dict_writer_object.writerow(item)
        output_file.close()

def get_current_report(s3_service, file_location: str, s3_bucket: str):
    try:
        return s3_service.download_file(s3_bucket, 'bulk_upload_report.csv', file_location)
    except ClientError as e:
        pass