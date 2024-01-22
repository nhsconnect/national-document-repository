import os

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.supported_document_types import SupportedDocumentTypes
from models.nhs_document_reference import NHSDocumentReference, UploadRequestDocument
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_exceptions import CreateDocumentRefException
from utils.lloyd_george_validator import LGInvalidFilesException, validate_lg_files
from utils.utilities import create_reference_id, validate_id

logger = LoggingService(__name__)


class CreateDocumentReferenceService:
    def __init__(self, nhs_number):
        self.nhs_number = nhs_number
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()

        self.lg_s3_bucket_name = os.getenv("LLOYD_GEORGE_BUCKET_NAME")
        self.lg_dynamo_table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.arf_s3_bucket_name = os.getenv("DOCUMENT_STORE_BUCKET_NAME")
        self.arf_dynamo_table = os.getenv("DOCUMENT_STORE_DYNAMODB_NAME")

        self.arf_documents: list[NHSDocumentReference] = []
        self.arf_documents_dict_format: list = []
        self.lg_documents: list[NHSDocumentReference] = []
        self.lg_documents_dict_format: list = []
        self.url_responses = {}

    def create_document_reference_request(self, documents_list: list[dict]):
        try:
            validate_id(self.nhs_number)
            for document in documents_list:
                document_reference = self.prepare_doc_object(document)
                self.prepare_pre_signed_url(document_reference)
            if self.lg_documents:
                validate_lg_files(self.lg_documents)
                self.create_reference_in_dynamodb(
                    self.lg_dynamo_table, self.lg_documents_dict_format
                )
            if self.arf_documents:
                self.create_reference_in_dynamodb(
                    self.arf_dynamo_table, self.arf_documents_dict_format
                )

        except (InvalidResourceIdException, LGInvalidFilesException) as e:
            logger.error(
                f"{LambdaError.CreateDocFiles.to_str()} :{str(e)}",
                {"Result": "Create document reference failed"},
            )
            raise CreateDocumentRefException(400, LambdaError.CreateDocFiles)

    def prepare_doc_object(self, document: dict) -> NHSDocumentReference:
        try:
            validated_doc: UploadRequestDocument = UploadRequestDocument.model_validate(
                document
            )
        except ValidationError as e:
            logger.error(
                f"{LambdaError.CreateDocNoParse.to_str()} :{str(e)}",
                {"Result": "Create document reference failed"},
            )
            raise CreateDocumentRefException(400, LambdaError.CreateDocNoParse)

        document_type = SupportedDocumentTypes.get_from_field_name(
            validated_doc.docType
        )
        if document_type is None:
            logger.error(
                f"{LambdaError.CreateDocNoType.to_str()}",
                {"Result": "Create document reference failed"},
            )
            raise CreateDocumentRefException(400, LambdaError.CreateDocNoType)

        logger.info("Provided document is supported")

        (
            s3_destination,
            documents_type_list,
            documents_list_dict_format,
        ) = self.return_info_by_doc_type(document_type)

        s3_object_key = create_reference_id()
        document_reference = NHSDocumentReference(
            nhs_number=self.nhs_number,
            s3_bucket_name=s3_destination,
            reference_id=s3_object_key,
            content_type=validated_doc.contentType,
            file_name=validated_doc.fileName,
        )

        documents_type_list.append(document_reference)
        documents_list_dict_format.append(document_reference.to_dict())
        return document_reference

    def prepare_pre_signed_url(self, document_reference: NHSDocumentReference):
        try:
            s3_response = self.s3_service.create_upload_presigned_url(
                document_reference.s3_bucket_name,
                document_reference.nhs_number + "/" + document_reference.id,
            )
            self.url_responses[document_reference.file_name] = s3_response

        except ClientError as e:
            logger.error(
                f"{LambdaError.CreateDocPresign.to_str()}: {str(e)}",
                {
                    "Result": "An error occurred when creating pre-signed url for document reference"
                },
            )
            raise CreateDocumentRefException(500, LambdaError.CreateDocPresign)

    def create_reference_in_dynamodb(self, dynamo_table, document_list):
        try:
            self.dynamo_service.batch_writing(dynamo_table, document_list)
            logger.info(
                f"Writing document references to {dynamo_table}",
                {"Result": "Upload reference was created successfully"},
            )

        except ClientError as e:
            logger.error(
                f"{LambdaError.CreateDocUpload.to_str()}: {str(e)}",
                {"Result": "Upload reference creation was unsuccessful"},
            )
            raise CreateDocumentRefException(500, LambdaError.CreateDocUpload)

    def return_info_by_doc_type(self, doc_type):
        if doc_type == SupportedDocumentTypes.LG.value:
            return (
                self.lg_s3_bucket_name,
                self.lg_documents,
                self.lg_documents_dict_format,
            )
        elif doc_type == SupportedDocumentTypes.ARF.value:
            return (
                self.arf_s3_bucket_name,
                self.arf_documents,
                self.arf_documents_dict_format,
            )
        else:
            logger.error(
                f"{LambdaError.CreateDocInvalidType.to_str()}",
                {"Result": "Upload reference creation was unsuccessful"},
            )
            raise CreateDocumentRefException(400, LambdaError.CreateDocInvalidType)
