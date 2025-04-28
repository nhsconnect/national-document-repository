import json
import os
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from inflection import underscore
from models.document_reference import DocumentReference, SearchDocumentReference
from models.fhir.R4.nrl_fhir_document_reference import Attachment, DocumentReferenceInfo
from pydantic import ValidationError
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import NotDeleted
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentRefSearchException

logger = LoggingService(__name__)


class DocumentReferenceSearchService(DocumentService):
    def get_document_references(self, nhs_number: str, return_fhir: bool = False):
        """
        Fetch document references for a given NHS number.

        :param nhs_number: The NHS number to search for.
        :param return_fhir: If True, return FHIR DocumentReference objects.
        :return: List of document references or FHIR DocumentReferences.
        """
        try:
            list_of_table_names = self._get_table_names()
            results = self._search_tables_for_documents(
                nhs_number, list_of_table_names, return_fhir
            )
            return results
        except (
            JSONDecodeError,
            ValidationError,
            ClientError,
            DynamoServiceException,
        ) as e:
            logger.error(
                f"{LambdaError.DocRefClient.to_str()}: {str(e)}",
                {"Result": "Document reference search failed"},
            )
            raise DocumentRefSearchException(500, LambdaError.DocRefClient)

    def _get_table_names(self) -> list[str]:
        try:
            return json.loads(os.environ["DYNAMODB_TABLE_LIST"])
        except JSONDecodeError as e:
            logger.error(f"Failed to decode table list: {str(e)}")
            raise

    def _search_tables_for_documents(
        self, nhs_number: str, table_names: list[str], return_fhir: bool
    ):
        results = []
        for table_name in table_names:
            logger.info(f"Searching for results in {table_name}")
            documents = self._fetch_documents(nhs_number, table_name, NotDeleted)
            self._validate_upload_status(documents)
            results.extend(self._process_documents(documents, return_fhir))
        return results

    def _fetch_documents(self, nhs_number: str, table_name: str, filter_expression):
        return self.fetch_documents_from_table_with_nhs_number(
            nhs_number, table_name, query_filter=filter_expression
        )

    def _validate_upload_status(self, documents: list[DocumentReference]):
        if self.is_upload_in_process(documents):
            logger.error(
                "Records are in the process of being uploaded. Will not process the new upload.",
                {"Result": "Document reference search failed"},
            )
            raise DocumentRefSearchException(423, LambdaError.UploadInProgressError)

    def _process_documents(
        self, documents: list[DocumentReference], return_fhir: bool
    ) -> list[dict]:
        results = []
        for document in documents:
            if return_fhir:
                fhir_response = self.create_document_reference_fhir_response(document)
                results.append(fhir_response)
            else:
                document_model = self._build_document_model(document)
                search_result = SearchDocumentReference(**document_model)
                results.append(search_result.model_dump(by_alias=True))
        return results

    def _build_document_model(self, document: DocumentReference) -> dict:
        base_model = document.model_dump(
            include={
                underscore(DocumentReferenceMetadataFields.ID.value),
                underscore(DocumentReferenceMetadataFields.FILE_NAME.value),
                underscore(DocumentReferenceMetadataFields.CREATED.value),
                underscore(DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT.value),
            }
        )
        base_model.update(
            {
                "file_size": self.s3_service.get_file_size(
                    s3_bucket_name=document.get_file_bucket(),
                    object_key=document.get_file_key(),
                )
            }
        )
        return base_model

    def create_document_reference_fhir_response(
        self,
        document_reference: DocumentReference,
    ) -> dict:
        document_details = Attachment(
            title=document_reference.file_name,
            creation=document_reference.created,
        )
        fhir_document_reference = (
            DocumentReferenceInfo(
                nhsNumber=document_reference.nhs_number,
                attachment=document_details,
            )
            .create_minimal_fhir_document_reference_object()
            .model_dump(exclude_none=True)
        )
        return fhir_document_reference
