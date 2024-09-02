import hashlib
import json
from urllib.parse import parse_qs

from services.edge_presign_service import EdgePresignService
from utils.audit_logging_setup import LoggingService
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = LoggingService(__name__)
default_table_name = "CloudFrontEdgeReference"


@set_request_context_for_logging
def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]
    uri = request["uri"]
    querystring = request.get("querystring", "")

    # Parse the querystring to extract parameters
    query_params = parse_qs(querystring)

    # Extract origin URL from query parameters
    origin_url = query_params.get("origin", [""])[0]

    edge_presign_service = EdgePresignService()
    uri_hash = hashlib.md5(f"{uri}?{querystring}".encode("utf-8")).hexdigest()
    headers = request.get("headers", {})

    logger.info("CloudFront received S3 request", {"Result": json.dumps(request)})

    response = edge_presign_service.attempt_url_update(
        table_name=default_table_name, uri_hash=uri_hash, origin_url=origin_url
    )

    if response is not None:
        return response

    if "authorization" in headers:
        del headers["authorization"]

    return request
