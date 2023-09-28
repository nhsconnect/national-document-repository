import logging
import os

from botocore.exceptions import ClientError

from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.dynamo_service import DynamoDBService
from services.pdf_stitch_service import stitch_pdf
from services.s3_service import S3Service
from utils.exceptions import InvalidResourceIdException, DynamoDbException
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
    except KeyError as e:
        return ApiGatewayResponse(
            500, f"An error occurred due to missing key: {str(e)}", "GET"
        ).create_api_gateway_response()

    try:
        response = get_lloyd_george_records_for_patient(
            lloyd_george_table_name, nhs_number
        )
        if len(response["Items"]) == 0:
            return ApiGatewayResponse(
                404, f"Lloyd george record not found for patient {nhs_number}", "GET"
            ).create_api_gateway_response()

        ordered_lg_records = order_response_by_filenames(response["Items"])

        s3_service = S3Service()
        all_lg_parts = download_lloyd_george_files(
            lloyd_george_bucket_name, ordered_lg_records, s3_service
        )

        stitched_lg_record = stitch_pdf(all_lg_parts)

        presign_url_response = upload_stitched_lg_record(
            stitched_lg_record=stitched_lg_record,
            upload_bucket_name=lloyd_george_bucket_name,
            s3_service=s3_service,
        )
        return ApiGatewayResponse(
            200, presign_url_response, "GET"
        ).create_api_gateway_response()

    except DynamoDbException:
        return ApiGatewayResponse(
            500, "Unable to retrieve documents for patient 9000000009", "GET"
        ).create_api_gateway_response()
    except ClientError as e:
        logger.error(e)
        return ApiGatewayResponse(
            500,
            "Unable to upload stitched pdf file to S3 due to internal server error",
            "GET",
        ).create_api_gateway_response()


def get_lloyd_george_records_for_patient(lloyd_george_table_name: str, nhs_number: str):
    try:
        dynamo_service = DynamoDBService()
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
        if response is None or ("Items" not in response):
            logger.error(f"Unrecognised response from DynamoDB: {response}")
            raise DynamoDbException("Unrecognised response from DynamoDB")
        return response["Items"]
    except ClientError as e:
        logger.error(e)
        raise DynamoDbException("Unexpected error when getting Lloyd George record")


def download_lloyd_george_files(
    lloyd_george_bucket_name: str, ordered_lg_records: list[dict], s3_service: S3Service
) -> list[str]:
    all_lg_parts = []
    for lg_part in ordered_lg_records:
        local_file_name = f"/tmp/{lg_part['FileName']}"
        s3_service.download_file(
            lloyd_george_bucket_name, lg_part["ID"], local_file_name
        )
        all_lg_parts.append(local_file_name)
    return all_lg_parts


def upload_stitched_lg_record(
    stitched_lg_record: str, upload_bucket_name: str, s3_service: S3Service
):
    lifecycle_policy_tag = os.environ.get(
        "STITCHED_FILE_LIFECYCLE_POLICY_TAG", "auto_delete"
    )
    filename_on_bucket = "alexCool.pdf"
    s3_service.upload_file_with_tags(
        file_name=stitched_lg_record,
        s3_bucket_name=upload_bucket_name,
        file_key=filename_on_bucket,
        tags={lifecycle_policy_tag: "true"},
    )
    presign_url_response = s3_service.create_download_presigned_url(
        s3_bucket_name=upload_bucket_name, file_key=filename_on_bucket
    )
    return presign_url_response
