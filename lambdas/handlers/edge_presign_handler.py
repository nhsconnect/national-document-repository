import logging

from services.edge_presign_service import EdgePresignService
from utils.decorators.handle_edge_exceptions import handle_edge_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@set_request_context_for_logging
@override_error_check
@handle_edge_exceptions
def lambda_handler(event, context):
    request: dict = event["Records"][0]["cf"]["request"]
    logger.info("Edge received S3 request")
    logger.info(f"Request: {request}")
    logger.info(f"Event: {event}")

    edge_presign_service = EdgePresignService()
    presign = edge_presign_service.use_presign(request)
    question_mark_index = presign.find("?")
    if question_mark_index != -1:
        querystring = presign[question_mark_index + 1 :]
    else:
        querystring = ""

    url_parts = presign[:question_mark_index].split("/")
    request["querystring"] = querystring
    request["uri"] = "/" + "/".join(url_parts[3:])
    forwarded_request: dict = edge_presign_service.update_s3_headers(request)

    logger.info("Edge forwarding S3 request")
    return forwarded_request
