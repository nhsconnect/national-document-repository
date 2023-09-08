import logging

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from utils.exceptions import DynamoDbException, InvalidResourceIdException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoQueryService:
    def __init__(self, table_name, index_name):
        self.TABLE_NAME = table_name
        self.INDEX_NAME = index_name

    def __call__(
        self, search_key, search_condition: str, requested_fields: list = None
    ):
        
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(self.TABLE_NAME)

            if requested_fields is None or len(requested_fields) == 0:
                raise InvalidResourceIdException

            projection_expression, expression_attribute_names = self.create_expressions(
                requested_fields
            )

            results = table.query(
                IndexName=self.INDEX_NAME,
                KeyConditionExpression=Key(search_key).eq(search_condition),
                ExpressionAttributeNames=expression_attribute_names,
                ProjectionExpression=projection_expression,
            )

            if results is None or "Items" not in results:
                logger.error(f"Unusable results in DynamoDB: {results!r}")
                raise DynamoDbException("Unrecognised response from DynamoDB")
            
            return results    

    # Make the expressions
    # ExpressionAttributeNames = {"#create": "Created", "#file": "FileName", "#doc": "DocumentUploaded"}
    # ProjectionExpression = "#id,#create,#file,#doc"
    @staticmethod
    def create_expressions(requested_fields: list):
        projection_expression = ""
        expression_attribute_names = {}

        for field_definition in requested_fields:
            if len(projection_expression) > 0:
                projection_expression = (
                    f"{projection_expression},{field_definition.field_alias}"
                )
            else:
                projection_expression = field_definition.field_alias

            expression_attribute_names[field_definition.field_alias] = str(
                field_definition.field_name
            )

        return projection_expression, expression_attribute_names
