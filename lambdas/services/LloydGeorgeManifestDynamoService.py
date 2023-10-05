
import logging
import os

from services.dynamo_service import DynamoDBService
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.document import Document
from utils.exceptions import DynamoDbException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class LloydGeorgeManifestDynamoService(DynamoDBService):

    def query_lloyd_george_documents(
        nhs_number: str
    ) -> list[Document]:
        documents = []

        document_table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]
        response = self.query_service(
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