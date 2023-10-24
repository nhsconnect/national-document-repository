import os
import boto3
from services.dynamo_service import DynamoDBService

s3_resource = boto3.resource('s3')

def lambda_handler(event, context):
    db_service = DynamoDBService()
    staging_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")

    # Upload temp file to S3
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

# def write_items_to_csv(item: list):
#    with open(TEMP_FILENAME, 'w') as output_file:

#     writer = csv.writer(output_file)
#     writer.writerow(item.keys())
# writer.writerow(item.values())
