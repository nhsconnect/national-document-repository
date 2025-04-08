import re

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from services.base.dynamo_service import DynamoDBService
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import CloudFrontEdgeException

logger = LoggingService(__name__)


class EdgePresignService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.ssm_service = SSMService()
        self.table_name_ssm_param = "EDGE_REFERENCE_TABLE"

    def use_presign(self, request_values: dict):
        request_id: str = request_values.get("uri").lstrip("/")
        origin: dict = request_values.get("origin", {})
        domain_name: str = origin["s3"]["domainName"]

        presign_url = self.attempt_presign_ingestion(
            request_id=request_id,
            domain_name=domain_name,
        )
        question_mark_index = presign_url.find("?")
        if question_mark_index != -1:
            querystring = presign_url[question_mark_index + 1 :]
        else:
            querystring = ""

        url_parts = presign_url[:question_mark_index].split("/")
        request_values["querystring"] = querystring
        request_values["uri"] = "/" + "/".join(url_parts[3:])
        return request_values

    def attempt_presign_ingestion(self, request_id: str, domain_name: str) -> str:
        try:
            environment = self.filter_domain_for_env(domain_name)
            logger.info(f"Environment found: {environment}")
            base_table_name: str = self.ssm_service.get_ssm_parameter(
                self.table_name_ssm_param
            )
            formatted_table_name: str = self.extend_table_name(
                base_table_name, environment
            )
            logger.info(f"Table: {formatted_table_name}")
            updated_item = self.dynamo_service.update_item(
                table_name=formatted_table_name,
                key_pair={"ID": request_id},
                updated_fields={"IsRequested": True},
                condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
                expression_attribute_values={":false": False},
            )
            logger.info("Found item related to request ID")
            return updated_item.get("Attributes").get("presignedUrl")
        except ClientError as e:
            logger.error(f"{str(e)}", {"Result": LambdaError.EdgeNoClient.to_str()})
            raise CloudFrontEdgeException(400, LambdaError.EdgeNoClient)

    @staticmethod
    def update_s3_headers(
        request: dict,
    ):
        origin: dict = request.get("origin", {})
        domain_name: str = origin["s3"]["domainName"]
        if "authorization" in request["headers"]:
            del request["headers"]["authorization"]
        request["headers"]["host"] = [{"key": "Host", "value": domain_name}]

        return request

    @staticmethod
    def filter_domain_for_env(domain_name: str) -> str:
        match = re.match(r"^[^-]+(?:-[^-]+)?(?=-lloyd)", domain_name)
        if match:
            return match.group(0)
        return ""

    @staticmethod
    def extend_table_name(base_table_name: str, environment: str) -> str:
        if environment:
            return f"{environment}_{base_table_name}"
        return base_table_name
