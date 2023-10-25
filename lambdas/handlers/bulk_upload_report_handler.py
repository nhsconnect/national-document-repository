import csv
import datetime
import os

from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service


def lambda_handler(event, context):
    db_service = DynamoDBService()
    s3_service = S3Service()
    staging_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
    start_time, end_time = get_times_for_scan()
    report_data = get_dynamo_data(db_service, start_time.timestamp(), end_time.timestamp())
    file_name = f'Bulk upload report for {str(start_time)} to {str(end_time)}'
    write_items_to_csv(report_data, file_name)
    s3_service.upload_file(s3_bucket_name=staging_bucket_name, file_key=file_name, file_name=f'reports/{file_name}')

def get_dynamo_data(db_service, start_timestamp, end_timestamp):
    bulk_upload_table_name = os.getenv("BULK_UPLOAD_DYNAMODB")
    db_response = db_service.scan_table(bulk_upload_table_name)
    last_key = db_response['LastEvaluatedKey']
    items = db_response['Items']
    filter_time = f"Attr('timestamp').gt({start_timestamp})&Attr('timestamp').lt({end_timestamp})"
    while last_key:
        db_response = db_service.scan_table(bulk_upload_table_name, exclusive_start_key=last_key, filter_expression=filter_time)
        last_key = db_response['LastEvaluatedKey']
        items.append(db_response['Items'])
    return items

def write_items_to_csv(items: list, csv_file_path: str):
   with open(csv_file_path, 'w') as output_file:
        field_names = items[0].keys()
        dict_writer_object = csv.DictWriter(output_file, fieldnames=field_names)
        for item in items:
            dict_writer_object.writerow(item)
        output_file.close()

def get_times_for_scan():
    current_time = datetime.datetime.now()
    seven_pm_time = datetime.time(19, 0, 0)
    today_date = datetime.datetime.today()
    end_timestamp = datetime.datetime.combine(today_date, seven_pm_time)
    if current_time < end_timestamp:
        end_timestamp -= datetime.timedelta(days=1)
    start_timestamp = end_timestamp - datetime.timedelta(days=1)
    return start_timestamp, end_timestamp

