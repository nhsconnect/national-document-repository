import re

from botocore.exceptions import ClientError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)

internal_server_error_response = {
    "status": "500",
    "statusDescription": "Internal Server Error",
    "headers": {
        "content-type": [{"key": "Content-Type", "value": "text/plain"}],
        "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
    },
    "body": "Internal Server Error",
}

client_error_response = {
    "status": "404",
    "statusDescription": "Not Found",
    "headers": {
        "content-type": [{"key": "Content-Type", "value": "text/plain"}],
        "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
    },
    "body": "Not Found",
}


class EdgePresignService:

    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()
        self.ssm_service = SSMService()
        self.table_name_ssm_param = "EDGE_REFERENCE_TABLE"

    def attempt_url_update(self, uri_hash, origin_url):
        try:
            environment = self.extract_environment_from_url(origin_url)
            logger.info("Extracted Environment", {"Result": {environment}})
            base_table_name = self.ssm_service.get_ssm_parameter(
                self.table_name_ssm_param
            )
            logger.info("Found table name", {"Result": base_table_name})
            formatted_table_name = self.extend_table_name(base_table_name, environment)

            self.dynamo_service.update_conditional(
                table_name=formatted_table_name,
                key=uri_hash,
                updated_fields={"IsRequested": True},
                condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
                expression_attribute_values={":false": False},
            )
        except ClientError as e:
            logger.error(
                f"{str(e)}", {"Result": "CloudFront Edge failed due to client"}
            )
            return client_error_response
        except Exception as e:
            logger.error(
                f"{str(e)}",
                {"Result": "CloudFront Edge failed due to unknown exception"},
            )
            return internal_server_error_response

    def extract_environment_from_url(self, url: str) -> str:
        match = re.search(r"https://([^.]+)\.[^.]+\.[^.]+\.[^.]+", url)
        if match:
            return match.group(1)
        return ""

    def extend_table_name(self, base_table_name, environment):
        if environment:
            return f"{environment}_{base_table_name}"
        return base_table_name
