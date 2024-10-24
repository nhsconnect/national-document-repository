import hashlib

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import CloudFrontEdgeException

logger = LoggingService(__name__)


class EdgePresignService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()
        self.ssm_service = SSMService()
        self.table_name_ssm_param = "EDGE_REFERENCE_TABLE"

    def attempt_url_update(self, uri_hash, domain_name) -> None:
        try:
            environment = self.extract_environment_from_domain(domain_name)
            logger.info(f"Environment found: {environment}")
            base_table_name: str = self.ssm_service.get_ssm_parameter(
                self.table_name_ssm_param
            )
            formatted_table_name: str = self.extend_table_name(
                base_table_name, environment
            )
            logger.info(f"Table: {formatted_table_name}")
            self.dynamo_service.update_item(
                table_name=formatted_table_name,
                key=uri_hash,
                updated_fields={"IsRequested": True},
                condition_expression="attribute_not_exists(IsRequested) OR IsRequested = :false",
                expression_attribute_values={":false": False},
            )
        except ClientError as e:
            logger.error(f"{str(e)}", {"Result": LambdaError.EdgeNoClient.to_str()})
            raise CloudFrontEdgeException(400, LambdaError.EdgeNoClient)

    def presign_request(self, request_values):
        uri = request_values["uri"]
        querystring = request_values["querystring"]
        domain_name = request_values["domain_name"]

        presign_string = f"{uri}?{querystring}"
        encoded_presign_string = presign_string.encode("utf-8")
        presign_credentials_hash = hashlib.md5(encoded_presign_string).hexdigest()

        self.attempt_url_update(
            uri_hash=presign_credentials_hash,
            domain_name=domain_name,
        )

    @staticmethod
    def prepare_s3_response(request, request_values):
        domain_name = request_values["domain_name"]
        if "authorization" in request["headers"]:
            del request["headers"]["authorization"]
        request["headers"]["host"] = [{"key": "Host", "value": domain_name}]

        return request

    @staticmethod
    def extract_request_values(request) -> dict:
        try:
            uri = request["uri"]
            querystring = request["querystring"]
            headers = request["headers"]
            origin = request.get("origin", {})
            domain_name = origin["s3"]["domainName"]
        except KeyError as e:
            logger.error(f"Missing request component: {str(e)}")
            raise CloudFrontEdgeException(500, LambdaError.EdgeNoOrigin)

        return {
            "uri": uri,
            "querystring": querystring,
            "headers": headers,
            "domain_name": domain_name,
        }
