import json
import os
import sys
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from enums.supported_document_types import SupportedDocumentTypes
from models.nhs_document_reference import (NHSDocumentReference,
                                           UploadRequestDocument)
from pydantic import ValidationError
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.lloyd_george_validator import (LGInvalidFilesException,
                                          validate_lg_files)
from utils.request_context import request_context
from utils.utilities import create_reference_id, validate_id

sys.path.append(os.path.join(os.path.dirname(__file__)))

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(
    names=[
        "LLOYD_GEORGE_BUCKET_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "DOCUMENT_STORE_BUCKET_NAME",
        "DOCUMENT_STORE_DYNAMODB_NAME",
    ]
)
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.UPLOAD_RECORD.value

    logger.info("Starting document reference creation process")

    lg_s3_bucket_name = os.environ["LLOYD_GEORGE_BUCKET_NAME"]
    lg_dynamo_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
    arf_s3_bucket_name = os.environ["DOCUMENT_STORE_BUCKET_NAME"]
    arf_dynamo_table = os.environ["DOCUMENT_STORE_DYNAMODB_NAME"]

    try:
        body = json.loads(event["body"])
        nhs_number = body["subject"]["identifier"]["value"]
        request_context.patient_nhs_no = nhs_number
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
        logger.error(e, {"Result": f"Upload Unsuccessful due to {str(e)}"})
        return ApiGatewayResponse(
            400, f"An error occurred due to missing key: {str(e)}", "GET"
        ).create_api_gateway_response()
    except ValidationError as e:
        logger.error(e, {"Result": f"Upload Unsuccessful due to {str(e)}"})
        return ApiGatewayResponse(
            400, "Failed to parse document upload request data", "GET"
        ).create_api_gateway_response()
    except JSONDecodeError as e:
        logger.error(e, {"Result": f"Upload Unsuccessful due to {str(e)}"})
        return ApiGatewayResponse(
            400, f"Invalid json in body: {str(e)}", "GET"
        ).create_api_gateway_response()
    except InvalidResourceIdException as e:
        logger.error(e, {"Result": f"Upload Unsuccessful due to {str(e)}"})
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

        s3_object_key = create_reference_id()

        document_reference: NHSDocumentReference

        if document_type == SupportedDocumentTypes.LG.value:
            document_reference = NHSDocumentReference(
                nhs_number=nhs_number,
                s3_bucket_name=lg_s3_bucket_name,
                reference_id=s3_object_key,
                content_type=document.contentType,
                file_name=document.fileName,
            )
            lg_documents.append(document_reference)
        elif document_type == SupportedDocumentTypes.ARF.value:
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
            logger.error(str(e), {"Result": f"Upload Unsuccessful due to {str(e)}"})
            response = ApiGatewayResponse(
                500,
                "An error occurred when creating pre-signed url for document reference",
                "POST",
            ).create_api_gateway_response()
            return response

    try:
        validate_lg_files(lg_documents)
        dynamo_service = DynamoDBService()
        if arf_documents:
            logger.info(
                "Writing ARF document references",
                {"Result": "Upload reference was created successfully"},
            )
            # TODO - Replace with dynamo batch writing
            for document in arf_documents:
                dynamo_service.create_item(arf_dynamo_table, document.to_dict())
        if lg_documents:
            logger.info(
                "Writing LG document references",
                {"Result": "Upload reference was created successfully"},
            )
            # TODO - Replace with dynamo batch writing
            for document in lg_documents:
                dynamo_service.create_item(lg_dynamo_table, document.to_dict())
    except ClientError as e:
        logger.error(str(e), {"Result": "Upload reference creation was unsuccessful"})
        response = ApiGatewayResponse(
            500, "An error occurred when creating document reference", "POST"
        ).create_api_gateway_response()
        return response
    except LGInvalidFilesException as e:
        logger.error(e, {"Result": "Upload reference creation was unsuccessful"})
        response = ApiGatewayResponse(
            400, "One or more of the files is not valid", "POST"
        ).create_api_gateway_response()
        return response

    return ApiGatewayResponse(
        200, json.dumps(url_responses), "POST"
    ).create_api_gateway_response()
