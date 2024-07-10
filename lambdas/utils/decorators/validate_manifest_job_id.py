from typing import Callable

from enums.lambda_error import LambdaError
from utils.audit_logging_setup import LoggingService
from utils.lambda_response import ApiGatewayResponse

logger = LoggingService(__name__)


def validate_manifest_job_id(lambda_func: Callable):
    """A decorator for lambda handler.
    Verify that the incoming event contains a valid job ID in the request
    If not, returns a 400 Bad request response before the lambda triggers.

    Usage:
    @validate_manifest_job_id
    def lambda_handler(event, context):
        ...
    """

    def interceptor(event, context):
        try:
            job_id = event["queryStringParameters"].get("jobId")
            if job_id is None:
                return ApiGatewayResponse(
                    400,
                    LambdaError.ManifestMissingJobId.create_error_body(),
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
