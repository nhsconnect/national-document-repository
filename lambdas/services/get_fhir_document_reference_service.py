import base64
import os

from enums.file_size import FileSize
from enums.lambda_error import LambdaError
from enums.snomed_codes import SnomedCodes
from models.document_reference import DocumentReference
from models.fhir.R4.fhir_document_reference import Attachment, DocumentReferenceInfo
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import GetFhirDocumentReferenceException
from utils.request_context import request_context

logger = LoggingService(__name__)


class GetFhirDocumentReferenceService:
    def __init__(self):
        self.tables = {
            SnomedCodes.LLOYD_GEORGE.value.code: os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        }
        self.ssm_prefix = getattr(request_context, "auth_ssm_prefix", "")
        get_document_presign_url_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.cloudfront_url = os.environ.get("CLOUDFRONT_URL")
        self.s3_service = S3Service(
            custom_aws_role=get_document_presign_url_aws_role_arn
        )
        self.ssm_service = SSMService()
        self.document_service = DocumentService()

    def handle_get_document_reference_request(self, snomed_code, document_id):
        table = self.tables.get(snomed_code, None)
        if not table:
            logger.error("No table found for the given SNOMED code.")
            raise GetFhirDocumentReferenceException(
                404, LambdaError.DocumentReferenceNotFound
            )
        document_reference = self.get_document_references(document_id, table)

        return document_reference

    def get_document_references(self, document_id: str, table) -> DocumentReference:
        documents = self.document_service.fetch_documents_from_table(
            table=table,
            search_condition=document_id,
            search_key="ID",
        )
        if len(documents) > 0:
            logger.info("Document found for given id")
            return documents[0]
        else:
            raise GetFhirDocumentReferenceException(
                404, LambdaError.DocumentReferenceNotFound
            )

    def get_presigned_url(self, bucket_name, file_location):
        """
        generates a presigned URL for downloading a file from S3 and formats it with a CloudFront URL.

        Args:
            bucket_name (str): The name of the S3 bucket where the file is stored.
            file_location (str): The key (path) of the file in the S3 bucket.

        Returns:
            str: A URL for the presigned S3 download link.
        """
        presign_url_response = self.s3_service.create_download_presigned_url(
            s3_bucket_name=bucket_name,
            file_key=file_location,
        )
        return presign_url_response

    def create_document_reference_fhir_response(
        self, document_reference: DocumentReference
    ) -> str:
        """
        Creates a FHIR-compliant DocumentReference response for a given document.

        If the file size is less than 8MB, the binary file is returned in the response.
        Otherwise, a presigned URL is generated and included in the response.

        Args:
            document_reference (DocumentReference): The document reference object containing metadata
                about the file (e.g., bucket name, file key, file size, etc.).

        Returns:
            str: A JSON string representing the FHIR DocumentReference object.
        """
        logger.info("Creating FHIR DocumentReference response for document.")
        bucket_name = document_reference.s3_bucket_name
        file_location = document_reference.s3_file_key
        file_size = self.s3_service.get_file_size(
            s3_bucket_name=bucket_name,
            object_key=file_location,
        )
        if file_size < FileSize.MAX_FILE_SIZE:
            logger.info("File size is smaller than 8MB. Returning binary file.")
            binary_file = self.s3_service.get_binary_file(
                s3_bucket_name=bucket_name,
                file_key=file_location,
            )
            base64_encoded_file = base64.b64encode(binary_file)
            document_details = Attachment(
                data=base64_encoded_file,
                title=document_reference.file_name,
                creation=document_reference.created,
            )

        else:
            logger.info("File size is larger than 8MB. Generating presigned URL.")
            presign_url = self.get_presigned_url(bucket_name, file_location)
            document_details = Attachment(
                url=presign_url,
                title=document_reference.file_name,
                creation=document_reference.created,
            )

        # Create and return the FHIR DocumentReference object as a JSON string.
        fhir_document_reference = (
            DocumentReferenceInfo(
                nhsNumber=document_reference.nhs_number,
                custodian=document_reference.current_gp_ods,
                attachment=document_details,
            )
            .create_minimal_fhir_document_reference_object()
            .model_dump_json(exclude_none=True)
        )
        return fhir_document_reference
