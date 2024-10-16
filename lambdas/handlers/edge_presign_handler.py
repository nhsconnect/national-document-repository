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


@set_request_context_for_logging
@override_error_check
@handle_edge_exceptions
def lambda_handler(event, context):
    try:
        request: dict = event["Records"][0]["cf"]["request"]
        logger.info("CloudFront received S3 request", {"Result": {json.dumps(request)}})
        uri: str = request.get("uri", "")
        presign_query_string: str = request.get("querystring", "")
        domain_name: str = request["origin"]["s3"]["domainName"]

    except (KeyError, IndexError) as e:
        logger.error(
            f"{str(e)}",
            {"Result": {LambdaError.EdgeMalformed.to_str()}},
        )
        raise CloudFrontEdgeException(500, LambdaError.EdgeMalformed)

    presign_string = f"{uri}?{presign_query_string}"
    encoded_presign_string: str = presign_string.encode("utf-8")
    presign_credentials_hash = hashlib.md5(encoded_presign_string).hexdigest()

    edge_presign_service = EdgePresignService()
    edge_presign_service.attempt_url_update(
        uri_hash=presign_credentials_hash,
        domain_name=domain_name,
    )

    headers: dict = request.get("headers", {})
    for header_key, header_values in headers.items():
        if isinstance(header_values, list) and len(header_values) > 0:
            header_value = header_values[0].get("value", "")
            logger.info(f"Header - {header_key}: {header_value}")
        else:
            logger.info(f"Header - {header_key}: [No Value]")

    if "Authorization" in headers:
        del headers["Authorization"]
    request["headers"] = headers

    return request
