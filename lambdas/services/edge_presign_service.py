import re

from botocore.exceptions import ClientError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)

internal_server_error_response = {
    "status": "500",
    "statusDescription": "Internal Server Error xD",
    "headers": {
        "content-type": [{"key": "Content-Type", "value": "text/plain"}],
        "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
    },
    "body": "Internal Server Error xD",
}

client_error_response = {
    "status": "404",
    "statusDescription": "Not Found :P",
    "headers": {
        "content-type": [{"key": "Content-Type", "value": "text/plain"}],
        "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
    },
    "body": "Not Found :P",
}


class EdgePresignService:

    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()

    def attempt_url_update(self, base_table_name, uri_hash, origin_url):
        try:
            environment = self.extract_environment_from_url(origin_url)
            logger.info(f"Extracted Environment: {environment}")

            table_name = self.extend_table_name(base_table_name, environment)

            self.dynamo_service.update_conditional(
                table_name=table_name,
                key=uri_hash,
                updated_fields={"IsRequested": True},
                condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
                expression_attribute_values={":false": False},
            )
        except ClientError as e:
            logger.error(
                f"[Message]: {str(e)}", {"Result": "Lloyd George stitching failed"}
            )
            return client_error_response
        except Exception as e:
            logger.error(
                f"[Message]: {str(e)}", {"Result": "Lloyd George stitching failed"}
            )
            return internal_server_error_response

    def extract_environment_from_url(self, url):
        match = re.search(r"https://([^.]+)\.", url)
        if match:
            return match.group(1)
        return ""

    def extend_table_name(self, base_table_name, environment):
        if environment:
            return f"{environment}_{base_table_name}"
        return base_table_name
