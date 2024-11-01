import logging

from services.edge_presign_service import EdgePresignService
from utils.decorators.handle_edge_exceptions import handle_edge_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_s3_request import validate_s3_request

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@set_request_context_for_logging
@override_error_check
@handle_edge_exceptions
@validate_s3_request
def lambda_handler(event, context):
    request: dict = event["Records"][0]["cf"]["request"]
    logger.info("Edge received S3 request")

    edge_presign_service = EdgePresignService()
    request_values: dict = edge_presign_service.filter_request_values(request)
    edge_presign_service.use_presign(request_values)

    forwarded_request: dict = edge_presign_service.update_s3_headers(
        request, request_values
    )

    logger.info("Edge forwarding S3 request")
    return forwarded_request
