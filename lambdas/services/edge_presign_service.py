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

    def use_presign(self, request_values: dict) -> dict:
        request_id = self._extract_request_id(request_values)
        domain_name = self._extract_domain_name(request_values)

        presign_url = self.attempt_presign_ingestion(request_id, domain_name)
        self._update_request_with_presign_url(request_values, presign_url)

        return request_values

    def attempt_presign_ingestion(self, request_id: str, domain_name: str) -> str:
        try:
            environment = self._filter_domain_for_env(domain_name)
            table_name = self._get_formatted_table_name(environment)
            updated_item = self._update_dynamo_item(table_name, request_id)
            return self._extract_presigned_url(updated_item)
        except ClientError as e:
            logger.error(f"{str(e)}", {"Result": LambdaError.EdgeNoClient.to_str()})
            raise CloudFrontEdgeException(400, LambdaError.EdgeNoClient)

    def update_s3_headers(self, request: dict) -> dict:
        domain_name = self._extract_domain_name(request)
        request["headers"].pop("authorization", None)
        request["headers"]["host"] = [{"key": "Host", "value": domain_name}]
        return request

    def _extract_request_id(self, request_values: dict) -> str:
        return request_values.get("uri", "").lstrip("/")

    def _extract_domain_name(self, request_values: dict) -> str:
        return request_values.get("origin", {}).get("s3", {}).get("domainName", "")

    def _update_request_with_presign_url(self, request_values: dict, presign_url: str):
        question_mark_index = presign_url.find("?")
        querystring = (
            presign_url[question_mark_index + 1 :] if question_mark_index != -1 else ""
        )
        url_parts = (
            presign_url[:question_mark_index].split("/")
            if question_mark_index != -1
            else presign_url.split("/")
        )
        request_values["querystring"] = querystring
        request_values["uri"] = "/" + "/".join(url_parts[3:])

    def _filter_domain_for_env(self, domain_name: str) -> str:
        match = re.match(r"^[^-]+(?:-[^-]+)?(?=-lloyd)", domain_name)
        return match.group(0) if match else ""

    def _get_formatted_table_name(self, environment: str) -> str:
        base_table_name = self.ssm_service.get_ssm_parameter(self.table_name_ssm_param)
        return f"{environment}_{base_table_name}" if environment else base_table_name

    def _update_dynamo_item(self, table_name: str, request_id: str) -> dict:
        return self.dynamo_service.update_item(
            table_name=table_name,
            key_pair={"ID": request_id},
            updated_fields={"IsRequested": True},
            condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
            expression_attribute_values={":false": False},
        )

    @staticmethod
    def _extract_presigned_url(updated_item: dict) -> str:
        return updated_item.get("Attributes", {}).get("presignedUrl", "")
