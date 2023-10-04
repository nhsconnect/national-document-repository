import json
import logging
import os
import sys
import uuid
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.supported_document_types import SupportedDocumentTypes
from models.nhs_document_reference import (NHSDocumentReference,
                                           UploadRequestDocument)
from pydantic import ValidationError
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.utilities import validate_id

sys.path.append(os.path.join(os.path.dirname(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Starting document reference creation process")

    try:
        lg_s3_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
        lg_dynamo_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        arf_s3_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
        arf_dynamo_table = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]
    except KeyError as e:
        return ApiGatewayResponse(
            500,
            f"An error occurred due to missing environment variables: {str(e)}",
            "POST",
        ).create_api_gateway_response()

    try:
        body = json.loads(event["body"])
        nhs_number = body["subject"]["identifier"]["value"]

        validate_id(nhs_number)

        if not body:
            return ApiGatewayResponse(
                400, "Provided an empty request body", "POST"
            ).create_api_gateway_response()

        upload_request_documents: list[UploadRequestDocument] = [
            UploadRequestDocument.model_validate(doc)
            for doc in body["content"][0]["attachment"]
        ]

        logger.info("Processed upload documents from request")
    except KeyError as e:
        logger.error(e)
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "GET"
        ).create_api_gateway_response()
    except ValidationError as e:
        logger.error(e)
        return ApiGatewayResponse(
            400, f"Failed to parse document upload request data: {str(e)}", "GET"
        ).create_api_gateway_response()
    except JSONDecodeError as e:
        logger.error(e)
        return ApiGatewayResponse(
            400, f"Invalid json in body: {str(e)}", "GET"
        ).create_api_gateway_response()
    except InvalidResourceIdException as e:
        logger.error(e)
        return ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()

    s3_service = S3Service()

    arf_documents: list[NHSDocumentReference] = []
    lg_documents: list[NHSDocumentReference] = []
    url_responses = {}

    for document in upload_request_documents:
        document_type = SupportedDocumentTypes.get_from_field_name(document.docType)
        if document_type is None:
            return ApiGatewayResponse(
                400, "An error occurred processing the required document type", "POST"
            ).create_api_gateway_response()

        logger.info("Provided document is supported")

        s3_object_key = str(uuid.uuid4())

        document_reference: NHSDocumentReference

        if document_type == SupportedDocumentTypes.LG:
            document_reference = NHSDocumentReference(
                nhs_number=nhs_number,
                s3_bucket_name=lg_s3_bucket_name,
                reference_id=s3_object_key,
                content_type=document.contentType,
                file_name=document.fileName,
            )
            lg_documents.append(document_reference)
        elif document_type == SupportedDocumentTypes.ARF:
            document_reference = NHSDocumentReference(
                nhs_number=nhs_number,
                s3_bucket_name=arf_s3_bucket_name,
                reference_id=s3_object_key,
                content_type=document.contentType,
                file_name=document.fileName,
            )
            arf_documents.append(document_reference)
        else:
            response = ApiGatewayResponse(
                400, "Provided invalid document type", "POST"
            ).create_api_gateway_response()
            return response

        try:
            s3_response = s3_service.create_document_presigned_url_handler(
                document_reference.s3_bucket_name,
                document_reference.nhs_number + "/" + document_reference.id,
            )
            url_responses[document_reference.file_name] = s3_response

        except ClientError as e:
            logger.error(str(e))
            response = ApiGatewayResponse(
                500,
                "An error occurred when creating pre-signed url for document reference",
                "POST",
            ).create_api_gateway_response()
            return response

    try:
        dynamo_service = DynamoDBService()
        if arf_documents:
            logger.info("Writing ARF document references")
            # TODO - Replace with dynamo batch writing
            for document in arf_documents:
                dynamo_service.post_item_service(arf_dynamo_table, document.to_dict())
        if lg_documents:
            logger.info("Writing LG document references")
            # TODO - Replace with dynamo batch writing
            for document in lg_documents:
                dynamo_service.post_item_service(lg_dynamo_table, document.to_dict())
    except ClientError as e:
        logger.error(str(e))
        response = ApiGatewayResponse(
            500, "An error occurred when creating document reference", "POST"
        ).create_api_gateway_response()
        return response

    return ApiGatewayResponse(
        200, json.dumps(url_responses), "POST"
    ).create_api_gateway_response()
