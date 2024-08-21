from services.edge_presign_service import EdgePresignService
from services.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]
    requested_url = request["uri"]
    logger.info(f"Info: URL Requested [{requested_url}]")

    edge_presign_service = EdgePresignService()
    s3_service = S3Service()

    table_name = "ndrd_CloudFrontEdgeReference"

    # Attempt to update the URL in DynamoDB
    dynamo_response = edge_presign_service.attempt_url_update(table_name, requested_url)

    # If the dynamo_response is a dictionary with a status code, return it
    if isinstance(dynamo_response, dict) and "status" in dynamo_response:
        return dynamo_response

    # Extract the file key from the requested URL
    file_key = requested_url.lstrip("/")

    # Create a presigned URL using S3Service
    s3_bucket_name = "ndrd_CloudFrontEdgeReference"
    presigned_url_response = s3_service.create_download_presigned_url(
        s3_bucket_name, file_key
    )

    return presigned_url_response
