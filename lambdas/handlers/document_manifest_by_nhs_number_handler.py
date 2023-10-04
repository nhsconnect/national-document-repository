import logging
import os

from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.document import Document
from services.document_manifest_service import DocumentManifestService
from services.dynamo_service import DynamoDBService
from utils.exceptions import (DynamoDbException, InvalidResourceIdException,
                              ManifestDownloadException)
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

        dynamo_service = DynamoDBService()

        logger.info("Retrieving doc store documents")
        ds_documents = query_documents(
            dynamo_service, document_store_table_name, nhs_number
        )

        logger.info("Retrieving lloyd george documents")
        lg_documents = query_documents(
            dynamo_service, lloyd_george_table_name, nhs_number
        )

        documents = lg_documents + ds_documents

        if not documents:
            return ApiGatewayResponse(
                204, "No documents found for given NHS number", "GET"
            ).create_api_gateway_response()

        logger.info("Starting document manifest process")
        document_manifest_service = DocumentManifestService(
            nhs_number=nhs_number,
            documents=documents,
            zip_output_bucket=zip_output_bucket,
            zip_trace_table=zip_trace_table_name,
        )

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
    except ManifestDownloadException as e:
        return ApiGatewayResponse(
            500,
            f"{str(e)}",
            "GET",
        ).create_api_gateway_response()
    except DynamoDbException as e:
        return ApiGatewayResponse(
            500,
            f"An error occurred when searching for available documents: {str(e)}",
            "GET",
        ).create_api_gateway_response()
    except ClientError as e:
        logger.error(str(e))
        response = ApiGatewayResponse(
            500, "An error occurred when creating document manifest", "POST"
        ).create_api_gateway_response()
        return response


def query_documents(
    dynamo_service: DynamoDBService, document_table: str, nhs_number: str
) -> list[Document]:
    documents = []

    response = dynamo_service.query_service(
        document_table,
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
