import hashlib
import json

from services.edge_presign_service import EdgePresignService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)
table_name = "ndrd_CloudFrontEdgeReference"


def lambda_handler(event, context):
    request = event["Records"][0]["cf"]["request"]
    uri = request["uri"]
    querystring = request.get("querystring", "")
    edge_presign_service = EdgePresignService()
    uri_hash = hashlib.md5(f"{uri}?{querystring}".encode("utf-8")).hexdigest()
    headers = request.get("headers", {})
    origin_url = headers.get("x-origin-url", [{}])[0].get("value", "")
    logger.info("CloudFront received S3 request", {"Result": json.dumps(request)})
    response = edge_presign_service.attempt_url_update(
        table_name="CloudFrontEdgeReference", uri_hash=uri_hash, origin_url=origin_url
    )
    if response is not None:
        return response

    if "authorization" in headers:
        del headers["authorization"]
    return request
