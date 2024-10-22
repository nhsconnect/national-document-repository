import hashlib
import json
import logging

from enums.lambda_error import LambdaError
from services.edge_presign_service import EdgePresignService
from utils.decorators.handle_edge_exceptions import handle_edge_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import CloudFrontEdgeException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REQUIRED_QUERY_PARAMS = [
    "X-Amz-Algorithm",
    "X-Amz-Credential",
    "X-Amz-Date",
    "X-Amz-Expires",
    "X-Amz-SignedHeaders",
    "X-Amz-Signature",
    "X-Amz-Security-Token",
]

REQUIRED_HEADERS = ["host", "cloudfront-viewer-country", "x-forwarded-for"]


@set_request_context_for_logging
@override_error_check
@handle_edge_exceptions
def lambda_handler(event, context):
    try:
        request: dict = event["Records"][0]["cf"]["request"]
        logger.info(f"CloudFront received S3 request {json.dumps(request)}")
        uri: str = request["uri"]
        querystring: str = request["querystring"]
        headers: dict = request["headers"]
        try:
            origin = request.get("origin", {})
            domain_name = origin["s3"]["domainName"]
        except KeyError as e:
            logger.error(
                f"Missing origin: {str(e)}",
                {"Result": LambdaError.EdgeNoOrigin.to_str()},
            )
            raise CloudFrontEdgeException(500, LambdaError.EdgeNoOrigin)

        try:
            query_params = {
                k: v
                for k, v in (x.split("=") for x in querystring.split("&") if "=" in x)
            }
        except ValueError:
            logger.error(f"Malformed query string: {querystring}")
            raise CloudFrontEdgeException(500, LambdaError.EdgeMalformedQuery)

        missing_query_params = [
            param for param in REQUIRED_QUERY_PARAMS if param not in query_params
        ]
        if missing_query_params:
            logger.error(f"Missing required query parameters: {missing_query_params}")
            raise CloudFrontEdgeException(500, LambdaError.EdgeMalformedQuery)

        missing_headers = [
            header for header in REQUIRED_HEADERS if header.lower() not in headers
        ]
        if missing_headers:
            logger.error(f"Missing required headers: {missing_headers}")
            raise CloudFrontEdgeException(500, LambdaError.EdgeMalformedHeader)

        presign_string = f"{uri}?{querystring}"
        encoded_presign_string: str = presign_string.encode("utf-8")
        presign_credentials_hash = hashlib.md5(encoded_presign_string).hexdigest()

        edge_presign_service = EdgePresignService()
        edge_presign_service.attempt_url_update(
            uri_hash=presign_credentials_hash,
            domain_name=domain_name,
        )

        if "authorization" in headers:
            del headers["authorization"]

        request["headers"] = headers
        request["headers"]["host"] = [{"key": "Host", "value": domain_name}]
        logger.info(f"Edge Response: {json.dumps(request)}")

        return request

    except (KeyError, IndexError) as e:
        logger.error(
            f"Generic Edge Malformed Error: {str(e)}",
            {"Result": LambdaError.EdgeMalformed.to_str()},
        )
        raise CloudFrontEdgeException(500, LambdaError.EdgeMalformed)
