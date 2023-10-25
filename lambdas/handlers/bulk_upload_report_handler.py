import csv
import os
import boto3
from services.dynamo_service import DynamoDBService

s3_resource = boto3.resource('s3')

def lambda_handler(event, context):
    db_service = DynamoDBService()
    staging_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
    report_data = get_dynamo_data(db_service)
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
        dictwriter_object = csv.DictWriter(output_file, fieldnames=field_names)
        for item in items:
            dictwriter_object.writerow(item)
        output_file.close()