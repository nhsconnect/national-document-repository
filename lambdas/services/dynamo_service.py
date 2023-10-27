import logging

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from utils.dynamo import (
    create_expression_attribute_values,
    create_expressions,
    create_nonexistant_or_empty_attr_filter,
)
from utils.exceptions import DynamoDbException, InvalidResourceIdException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")

    def get_table(self, table_name):
        try:
            return self.dynamodb.Table(table_name)
        except ClientError as e:
            logger.error("Unable to connect to DB")
            logger.error(e)
            raise e

    def query_with_requested_fields(
        self,
        table_name,
        index_name,
        search_key,
        search_condition: str,
        requested_fields: list = None,
        filtered_fields: dict = None,
    ):
        try:
            table = self.get_table(table_name)

            if requested_fields is None or len(requested_fields) == 0:
                raise InvalidResourceIdException

            projection_expression, expression_attribute_names = create_expressions(
                requested_fields
            )

            if not filtered_fields:
                results = table.query(
                    IndexName=index_name,
                    KeyConditionExpression=Key(search_key).eq(search_condition),
                    ExpressionAttributeNames=expression_attribute_names,
                    ProjectionExpression=projection_expression,
                )
            else:
                filtered_field_names = list(filtered_fields.keys())
                filtered_field_values = list(filtered_fields.values())

                fields_filter = create_nonexistant_or_empty_attr_filter(
                    filtered_field_names
                )

                expression_attribute_values = create_expression_attribute_values(
                    filtered_field_names, filtered_field_values
                )

                results = table.query(
                    IndexName=index_name,
                    KeyConditionExpression=Key(search_key).eq(search_condition),
                    FilterExpression=fields_filter,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
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

    def simple_query(self, table_name: str, key_condition_expression):
        """
        Allow querying dynamodb table without explicitly defining the fields to retrieve.
        :param table_name: Dynamodb table name
        :param key_condition_expression: Key condition object generated by boto3.dynamodb.conditions.Key

        example usage:
            from boto3.dynamodb.conditions import Key

            query_response = db_service.simple_query(
                table_name=session_table_name,
                key_condition_expression=Key("NDRSessionId").eq(ndr_session_id)
            )
        """
        try:
            table = self.get_table(table_name)

            results = table.query(KeyConditionExpression=key_condition_expression)
            if results is None or "Items" not in results:
                logger.error(f"Unusable results in DynamoDB: {results!r}")
                raise DynamoDbException("Unrecognised response from DynamoDB")
            return results
        except ClientError as e:
            logger.error(f"Unable to query table: {table_name}")
            logger.error(e)
            raise e

    def create_item(self, table_name, item):
        try:
            table = self.get_table(table_name)
            logger.info(f"Writing item to table: {table_name}")
            table.put_item(Item=item)
        except ClientError as e:
            logger.error(f"Unable to write item to table: {table_name}")
            logger.error(e)
            raise e

    def update_item(
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

    def delete_item(self, table_name: str, key: dict):
        try:
            table = self.get_table(table_name)
            table.delete_item(Key=key)
            logger.info(f"Deleting item in table: {table_name}")
        except ClientError as e:
            logger.error(f"Unable to delete item in table: {table_name}")
            logger.error(e)
            raise e
