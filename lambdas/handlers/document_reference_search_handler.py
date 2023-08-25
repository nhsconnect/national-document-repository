import logging

from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("API Gateway event received - processing starts")
    logger.info(event)

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        # Search metadata table for documents
        # Bundle them
        # Send the response
        return ApiGatewayResponse(200, "OK", "GET")

    except Exception:
        logger.error("An unidentified problem occurred when searching for patient documents")
        return ApiGatewayResponse(500, "An unidentified problem occurred when searching for patient documents", "GET")
    pass
