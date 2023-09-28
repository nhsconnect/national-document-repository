import logging
import os

from botocore.exceptions import ClientError

from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.dynamo_service import DynamoDBService
from services.pdf_stitch_service import stitch_pdf
from services.s3_service import S3Service
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.order_response_by_filenames import order_response_by_filenames
from utils.utilities import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)
    except InvalidResourceIdException:
        return ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
    except KeyError as e:
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "GET"
        ).create_api_gateway_response()

    try:
        lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        lifecycle_policy_tag = os.environ.get(
            "STITCHED_FILE_LIFECYCLE_POLICY_TAG", "auto_delete"
        )
    except KeyError as e:
        return ApiGatewayResponse(
            500, f"An error occurred due to missing key: {str(e)}", "GET"
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
                DocumentReferenceMetadataFields.FILE_NAME,
            ],
        )

    except ClientError:
        return ApiGatewayResponse(
            500, f"Unable to retrieve documents for patient {nhs_number}", "GET"
        ).create_api_gateway_response()

    ordered_lg_records = order_response_by_filenames(response["Items"])

    s3_service = S3Service()

    # merger = PdfWriter()

    all_lg_parts = []
    for lg_part in ordered_lg_records:
        s3_service.download_file(
            lloyd_george_bucket_name, lg_part["ID"], lg_part["FileName"]
        )
        all_lg_parts.append(lg_part["FileName"])

    stitched_lg_record_filename = stitch_pdf(all_lg_parts)

    upload_bucket_name = "ndr-dev-lloyd-george-store"
    filename_on_bucket = "alexCool.pdf"

    try:
        s3_service.upload_file_with_tags(
            file_name=stitched_lg_record_filename,
            s3_bucket_name=upload_bucket_name,
            file_key=filename_on_bucket,
            tags={lifecycle_policy_tag: "true"},
        )

        presign_url_response = s3_service.create_download_presigned_url(
            s3_bucket_name=upload_bucket_name, file_key=filename_on_bucket
        )
        return ApiGatewayResponse(
            200, presign_url_response, "GET"
        ).create_api_gateway_response()

    except ClientError as e:
        logger.error(e)
        return ApiGatewayResponse(
            500, "Unable to upload stitched pdf file to S3", "GET"
        ).create_api_gateway_response()
