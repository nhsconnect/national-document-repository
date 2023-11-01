import logging
import os

from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.s3_lifecycle_tags import S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from services.document_service import DocumentService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.validate_document_type import validate_document_type
from utils.decorators.validate_patient_id import validate_patient_id
from utils.lambda_response import ApiGatewayResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@validate_patient_id
@validate_document_type
@ensure_environment_variables(
    names=[
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
    ]
)
def lambda_handler(event, context):
    nhs_number = event["queryStringParameters"]["patientId"]
    doc_type = event["queryStringParameters"]["docType"]

    document_service = DocumentService()

    try:
        table = ""
        if SupportedDocumentTypes.ARF.name == doc_type:
            logger.info("Retrieving ARF documents for deletion")
            table = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]

        if SupportedDocumentTypes.LG.name == doc_type:
            logger.info("Retrieving Lloyd George documents for deletion")
            table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]

        results = document_service.fetch_documents_from_table_with_filter(
            nhs_number, table, {DocumentReferenceMetadataFields.DELETED.value: ""}
        )

        if not results:
            return ApiGatewayResponse(
                404, "No documents available", "DELETE"
            ).create_api_gateway_response()

        document_service.delete_documents(
            table_name=table,
            document_references=results,
            type_of_delete=str(S3LifecycleTags.SOFT_DELETE.value),
        )
    except ClientError as e:
        logger.info(str(e))
        return ApiGatewayResponse(
            500, "Failed to delete documents", "DELETE"
        ).create_api_gateway_response()

    return ApiGatewayResponse(200, "Success", "DELETE").create_api_gateway_response()
