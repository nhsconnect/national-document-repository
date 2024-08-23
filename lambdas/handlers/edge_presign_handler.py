# from services.base.s3_service import S3Service
# from services.edge_presign_service import EdgePresignService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]
    return request
    # requested_url = request["uri"]
    # logger.info(f"Info: URL Requested [{requested_url}]")

    # edge_presign_service = EdgePresignService()
    # s3_service = S3Service()

    # # TODO : ADD DYNAMIC TABLE NAME
    # # PULL ENV FROM ORIGIN USE ENV PULL FOR DEFAULT SSM REQ
    # # LOGIC TO CHECK WHETHER ITS PROD TO PREPEND OR NOT
    # table_name = "ndrd_CloudFrontEdgeReference"

    # # Attempt to update the URL in DynamoDB
    # dynamo_response = edge_presign_service.attempt_url_update(table_name, requested_url)
    # logger.info(f"Success Dynamo {str(dynamo_response)}")

    # # If the dynamo_response is a dictionary with a status code, return it
    # if isinstance(dynamo_response, dict) and "status" in dynamo_response:
    #     return dynamo_response

    # # Extract the file key from the requested URL
    # file_key = requested_url.lstrip("/")

    # # Create a presigned URL using S3Service
    # # TODO : ADD DYNAMIC BUCKET NAME

    # s3_bucket_name = "ndrd_lloyd-george-store"
    # presigned_url_response = s3_service.create_download_presigned_url(
    #     s3_bucket_name, file_key
    # )

    # logger.info(f"Success Response: {str(presigned_url_response)}")
    # return presigned_url_response
