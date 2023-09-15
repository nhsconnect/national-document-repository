import json
import logging
import os

from botocore.exceptions import ClientError
from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_query_service import DynamoQueryService
from utils.exceptions import DynamoDbException, InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.nhs_number_validator import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    return ApiGatewayResponse(
    200, json.dumps(os.environ.items()), "GET"
    ).create_api_gateway_response()
