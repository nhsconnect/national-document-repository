import base64

from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class EdgePresignService:

    def __init__(
        self,
    ):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()

    def attempt_url_update(self, table_name, requested_url):
        try:
            try:
                return self.dynamo_service.update_conditional(
                    table_name=table_name,
                    key=requested_url,
                    updated_fields={"IsRequested": True},
                    condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
                    expression_attribute_values={":false": False},
                )
            except ClientError as e:
                error = (
                    "This URL has already been requested and cannot be accessed again"
                )

                logger.error(f"Message: {error}: {str(e)}")
                return {
                    "status": "404",
                    "statusDescription": "Not Found",
                    "body": error,
                }

        except EndpointConnectionError as e:
            error = "Unable to reach the DynamoDB service"

            logger.error(f"Message: {error}: {str(e)}")
            return {"status": "502", "statusDescription": "Bad Gateway", "body": e}

        except BotoCoreError as e:
            error = "An AWS SDK error occurred"

            logger.error(f"Message: {error}: {str(e)}")
            return {
                "status": "500",
                "statusDescription": "Internal Server Error",
                "body": error,
            }

        except Exception as e:
            error = "An unexpected error occurred"

            logger.error(f"Message: {error}: {str(e)}")
            return {
                "status": "500",
                "statusDescription": "Internal Server Error",
                "body": error,
            }

    def get_s3_object(self, bucket_name: str, file_key: str):
        try:
            pdf_object = self.s3_service.get_object(bucket_name, file_key)
            logger.info(f"Success S3 {bucket_name}")

            return self.create_success_response(pdf_object["Body"].read())

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"ClientError occurred: {error_code} - {e}")

            if error_code == "404":
                return {
                    "status": "404",
                    "statusDescription": "Not Found",
                    "body": "The requested PDF object does not exist.",
                }
            else:
                return {
                    "status": "500",
                    "statusDescription": "Internal Server Error",
                    "body": "An error occurred while retrieving the PDF object.",
                }

        except Exception as e:
            # Handle any other unexpected errors
            logger.error(f"Unexpected error occurred: {str(e)}")
            return {
                "status": "500",
                "statusDescription": "Internal Server Error",
                "body": "An unexpected error occurred while retrieving the PDF object.",
            }

    def create_success_response(self, pdf_object):
        res = {
            "status": "200",
            "statusDescription": "OK",
            "headers": {
                "content-type": [{"key": "Content-Type", "value": "application/pdf"}],
                "cache-control": [{"key": "Cache-Control", "value": "max-age=3600"}],
            },
            "body": base64.b64encode(pdf_object).decode("utf-8"),
            "bodyEncoding": "base64",
        }
        return res
