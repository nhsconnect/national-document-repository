import logging

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from utils.exceptions import DynamoDbException, InvalidResourceIdException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoDBService:
    def __init__(self, table_name):
        try:
            self.TABLE_NAME = table_name
            dynamodb = boto3.resource("dynamodb")
            self.table = dynamodb.Table(self.TABLE_NAME)
        except ClientError as e:
            logger.error("Unable to connect to DB")
            logger.error(e)
            raise e

    def query_service(
        self, index_name, search_key, search_condition: str, requested_fields: list = None
    ):
        try:
            if requested_fields is None or len(requested_fields) == 0:
                raise InvalidResourceIdException

            projection_expression, expression_attribute_names = self.create_expressions(
                requested_fields
            )

            results = self.table.query(
                IndexName=index_name,
                KeyConditionExpression=Key(search_key).eq(search_condition),
                ExpressionAttributeNames=expression_attribute_names,
                ProjectionExpression=projection_expression,
            )

            if results is None or "Items" not in results:
                logger.error(f"Unusable results in DynamoDB: {results!r}")
                raise DynamoDbException("Unrecognised response from DynamoDB")

            return results
        except ClientError as e:
            logger.error("Unable to get query")
            logger.error(e)
            raise e

    def post_item_service(self, item):
        try:
            self.table.put_item(
                Item=item
            )
            logger.info(f"Saving item to DynamoDB: {self.TABLE_NAME}")
        except ClientError as e:
            logger.error("Unable to get write to table")
            logger.error(e)
            raise e

    def update_item_service(self, key, update_expression, expression_attribute_values):
        try:
            self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            logger.info(f"Saving item to DynamoDB: {self.TABLE_NAME}")
        except ClientError as e:
            logger.error("Unable to get write to table")
            logger.error(e)
            raise e

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
