import json

from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError
from services.base.dynamo_service import DynamoDBService


class EdgePresignService:

    def __init__(
        self,
        table_name: str,
        progress_store_file_path: str = "batch_update_progress.json",
    ):
        self.dynamo_service = DynamoDBService()

    def attempt_url_update(self, table_name, requested_url):
        try:
            # Attempt to update the item only if IsRequested is False or does not exist
            try:
                return self.dynamo_service.update_item(
                    table_name=table_name,
                    key=requested_url,
                    updated_fields={"IsRequested": True},
                    condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
                    expression_attribute_values={":false": False},
                )
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "ConditionalCheckFailedException":
                    # The condition failed, meaning IsRequested was already True
                    return {
                        "status": "404",
                        "statusDescription": "Not Found",
                        "body": "This URL has already been requested and cannot be accessed again.",
                    }
                elif error_code == "ProvisionedThroughputExceededException":
                    # The table's provisioned throughput has been exceeded
                    return {
                        "status": "429",
                        "statusDescription": "Too Many Requests",
                        "body": "Request limit exceeded. Please try again later.",
                    }
                elif error_code == "ResourceNotFoundException":
                    # The table or the requested item does not exist
                    return {
                        "status": "404",
                        "statusDescription": "Not Found",
                        "body": "The requested resource was not found.",
                    }
                else:
                    # For any other ClientError
                    return {
                        "status": "500",
                        "statusDescription": "Internal Server Error",
                        "body": json.dumps(f"An error occurred: {str(e)}"),
                    }

        except EndpointConnectionError:
            # Handle connection errors specifically
            return {
                "status": "502",
                "statusDescription": "Bad Gateway",
                "body": "Unable to reach the DynamoDB service. Please try again later.",
            }

        except BotoCoreError as e:
            # Handle general BotoCore errors (parent of ClientError)
            return {
                "status": "500",
                "statusDescription": "Internal Server Error",
                "body": json.dumps(f"An AWS SDK error occurred: {str(e)}"),
            }

        except Exception as e:
            # Handle any other unforeseen exceptions
            return {
                "status": "500",
                "statusDescription": "Internal Server Error",
                "body": json.dumps(f"An unexpected error occurred: {str(e)}"),
            }
