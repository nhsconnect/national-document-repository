import os

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
from utils.utilities import format_cloudfront_url

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
            str: A formatted CloudFront URL for the presigned S3 download link.
        """
        presign_url_response = self.s3_service.create_download_presigned_url(
            s3_bucket_name=bucket_name,
            file_key=file_location,
        )
        return format_cloudfront_url(presign_url_response, self.cloudfront_url)

    def create_document_reference_fhir_response(
        self, document_reference: DocumentReference
    ) -> (str, bool):
        """
        Creates a FHIR-compliant DocumentReference response for a given document.

        If the file size is less than 8MB, the binary file is returned directly.
        Otherwise, a presigned URL is generated and included in the response.

        Args:
            document_reference (DocumentReference): The document reference object containing metadata
                about the file (e.g. bucket name, file key, file size, etc.).

        Returns:
            str: A JSON string representing the FHIR DocumentReference object.
        """
        bucket_name = document_reference.get_file_bucket()
        file_location = document_reference.get_file_key()
        file_size = self.s3_service.get_file_size(
            s3_bucket_name=bucket_name,
            object_key=file_location,
        )
        is_return_file_binary = False
        if file_size < 8 * 10**6:
            is_return_file_binary = True
            # If the file size is less than 8MB, return the binary file as a base64 encoded string.
            return (
                self.s3_service.get_binary_file(
                    s3_bucket_name=bucket_name,
                    file_key=file_location,
                ),
                is_return_file_binary,
            )
        else:
            # Generate a presigned URL for larger files.
            presign_url = self.get_presigned_url(bucket_name, file_location)

            # Create an Attachment object with the presigned URL and document metadata.
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
                .create_fhir_document_reference_object()
                .model_dump_json(exclude_none=True)
            )
            return fhir_document_reference, is_return_file_binary
