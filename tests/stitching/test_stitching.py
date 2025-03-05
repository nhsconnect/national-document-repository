import boto3
from boto3.dynamodb.conditions import Key
from pypdf import PdfReader


def get_dlq_message_count(queue_url):
    # Create a new session
    session = boto3.Session()
    # Create SQS client
    sqs = session.client("sqs")

    # Get attributes of the queue
    response = sqs.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages"]
    )
    # Extract the approximate number of messages in the DLQ
    return int(response["Attributes"]["ApproximateNumberOfMessages"])


def test_stitching_function():
    sqs = boto3.client("sqs")
    queue_url = ""
    start_dlq_count = get_dlq_message_count(queue_url)

    sqs.send_message(QueueUrl=queue_url, MessageBody="{}")
    while get_dlq_message_count(queue_url) == start_dlq_count:
        if pdf_stitched():
            assert True, "The PDF has been stitched"
    assert False, "A Message has appeared in the DLQ"


def pdf_stitched():
    pass


def delete_record_from_dynamo(nhs_number, table_name):
    dynamodb = boto3.client("dynamodb")
    table = dynamodb.Table(table_name)

    try:
        response = table.delete_item(Key={"NhsNumber": nhs_number})
        return response
    except Exception as e:
        print(f"Error deleting item: {e}")


def find_guid_by_nhs_number(nhs_number):
    dynamodb = boto3.client("dynamodb")
    table = dynamodb.Table("YourTableName")

    response = table.query(
        IndexName="Id",
        KeyConditionExpression=Key("Id").eq(nhs_number),
    )

    items = response.get("Items", [])
    if not items:
        return None

    return items[0].get("guid")


def download_file_from_s3(bucket_name, object_key, file_name):
    s3 = boto3.client("s3")
    try:
        s3.download_file(bucket_name, object_key, file_name)
        print(f"File {file_name} downloaded successfully from S3 bucket {bucket_name}.")
    except Exception as e:
        print(f"Error downloading file: {e}")


def delete_file_from_s3(bucket_name, file_key):
    s3 = boto3.client("s3")
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_key)
        print(f"File {file_key} deleted from {bucket_name}.")
    except Exception as e:
        print(f"Error deleting {file_key} from {bucket_name}: {e}")


def check_string_in_pdf(file_path, expected_string):
    reader = PdfReader(file_path)
    for page in reader.pages:
        text = page.extract_text()
        if expected_string in text:
            return True
    return False
