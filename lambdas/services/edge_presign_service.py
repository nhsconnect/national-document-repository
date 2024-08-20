from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class EdgePresignService:

    def __init__(
        self,
    ):
        self.dynamo_service = DynamoDBService()

    def attempt_url_update(self, table_name, requested_url):
        try:
            try:
                return self.dynamo_service.update_item(
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
