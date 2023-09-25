import logging
import os

from botocore.exceptions import ClientError
from pydantic import ValidationError

from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.virus_scan import VirusScannedEvent, ScanResult
from services.dynamo_service import DynamoDBService
from utils.exceptions import VirusScanEventHandleError
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _context):
    logger.info(f"Received events: {event}")

    dynamo_service = DynamoDBService()

    for record in event["Records"]:
        try:
            virus_scanned_event = VirusScannedEvent.model_validate(
                record["Sns"]["Message"]
            )
            handle_virus_scanned_event(
                virus_scanned_event=virus_scanned_event, dynamo_service=dynamo_service
            )
        except ClientError as e:
            logger.error(e)
            raise e
        except (ValidationError, KeyError) as e:
            logger.info("Failed to interpret virus scanned event:")
            logger.info(record)
            logger.error(e)
        except Exception as e:
            logger.info("Got unexpected error when handling virus scanned event:")
            logger.error(e)

    return ApiGatewayResponse(200, "", "PATCH").create_api_gateway_response()


def handle_virus_scanned_event(
    virus_scanned_event: VirusScannedEvent, dynamo_service: DynamoDBService
):
    logger.info(f"handling virus scanned event: {virus_scanned_event}")

    document_store_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    document_store_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
    lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
    lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]

    if virus_scanned_event.bucketName == document_store_bucket_name:
        table_name = document_store_table_name
    elif virus_scanned_event.bucketName == lloyd_george_bucket_name:
        table_name = lloyd_george_table_name
    else:
        logger.info(
            f"Cannot determine the dynamodb table name for event: {virus_scanned_event}"
        )
        raise VirusScanEventHandleError()

    # TODO: add proper logic to set doc location to quarantine bucket
    if virus_scanned_event.result == ScanResult.INFECTED:
        quarantine_bucket_name = "QuarantineBucket"
        document_location = f"s3://{quarantine_bucket_name}/{virus_scanned_event.key}"
    else:
        document_location = (
            f"s3://{virus_scanned_event.bucketName}/{virus_scanned_event.key}"
        )

    virus_result_column_name = DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT.value[0]  # fmt: skip
    file_location_column_name = DocumentReferenceMetadataFields.FILE_LOCATION.value[0]

    logger.info(
        f"Updating DocumentReference {virus_scanned_event.key} to uploaded and "
        f"adding virusScan result as {virus_scanned_event.result}"
    )
    dynamo_service.update_item_service(
        table_name=table_name,
        key={"ID": virus_scanned_event.key},
        update_expression=f"SET {virus_result_column_name}=:result, "
        f"{file_location_column_name}=:location, "
        f"documentUploaded=:true",
        expression_attribute_values={
            ":result": {"S": virus_scanned_event.result},
            ":location": {"S": document_location},
            ":true": {"BOOL": True},
        },
    )
