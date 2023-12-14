import json
import os
import tempfile
from urllib import parse
from urllib.parse import urlparse

from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from enums.metadata_field_names import DocumentReferenceMetadataFields
from pypdf.errors import PyPdfError
from services.dynamo_service import DynamoDBService
from services.lloyd_george_stitch_service import LloydGeorgeStitchService
from services.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.handle_lambda_exceptions import handle_lambda_exceptions
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.validate_patient_id import (
    extract_nhs_number_from_event,
    validate_patient_id,
)
from utils.exceptions import DynamoDbException
from utils.lambda_response import ApiGatewayResponse
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@validate_patient_id
@override_error_check
@handle_lambda_exceptions
@ensure_environment_variables(
    names=["LLOYD_GEORGE_DYNAMODB_NAME", "LLOYD_GEORGE_BUCKET_NAME"]
)
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.VIEW_LG_RECORD.value
    nhs_number = extract_nhs_number_from_event(event)
    request_context.patient_nhs_no = nhs_number
    os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
    os.environ["LLOYD_GEORGE_BUCKET_NAME"]

    stitch_service = LloydGeorgeStitchService()

    try:
        # response = get_lloyd_george_records_for_patient(
        #     lloyd_george_table_name, nhs_number
        # )
        lg_records = stitch_service.get_lloyd_george_record_for_patient(nhs_number)
        if len(lg_records) == 0:
            return ApiGatewayResponse(
                404, f"Lloyd george record not found for patient {nhs_number}", "GET"
            ).create_api_gateway_response()

        # ordered_lg_records = order_response_by_filenames(response["Items"])
        ordered_lg_records = stitch_service.sort_documents_by_filenames(lg_records)
        all_lg_parts = stitch_service.download_lloyd_george_files(ordered_lg_records)

        # s3_service = S3Service()
        # all_lg_parts = download_lloyd_george_files(
        #     lloyd_george_bucket_name, ordered_lg_records, s3_service
        # )
    except (ClientError, DynamoDbException) as e:
        logger.error(e, {"Result": f"Unsuccessful viewing LG due to {str(e)}"})
        return ApiGatewayResponse(
            500, f"Unable to retrieve documents for patient {nhs_number}", "GET"
        ).create_api_gateway_response()

    try:
        # filename_for_stitched_file = make_filename_for_stitched_file(response["Items"])
        filename_for_stitched_file = stitch_service.make_filename_for_stitched_file(
            lg_records
        )
        # stitched_lg_record = stitch_pdf(all_lg_parts)
        stitched_lg_record = stitch_service.stitch_pdf(all_lg_parts)

        # number_of_files = len(response["Items"])
        number_of_files = len(all_lg_parts)
        # last_updated = get_most_recent_created_date(response["Items"])
        last_updated = stitch_service.get_most_recent_created_date(lg_records)
        # total_file_size = get_total_file_size(all_lg_parts)
        total_file_size = stitch_service.get_total_file_size(all_lg_parts)
        # presign_url = upload_stitched_lg_record_and_retrieve_presign_url(
        #     stitched_lg_record=stitched_lg_record,
        #     filename_on_bucket=f"{nhs_number}/{filename_for_stitched_file}",
        #     upload_bucket_name=lloyd_george_bucket_name,
        #     s3_service=s3_service,
        # )
        presign_url = stitch_service.upload_stitched_lg_record_and_retrieve_presign_url(
            stitched_lg_record=stitched_lg_record,
            filename_on_bucket=f"{nhs_number}/{filename_for_stitched_file}",
        )
        response = json.dumps(
            {
                "number_of_files": number_of_files,
                "last_updated": last_updated,
                "presign_url": presign_url,
                "total_file_size_in_byte": total_file_size,
            }
        )
        logger.audit_splunk_info(
            "User has viewed Lloyd George records", {"Result": "Successful viewing LG"}
        )
        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()
    except (ClientError, PyPdfError, FileNotFoundError) as e:
        logger.error(e, {"Result": f"Unsuccessful viewing LG due to {str(e)}"})
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
        response = dynamo_service.query_with_requested_fields(
            lloyd_george_table_name,
            "NhsNumberIndex",
            "NhsNumber",
            nhs_number,
            [
                DocumentReferenceMetadataFields.ID.value,
                DocumentReferenceMetadataFields.FILE_LOCATION.value,
                DocumentReferenceMetadataFields.NHS_NUMBER.value,
                DocumentReferenceMetadataFields.FILE_NAME.value,
                DocumentReferenceMetadataFields.CREATED.value,
            ],
            filtered_fields={DocumentReferenceMetadataFields.DELETED.value: ""},
        )
        if response is None or ("Items" not in response):
            logger.error(
                f"Unrecognised response from DynamoDB: {response}",
                {
                    "Result": "Unsuccessful viewing LG due to Unrecognised response from DynamoDB"
                },
            )
            raise DynamoDbException("Unrecognised response from DynamoDB")
        return response
    except ClientError:
        raise DynamoDbException("Unexpected error when getting Lloyd George record")


def download_lloyd_george_files(
    lloyd_george_bucket_name: str, ordered_lg_records: list[dict], s3_service: S3Service
) -> list[str]:
    all_lg_parts = []
    temp_folder = tempfile.mkdtemp()
    for lg_part in ordered_lg_records:
        file_location_on_s3 = lg_part[
            DocumentReferenceMetadataFields.FILE_LOCATION.value
        ]
        original_file_name = lg_part[DocumentReferenceMetadataFields.FILE_NAME.value]  # fmt: skip

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

    filename_key = DocumentReferenceMetadataFields.FILE_NAME.value
    base_filename = dynamo_response[0][filename_key]
    end_of_total_page_numbers = base_filename.index("_")

    return "Combined" + base_filename[end_of_total_page_numbers:]


def get_most_recent_created_date(dynamo_response: list[dict]) -> str:
    created_date_key = DocumentReferenceMetadataFields.CREATED.value
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
