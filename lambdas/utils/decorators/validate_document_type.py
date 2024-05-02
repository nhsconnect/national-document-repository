from typing import Callable

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.document_type_utils import doc_type_is_valid
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


def validate_document_type(lambda_func: Callable):
    """A decorator for lambda handler.
    Verify that the incoming event contains a valid document Type (ARF or LG)
    If not, returns a 400 Bad request response before the lambda triggers.

    Usage:
    @validate_patient_id
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        try:
            doc_type = event["queryStringParameters"]["docType"]
            if doc_type is None:
                return ApiGatewayResponse(
                    400,
                    LambdaError.DocTypeNull.create_error_body(),
                    event["httpMethod"],
                ).create_api_gateway_response()
            if not doc_type_is_valid(doc_type):
                return ApiGatewayResponse(
                    400,
                    LambdaError.DocTypeInvalid.create_error_body(),
                    event["httpMethod"],
                ).create_api_gateway_response()
        except KeyError as e:
            logger.info({str(e)}, {"Result": "An error occurred due to missing key"})
            return ApiGatewayResponse(
                400,
                LambdaError.DocTypeKey.create_error_body(),
                event["httpMethod"],
            ).create_api_gateway_response()

        # Validation done. Return control flow to original lambda handler
        return lambda_func(event, context)

    return interceptor
