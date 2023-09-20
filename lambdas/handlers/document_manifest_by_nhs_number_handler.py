import logging
import os

from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.document import Document
from services.document_manifest_service import DocumentManifestService
from services.dynamo_service import DynamoDBService
from utils.exceptions import DynamoDbException, InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import validate_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting document manifest process")

    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)

        document_store_table_name = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
        lloyd_george_table_name = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        zip_trace_table_name = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]
        # zip_trace_ttl = os.environ["DOCUMENT_ZIP_TRACE_TTL_IN_DAYS"]

        logger.info("Retrieving doc store george documents")
        ds_documents = get_doc_store_documents(document_store_table_name, nhs_number)

        logger.info("Retrieving lloyd george documents")
        lg_documents = get_lloyd_george_documents(lloyd_george_table_name, nhs_number)

        if not lg_documents or not ds_documents:
            return ApiGatewayResponse(
                204, "No documents found for given NHS number", "GET"
            ).create_api_gateway_response()

        documents = lg_documents + ds_documents

        document_manifest_service = DocumentManifestService(
            nhs_number=nhs_number,
            documents=documents,
            zip_output_bucket=zip_output_bucket,
            zip_trace_table=zip_trace_table_name,
        )

        logger.info("Starting document manifest process")

        response = document_manifest_service.create_document_manifest_presigned_url()

        return ApiGatewayResponse(200, response, "GET").create_api_gateway_response()

    except InvalidResourceIdException:
        return ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
    except KeyError as e:
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "GET"
        ).create_api_gateway_response()
    except DynamoDbException as e:
        return ApiGatewayResponse(
            500,
            f"An error occurred when searching for available documents: {str(e)}",
            "GET",
        ).create_api_gateway_response()


def get_lloyd_george_documents(
    lloyd_george_table: str, nhs_number: str
) -> list[Document]:
    lg_dynamo_service = DynamoDBService(lloyd_george_table)
    return query_documents(lg_dynamo_service, nhs_number)


def get_doc_store_documents(doc_store_table: str, nhs_number: str) -> list[Document]:
    ds_dynamo_service = DynamoDBService(doc_store_table)
    return query_documents(ds_dynamo_service, nhs_number)


def query_documents(dynamo_service: DynamoDBService, nhs_number: str) -> list[Document]:
    documents = []

    response = dynamo_service.query_service(
        "NhsNumberIndex",
        "NhsNumber",
        nhs_number,
        [
            DocumentReferenceMetadataFields.FILE_NAME,
            DocumentReferenceMetadataFields.FILE_LOCATION,
            DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT,
        ],
    )
    if response is None or ("Items" not in response):
        logger.error(f"Unrecognised response from DynamoDB: {response}")
        raise DynamoDbException("Unrecognised response from DynamoDB")

    logger.info("Creating documents from response")
    for item in response["Items"]:
        document = Document(
            nhs_number=nhs_number,
            file_name=item[DocumentReferenceMetadataFields.FILE_NAME.field_name],
            virus_scanner_result=item[
                DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT.field_name
            ],
            file_location=item[
                DocumentReferenceMetadataFields.FILE_LOCATION.field_name
            ],
        )
        documents.append(document)

    return documents
