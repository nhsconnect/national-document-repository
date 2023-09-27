import os

from botocore.exceptions import ClientError

from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.dynamo_service import DynamoDBService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import validate_id


def lambda_handler(event, context):

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)

        lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]

    except InvalidResourceIdException:
        return ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
    except KeyError as e:
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "GET"
        ).create_api_gateway_response()

    dynamo_service = DynamoDBService()
    try:
        response = dynamo_service.query_service(
            lloyd_george_table_name,
            "NhsNumberIndex",
            "NhsNumber",
            nhs_number,
            [
                DocumentReferenceMetadataFields.ID,
                DocumentReferenceMetadataFields.NHS_NUMBER,
                DocumentReferenceMetadataFields.FILE_LOCATION,
            ],
        )
    except ClientError:
        return ApiGatewayResponse(500, f"Unable to retrieve documents for user {nhs_number}", "GET")







    # Get the patient's list of docs from the NDR LG Dynamo table
    # Download them all in order, their filenames should impose an order
    # File names are stored in Dynamo which is why we need it first
    # Stitch them together in order
    # upload them to S3 - set a TTL on the bucket
    # return pre-signed URL to download and send it to the UI using api response

    pass
