import csv
import datetime
import logging
import os

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    db_service = DynamoDBService()
    s3_service = S3Service()
    try:
        report_handler(db_service, s3_service)
    except ClientError as e:
        logger.error("Report creation failed")
        logger.error(e.response)


def report_handler(db_service, s3_service):
    staging_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
    start_time, end_time = get_times_for_scan()
    report_data = get_dynamo_data(
        db_service, int(start_time.timestamp()), int(end_time.timestamp())
    )
    file_name = f"Bulk upload report for {str(start_time)} to {str(end_time)}"
    write_items_to_csv(report_data, f"/tmp/{file_name}.csv")
    logger.info("Uploading new report file to S3")
    s3_service.upload_file(
        s3_bucket_name=staging_bucket_name,
        file_key=f"reports/{file_name}",
        file_name=f"/tmp/{file_name}.csv",
    )


def get_dynamo_data(db_service, start_timestamp, end_timestamp):
    logger.info("Starting Scan on DynamoDB table")
    bulk_upload_table_name = os.getenv("BULK_UPLOAD_DYNAMODB_NAME")
    filter_time = Attr("Timestamp").gt(start_timestamp) & Attr("Timestamp").lt(
        end_timestamp
    )
    db_response = db_service.scan_table(
        bulk_upload_table_name, filter_expression=filter_time
    )
    items = db_response["Items"]
    while "LastEvaluatedKey" in db_response:
        db_response = db_service.scan_table(
            bulk_upload_table_name,
            exclusive_start_key=db_response["LastEvaluatedKey"],
            filter_expression=filter_time,
        )
        items.append(db_response["Items"])
    return items


def write_items_to_csv(items: list, csv_file_path: str):
    logger.info("Writing scan results to csv file")
    with open(csv_file_path, "w") as output_file:
        field_names = items[0].keys()
        dict_writer_object = csv.DictWriter(output_file, fieldnames=field_names)
        dict_writer_object.writeheader()
        for item in items:
            dict_writer_object.writerow(item)
        output_file.close()


def get_times_for_scan():
    current_time = datetime.datetime.now()
    end_report_time = datetime.time(6, 59, 59, 0)
    today_date = datetime.datetime.today()
    end_timestamp = datetime.datetime.combine(today_date, end_report_time)
    if current_time < end_timestamp:
        end_timestamp -= datetime.timedelta(days=1)
    start_timestamp = (
        end_timestamp - datetime.timedelta(days=1) + datetime.timedelta(seconds=1)
    )
    return start_timestamp, end_timestamp
