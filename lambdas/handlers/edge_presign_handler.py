import hashlib
import json
import logging
from urllib.parse import parse_qs

from enums.lambda_error import LambdaError
from services.edge_presign_service import EdgePresignService
from utils.decorators.handle_edge_exceptions import handle_edge_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.lambda_exceptions import CloudFrontEdgeException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@set_request_context_for_logging
@override_error_check
@handle_edge_exceptions
def lambda_handler(event, context):
    try:
        request: dict = event["Records"][0]["cf"]["request"]
        logger.info("CloudFront received S3 request", {"Result": {json.dumps(request)}})
        uri: str = request.get("uri", "")
        presign_query_string: str = request.get("querystring", "")

    except (KeyError, IndexError) as e:
        logger.error(
            f"{str(e)}",
            {"Result": {LambdaError.EdgeMalformed.to_str()}},
        )
        raise CloudFrontEdgeException(500, LambdaError.EdgeMalformed)

    s3_presign_credentials = parse_qs(presign_query_string)
    origin_url = s3_presign_credentials.get("origin", [""])[0]
    if not origin_url:
        logger.error(
            "No Origin",
            {"Result": {LambdaError.EdgeNoOrigin.to_str()}},
        )
        raise CloudFrontEdgeException(500, LambdaError.EdgeNoOrigin)

    presign_string = f"{uri}?{presign_query_string}"
    encoded_presign_string: str = presign_string.encode("utf-8")
    presign_credentials_hash = hashlib.md5(encoded_presign_string).hexdigest()

    edge_presign_service = EdgePresignService()
    edge_presign_service.attempt_url_update(
        uri_hash=presign_credentials_hash, origin_url=origin_url
    )

    headers: dict = request.get("headers", {})
    if "authorization" in headers:
        del headers["authorization"]
    request["headers"] = headers
    request["querystring"] = ""

    return request
