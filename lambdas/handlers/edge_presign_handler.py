import hashlib
import json
import logging
from urllib.parse import parse_qs

from services.edge_presign_service import EdgePresignService

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bad Request response for missing or invalid data
bad_request_response = {
    "status": "400",
    "statusDescription": "Bad Request",
    "headers": {
        "content-type": [{"key": "Content-Type", "value": "text/plain"}],
        "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
    },
    "body": "Invalid request structure or missing data",
}


def lambda_handler(event, context):
    try:
        request = event["Records"][0]["cf"]["request"]
        logger.info(f"CloudFront received S3 request:  ${json.dumps(request)}")
        uri = request.get("uri", "")
        presign_query_string = request.get("querystring", "")

    except (KeyError, IndexError) as e:
        logger.error("Malformed event structure or missing data", {"Result": {str(e)}})
        return bad_request_response

    s3_presign_credentials = parse_qs(presign_query_string)
    origin_url = s3_presign_credentials.get("origin", [""])[0]
    if not origin_url:
        logger.error(
            "Origin URL not provided in presigned credentials",
            {"Result": {presign_query_string}},
        )
        return {
            "status": "400",
            "statusDescription": "Bad Request",
            "headers": {
                "content-type": [{"key": "Content-Type", "value": "text/plain"}],
                "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
            },
            "body": "Origin URL not provided",
        }

    presign_string = f"{uri}?{presign_query_string}"
    encoded_presign_string = presign_string.encode("utf-8")
    presign_credentials_hash = hashlib.md5(encoded_presign_string).hexdigest()

    edge_presign_service = EdgePresignService()
    response = edge_presign_service.attempt_url_update(
        uri_hash=presign_credentials_hash, origin_url=origin_url
    )

    if response:
        return response

    headers = request.get("headers", {})
    if "authorization" in headers:
        del headers["authorization"]

    return request
