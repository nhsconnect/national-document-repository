import logging

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from enums.metadata_field_names import DynamoField

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALL_FIELDS = "ID, ContentType, Created, DocumentUploaded, FileName, Indexed, Location, NhsNumber, Type, VirusScanResult"


class DynamoQueryService:
    def __init__(self, table_name):
        self.TABLE_NAME = table_name

    def __call__(self, nhs_number: str, requested_fields: list = None):
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(self.TABLE_NAME)

            if requested_fields is None:
                requested_fields = DynamoField.list()

            projection_expression, expression_attribute_names = self.create_expressions(requested_fields)

            return table.query(
                IndexName='NhsNumberIndex',
                KeyConditionExpression=Key('NhsNumber').eq(nhs_number),
                ExpressionAttributeNames=expression_attribute_names,
                ProjectionExpression=projection_expression
            )

        except ClientError as e:
            logger.error("Unable to connect to DB")
            logger.error(e)
            raise e

    # Make the expressions
    # ExpressionAttributeNames = {"#create": "Created", "#file": "FileName", "#doc": "DocumentUploaded"}
    # ProjectionExpression = "#id,#create,#file,#doc"
    @staticmethod
    def create_expressions(requested_fields: list):
        projection_expression = ""
        expression_attribute_names = ""

        for field_definition in requested_fields:
            if len(projection_expression) > 0:
                projection_expression = "{},{}".format(projection_expression, field_definition.field_alias)
            else:
                projection_expression = field_definition.field_alias

            new_attribute_name_expression = '"{}":"{}"'.format(field_definition.field_alias,
                                                               field_definition.field_name)

            if len(expression_attribute_names) > 0:
                expression_attribute_names = "{},{}".format(expression_attribute_names,
                                                            new_attribute_name_expression)
            else:
                expression_attribute_names = new_attribute_name_expression

        return projection_expression, expression_attribute_names
