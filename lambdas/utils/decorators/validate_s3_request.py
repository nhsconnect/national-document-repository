import logging
from functools import wraps
from urllib.parse import parse_qs

from enums.lambda_error import LambdaError
from utils.lambda_exceptions import CloudFrontEdgeException

logger = logging.getLogger(__name__)

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


def validate_s3_request(lambda_func):
    @wraps(lambda_func)
    def wrapper(event, context):
        request: dict = event["Records"][0]["cf"]["request"]
        bad_request: bool = (
            "uri" not in request
            or "querystring" not in request
            or "headers" not in request
        )
        if bad_request:
            logger.error(
                "Missing required request components: uri, querystring, or headers."
            )
            raise CloudFrontEdgeException(500, LambdaError.EdgeMalformed)

        origin: dict = request.get("origin", {})
        if "s3" not in origin or "domainName" not in origin["s3"]:
            logger.error("Missing origin domain name.")
            raise CloudFrontEdgeException(500, LambdaError.EdgeNoOrigin)

        querystring: str = request["querystring"]
        if not querystring:
            logger.error(f"Missing query string: {querystring}")
            raise CloudFrontEdgeException(500, LambdaError.EdgeNoQuery)

        query_params: dict = {
            query: value[0] for query, value in parse_qs(querystring).items()
        }
        missing_query_params: list = [
            param for param in REQUIRED_QUERY_PARAMS if param not in query_params
        ]
        if missing_query_params:
            logger.error(f"Missing required query parameters: {missing_query_params}")
            raise CloudFrontEdgeException(500, LambdaError.EdgeRequiredQuery)

        headers: dict = request["headers"]
        missing_headers = [
            header for header in REQUIRED_HEADERS if header.lower() not in headers
        ]
        if missing_headers:
            logger.error(f"Missing required headers: {missing_headers}")
            raise CloudFrontEdgeException(500, LambdaError.EdgeRequiredHeaders)

        return lambda_func(event, context)

    return wrapper
