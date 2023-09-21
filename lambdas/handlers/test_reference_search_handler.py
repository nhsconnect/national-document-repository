import json
import logging
import os

from dotenv import load_dotenv
from botocore.exceptions import ClientError
from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from services.dynamo_query_service import DynamoQueryService
from utils.exceptions import DynamoDbException, InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.nhs_number_validator import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    
    dotenv_path = Path('../.env')
    load_dotenv(dotenv_path=dotenv_path)
    list_of_table_names = json.loads(os.environ["DYNAMODB_TABLE_LIST"])

    return ApiGatewayResponse(
    200, json.dumps(list_of_table_names), "GET"
    ).create_api_gateway_response()
