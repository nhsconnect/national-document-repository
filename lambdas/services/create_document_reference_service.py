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
from utils.utilities import create_reference_id, validate_nhs_number, validate_nhs_number

logger = LoggingService(__name__)


class CreateDocumentReferenceService:
    def __init__(self):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()

        self.lg_dynamo_table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.arf_dynamo_table = os.getenv("DOCUMENT_STORE_DYNAMODB_NAME")
        self.staging_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")


    def create_document_reference_request(self, nhs_number: int, documents_list: list[dict]):

        arf_documents: list[NHSDocumentReference] = []
        arf_documents_dict_format: list = []
        lg_documents: list[NHSDocumentReference] = []
        lg_documents_dict_format: list = []
        url_responses = {}
    
        try:
            validate_nhs_number(nhs_number)
            for document in documents_list:
                (document_reference, doc_type) = self.prepare_doc_object(nhs_number, document)
                self.check_valid_doc_type(doc_type)
                
                if doc_type.value == SupportedDocumentTypes.ARF.value:
                    arf_documents.append(document_reference)
                    arf_documents_dict_format.append(document_reference.to_dict())
                
                if doc_type.value == SupportedDocumentTypes.LG.value:
                    lg_documents.append(document_reference)
                    lg_documents_dict_format.append(document_reference.to_dict())

                url_responses[document_reference.file_name] = self.prepare_pre_signed_url(document_reference)

            if lg_documents:
                validate_lg_files(lg_documents)
                self.create_reference_in_dynamodb(
                    self.lg_dynamo_table, lg_documents_dict_format
                )
                
            if arf_documents:
                self.create_reference_in_dynamodb(
                    self.arf_dynamo_table, arf_documents_dict_format
                )

        except (InvalidResourceIdException, LGInvalidFilesException) as e:
            logger.error(
                f"{LambdaError.CreateDocFiles.to_str()} :{str(e)}",
                {"Result": "Create document reference failed"},
            )
            raise CreateDocumentRefException(400, LambdaError.CreateDocFiles)

    def prepare_doc_object(self, nhs_number:str, document: dict) -> NHSDocumentReference:
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

        s3_object_key = create_reference_id()

        document_reference = NHSDocumentReference(
            nhs_number=nhs_number,
            s3_bucket_name=self.staging_bucket_name,
            reference_id=s3_object_key,
            content_type=validated_doc.contentType,
            file_name=validated_doc.fileName,
        )

        return document_reference, document_type

    def prepare_pre_signed_url(self, document_reference: NHSDocumentReference):
        try:
            s3_response = self.s3_service.create_upload_presigned_url(
                document_reference.s3_bucket_name,
                document_reference.nhs_number + "/" + document_reference.id,
            )

            return s3_response

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

    def check_valid_doc_type(self, doc_type):
        if (doc_type.value == SupportedDocumentTypes.LG.value or
            doc_type.value == SupportedDocumentTypes.ARF.value):
            return;

        logger.error(
                f"{LambdaError.CreateDocInvalidType.to_str()}",
                {"Result": "Upload reference creation was unsuccessful"},
            )
        raise CreateDocumentRefException(400, LambdaError.CreateDocInvalidType)


