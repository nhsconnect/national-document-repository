import logging

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from utils.exceptions import DynamoDbException, InvalidResourceIdException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")

    def get_table(self, table_name):
        try:
            return self.dynamodb.Table(table_name)
        except ClientError as e:
            logger.error("Unable to connect to DB")
            logger.error(e)
            raise e

    def query_service(
        self,
        table_name,
        index_name,
        search_key,
        search_condition: str,
        requested_fields: list = None,
    ):
        try:
            table = self.get_table(table_name)

            if requested_fields is None or len(requested_fields) == 0:
                raise InvalidResourceIdException

            projection_expression, expression_attribute_names = self.create_expressions(
                requested_fields
            )

            results = table.query(
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
            logger.error(f"Unable to query table: {table_name}")
            logger.error(e)
            raise e

    def post_item_service(self, table_name, item):
        try:
            table = self.get_table(table_name)
            logger.info(f"Writing item to table: {table_name}")
            table.put_item(Item=item)
        except ClientError as e:
            logger.error(f"Unable to write item to table: {table_name}")
            logger.error(e)
            raise e

    def update_item_service(
        self, table_name, key, update_expression, expression_attribute_values
    ):
        try:
            table = self.get_table(table_name)
            table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
            logger.info(f"Updating item in table: {table_name}")
        except ClientError as e:
            logger.error(f"Unable to update item in table: {table_name}")
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
