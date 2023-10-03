import json
import logging
import os
import tempfile
from urllib import parse
from urllib.parse import urlparse

from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from pypdf.errors import PyPdfError
from services.dynamo_service import DynamoDBService
from services.pdf_stitch_service import stitch_pdf
from services.s3_service import S3Service
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event, validate_patient_id)
from utils.exceptions import DynamoDbException
from utils.lambda_response import ApiGatewayResponse
from utils.order_response_by_filenames import order_response_by_filenames

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@validate_patient_id
@ensure_environment_variables(
    names=["LLOYD_GEORGE_DYNAMODB_NAME", "LLOYD_GEORGE_BUCKET_NAME"]
)
def lambda_handler(event, context):
    nhs_number = extract_nhs_number_from_event(event)
    lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
    lloyd_george_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]

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
    except (ClientError, DynamoDbException) as e:
        logger.error(e)
        return ApiGatewayResponse(
            500, f"Unable to retrieve documents for patient {nhs_number}", "GET"
        ).create_api_gateway_response()

    try:
        filename_for_stitched_file = make_filename_for_stitched_file(response["Items"])
        stitched_lg_record = stitch_pdf(all_lg_parts)

        number_of_files = len(response["Items"])
        last_updated = get_most_recent_created_date(response["Items"])
        total_file_size = get_total_file_size(all_lg_parts)
        presign_url = upload_stitched_lg_record_and_retrieve_presign_url(
            stitched_lg_record=stitched_lg_record,
            filename_on_bucket=f"{nhs_number}/{filename_for_stitched_file}",
            upload_bucket_name=lloyd_george_bucket_name,
            s3_service=s3_service,
        )
        response = json.dumps(
            {
                "number_of_files": number_of_files,
                "last_updated": last_updated,
                "presign_url": presign_url,
                "total_file_size_in_byte": total_file_size,
            }
        )
        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()
    except (ClientError, PyPdfError, FileNotFoundError) as e:
        logger.error(e)
        return ApiGatewayResponse(
            500,
            "Unable to return stitched pdf file due to internal error",
            "GET",
        ).create_api_gateway_response()


def get_lloyd_george_records_for_patient(
    lloyd_george_table_name: str, nhs_number: str
) -> dict:
    try:
        dynamo_service = DynamoDBService()
        response = dynamo_service.query_service(
            lloyd_george_table_name,
            "NhsNumberIndex",
            "NhsNumber",
            nhs_number,
            [
                DocumentReferenceMetadataFields.ID,
                DocumentReferenceMetadataFields.FILE_LOCATION,
                DocumentReferenceMetadataFields.NHS_NUMBER,
                DocumentReferenceMetadataFields.FILE_NAME,
                DocumentReferenceMetadataFields.CREATED,
            ],
        )
        if response is None or ("Items" not in response):
            logger.error(f"Unrecognised response from DynamoDB: {response}")
            raise DynamoDbException("Unrecognised response from DynamoDB")
        return response
    except ClientError as e:
        logger.error(e)
        raise DynamoDbException("Unexpected error when getting Lloyd George record")


def download_lloyd_george_files(
    lloyd_george_bucket_name: str, ordered_lg_records: list[dict], s3_service: S3Service
) -> list[str]:
    all_lg_parts = []
    temp_folder = tempfile.mkdtemp()
    for lg_part in ordered_lg_records:
        file_location_on_s3 = lg_part[
            DocumentReferenceMetadataFields.FILE_LOCATION.field_name
        ]
        original_file_name = lg_part[DocumentReferenceMetadataFields.FILE_NAME.field_name]  # fmt: skip

        s3_file_name = urlparse(file_location_on_s3).path.lstrip("/")

        local_file_name = os.path.join(temp_folder, original_file_name)
        s3_service.download_file(
            lloyd_george_bucket_name, s3_file_name, local_file_name
        )
        all_lg_parts.append(local_file_name)
    return all_lg_parts


def make_filename_for_stitched_file(dynamo_response: list[dict]) -> str:
    # Build a filename with this pattern:
    # Combined_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf

    filename_key = DocumentReferenceMetadataFields.FILE_NAME.field_name
    base_filename = dynamo_response[0][filename_key]
    end_of_total_page_numbers = base_filename.index("_")

    return "Combined" + base_filename[end_of_total_page_numbers:]


def get_most_recent_created_date(dynamo_response: list[dict]) -> str:
    created_date_key = DocumentReferenceMetadataFields.CREATED.field_name
    return max(lg_part[created_date_key] for lg_part in dynamo_response)


def get_total_file_size(filepaths: list[str]) -> int:
    # Return the sum of a list of files (unit: byte)
    return sum(os.path.getsize(filepath) for filepath in filepaths)


def upload_stitched_lg_record_and_retrieve_presign_url(
    stitched_lg_record: str,
    filename_on_bucket: str,
    upload_bucket_name: str,
    s3_service: S3Service,
):
    lifecycle_policy_tag = os.environ.get(
        "STITCHED_FILE_LIFECYCLE_POLICY_TAG", "autodelete"
    )
    extra_args = {
        "Tagging": parse.urlencode({lifecycle_policy_tag: "true"}),
        "ContentDisposition": "inline",
        "ContentType": "application/pdf",
    }
    s3_service.upload_file_with_extra_args(
        file_name=stitched_lg_record,
        s3_bucket_name=upload_bucket_name,
        file_key=filename_on_bucket,
        extra_args=extra_args,
    )
    presign_url_response = s3_service.create_download_presigned_url(
        s3_bucket_name=upload_bucket_name, file_key=filename_on_bucket
    )
    return presign_url_response
