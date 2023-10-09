from typing import Callable

from enums.supported_document_types import SupportedDocumentTypes
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse


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
                    400, "docType not supplied", "GET"
                ).create_api_gateway_response()
            if not doc_type_is_valid(doc_type):
                return ApiGatewayResponse(
                    400, "Invalid document type requested", "GET"
                ).create_api_gateway_response()
        except KeyError as e:
            return ApiGatewayResponse(
                400, f"An error occurred due to missing key: {str(e)}", "GET"
            ).create_api_gateway_response()

        # Validation done. Return control flow to original lambda handler
        return lambda_func(event, context)

    return interceptor


def doc_type_is_valid(doc_type: SupportedDocumentTypes) -> bool:
    return SupportedDocumentTypes.ARF.name in doc_type or \
        SupportedDocumentTypes.LG.name in doc_type
