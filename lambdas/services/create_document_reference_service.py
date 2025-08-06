import os
from typing import Optional

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.snomed_codes import SnomedCodes
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference, UploadRequestDocument
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.base.ssm_service import SSMService
from services.document_deletion_service import DocumentDeletionService
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import NotDeleted, UploadIncomplete
from utils.constants.ssm import UPLOAD_PILOT_ODS_ALLOWED_LIST
from utils.exceptions import InvalidNhsNumberException, PdsTooManyRequestsException, PatientNotFoundException
from utils.lambda_exceptions import CreateDocumentRefException
from utils.lloyd_george_validator import (
    getting_patient_info_from_pds,
    validate_lg_files,
)
from utils.utilities import create_reference_id, validate_nhs_number
from utils.exceptions import LGInvalidFilesException

FAILED_CREATE_REFERENCE_MESSAGE = "Create document reference failed"
PROVIDED_DOCUMENT_SUPPORTED_MESSAGE = "Provided document is supported"
UPLOAD_REFERENCE_SUCCESS_MESSAGE = "Upload reference creation was successful"
UPLOAD_REFERENCE_FAILED_MESSAGE = "Upload reference creation was unsuccessful"
PRESIGNED_URL_ERROR_MESSAGE = (
    "An error occurred when creating pre-signed url for document reference"
)

logger = LoggingService(__name__)


class CreateDocumentReferenceService:
    def __init__(self):
        create_document_aws_role_arn = os.getenv("PRESIGNED_ASSUME_ROLE")
        self.s3_service = S3Service(custom_aws_role=create_document_aws_role_arn)
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()
        self.document_deletion_service = DocumentDeletionService()
        self.ssm_service = SSMService()

        self.lg_dynamo_table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.arf_dynamo_table = os.getenv("DOCUMENT_STORE_DYNAMODB_NAME")
        self.staging_bucket_name = os.getenv("STAGING_STORE_BUCKET_NAME")
        self.upload_sub_folder = "user_upload"

    def create_document_reference_request(
        self, nhs_number: str, documents_list: list[dict]
    ):
        arf_documents: list[DocumentReference] = []
        arf_documents_dict_format: list = []
        lg_documents: list[DocumentReference] = []
        lg_documents_dict_format: list = []
        url_responses = {}
        upload_request_documents = self.parse_documents_list(documents_list)

        has_lg_document = any(
            document.docType == SupportedDocumentTypes.LG
            for document in upload_request_documents
        )

        try:
            snomed_code_type = None
            current_gp_ods = ""
            if has_lg_document:
                pds_patient_details = getting_patient_info_from_pds(nhs_number)
                current_gp_ods = (
                    pds_patient_details.get_ods_code_or_inactive_status_for_gp()
                )
                ods_allowed = self.check_if_ods_code_is_in_pilot(current_gp_ods)
                if not ods_allowed:
                    raise CreateDocumentRefException(404, LambdaError.CreateDocRefOdsCodeNotAllowed)
                snomed_code_type = SnomedCodes.LLOYD_GEORGE.value.code

            for validated_doc in upload_request_documents:
                document_reference = self.create_document_reference(
                    nhs_number, current_gp_ods, validated_doc, snomed_code_type
                )

                match document_reference.doc_type:
                    case SupportedDocumentTypes.ARF:
                        arf_documents.append(document_reference)
                        arf_documents_dict_format.append(
                            document_reference.model_dump(
                                by_alias=True, exclude_none=True
                            )
                        )
                    case SupportedDocumentTypes.LG:
                        lg_documents.append(document_reference)
                        lg_documents_dict_format.append(
                            document_reference.model_dump(
                                by_alias=True, exclude_none=True
                            )
                        )
                    case _:
                        logger.error(
                            f"{LambdaError.CreateDocInvalidType.to_str()}",
                            {"Result": UPLOAD_REFERENCE_FAILED_MESSAGE},
                        )
                        raise CreateDocumentRefException(
                            400, LambdaError.CreateDocInvalidType
                        )

                url_responses[validated_doc.clientId] = self.prepare_pre_signed_url(
                    document_reference
                )

            if lg_documents:
                validate_lg_files(lg_documents)
                self.check_existing_lloyd_george_records_and_remove_failed_upload(
                    nhs_number
                )

                self.create_reference_in_dynamodb(
                    self.lg_dynamo_table, lg_documents_dict_format
                )

            if arf_documents:
                self.check_existing_arf_record_and_remove_failed_upload(nhs_number)

                self.create_reference_in_dynamodb(
                    self.arf_dynamo_table, arf_documents_dict_format
                )

            return url_responses

        except (
            PatientNotFoundException
        ) as e: 
            raise CreateDocumentRefException(404, LambdaError.SearchPatientNoPDS)
        
        except (
            InvalidNhsNumberException,
            LGInvalidFilesException,
            PdsTooManyRequestsException,
        ) as e:
            logger.error(
                f"{LambdaError.CreateDocFiles.to_str()} :{str(e)}",
                {"Result": FAILED_CREATE_REFERENCE_MESSAGE},
            )
            raise CreateDocumentRefException(400, LambdaError.CreateDocFiles)

    def check_if_ods_code_is_in_pilot(self, ods_code) -> bool:
        pilot_ods_codes = self.get_allowed_list_of_ods_codes_for_upload_pilot()
        return ods_code in pilot_ods_codes

    def check_existing_arf_record_and_remove_failed_upload(self, nhs_number):
        incomplete_arf_upload_records = self.fetch_incomplete_arf_upload_records(
            nhs_number
        )
        self.stop_if_upload_is_in_process(incomplete_arf_upload_records)
        self.remove_records_of_failed_upload(
            self.arf_dynamo_table, incomplete_arf_upload_records
        )

    def parse_documents_list(
        self, document_list: list[dict]
    ) -> list[UploadRequestDocument]:
        upload_request_document_list = []
        for document in document_list:
            try:
                validated_doc: UploadRequestDocument = (
                    UploadRequestDocument.model_validate(document)
                )
                upload_request_document_list.append(validated_doc)
            except ValidationError as e:
                logger.error(
                    f"{LambdaError.CreateDocNoParse.to_str()} :{str(e)}",
                    {"Result": FAILED_CREATE_REFERENCE_MESSAGE},
                )
                raise CreateDocumentRefException(400, LambdaError.CreateDocNoParse)

        return upload_request_document_list

    def create_document_reference(
        self,
        nhs_number: str,
        current_gp_ods: str,
        validated_doc: UploadRequestDocument,
        snomed_code_type: Optional[str] = None,
    ) -> DocumentReference:

        s3_bucket_name = self.staging_bucket_name
        sub_folder = self.upload_sub_folder

        logger.info(PROVIDED_DOCUMENT_SUPPORTED_MESSAGE)

        s3_object_key = create_reference_id()

        document_reference = DocumentReference(
            id=s3_object_key,
            nhs_number=nhs_number,
            author=current_gp_ods,
            current_gp_ods=current_gp_ods,
            custodian=current_gp_ods,
            content_type=validated_doc.contentType,
            file_name=validated_doc.fileName,
            doc_type=validated_doc.docType,
            document_snomed_code_type=snomed_code_type,
            s3_bucket_name=s3_bucket_name,
            sub_folder=sub_folder,
            uploading=True,
            doc_status="preliminary",
        )
        return document_reference

    def prepare_pre_signed_url(self, document_reference: DocumentReference):
        try:
            s3_response = self.s3_service.create_upload_presigned_url(
                document_reference.s3_bucket_name, document_reference.s3_file_key
            )

            return s3_response

        except ClientError as e:
            logger.error(
                f"{LambdaError.CreateDocPresign.to_str()}: {str(e)}",
                {"Result": PRESIGNED_URL_ERROR_MESSAGE},
            )
            raise CreateDocumentRefException(500, LambdaError.CreateDocPresign)

    def create_reference_in_dynamodb(self, dynamo_table, document_list):
        try:
            self.dynamo_service.batch_writing(dynamo_table, document_list)
            logger.info(
                f"Writing document references to {dynamo_table}",
                {"Result": UPLOAD_REFERENCE_SUCCESS_MESSAGE},
            )

        except ClientError as e:
            logger.error(
                f"{LambdaError.CreateDocUploadInternalError.to_str()}: {str(e)}",
                {"Result": UPLOAD_REFERENCE_FAILED_MESSAGE},
            )
            raise CreateDocumentRefException(
                500, LambdaError.CreateDocUploadInternalError
            )

    def check_existing_lloyd_george_records_and_remove_failed_upload(
        self,
        nhs_number: str,
    ) -> None:
        logger.info("Looking for previous records for this patient...")

        previous_records = (
            self.document_service.fetch_available_document_references_by_type(
                nhs_number=nhs_number,
                doc_type=SupportedDocumentTypes.LG,
                query_filter=NotDeleted,
            )
        )
        if not previous_records:
            logger.info(
                "No record was found for this patient. Will continue to create doc ref."
            )
            return

        self.stop_if_all_records_uploaded(previous_records)
        self.stop_if_upload_is_in_process(previous_records)
        self.remove_records_of_failed_upload(self.lg_dynamo_table, previous_records)

    def stop_if_upload_is_in_process(self, previous_records: list[DocumentReference]):
        if any(
            self.document_service.is_upload_in_process(document)
            for document in previous_records
        ):
            logger.error(
                "Records are in the process of being uploaded. Will not process the new upload.",
                {"Result": UPLOAD_REFERENCE_FAILED_MESSAGE},
            )
            raise CreateDocumentRefException(423, LambdaError.UploadInProgressError)

    def stop_if_all_records_uploaded(self, previous_records: list[DocumentReference]):
        all_records_uploaded = all(record.uploaded for record in previous_records)
        if all_records_uploaded:
            logger.info(
                "The patient already has a full set of record. "
                "We should not be processing the new Lloyd George record upload."
            )
            logger.error(
                f"{LambdaError.CreateDocRecordAlreadyInPlace.to_str()}",
                {"Result": UPLOAD_REFERENCE_FAILED_MESSAGE},
            )
            raise CreateDocumentRefException(
                422, LambdaError.CreateDocRecordAlreadyInPlace
            )

    def remove_records_of_failed_upload(
        self,
        table_name: str,
        failed_upload_records: list[DocumentReference],
    ):
        logger.info(
            "Found previous records of failed upload. "
            "Will delete those records before creating new document references."
        )

        logger.info("Deleting files from s3...")
        for record in failed_upload_records:
            s3_bucket_name = record.s3_bucket_name
            file_key = record.s3_file_key
            self.s3_service.delete_object(s3_bucket_name, file_key)

        logger.info("Deleting dynamodb record...")
        self.document_service.hard_delete_metadata_records(
            table_name=table_name, document_references=failed_upload_records
        )

        logger.info("Previous failed records are deleted.")

    def fetch_incomplete_arf_upload_records(
        self, nhs_number
    ) -> list[DocumentReference]:
        return self.document_service.fetch_available_document_references_by_type(
            nhs_number=nhs_number,
            doc_type=SupportedDocumentTypes.ARF,
            query_filter=UploadIncomplete,
        )
    
    def get_allowed_list_of_ods_codes_for_upload_pilot(self) -> list[str]:
        logger.info("Starting ssm request to retrieve allowed list of ODS codes for Upload Pilot")
        response = self.ssm_service.get_ssm_parameter(UPLOAD_PILOT_ODS_ALLOWED_LIST)
        if not response:
            logger.warning("No ODS codes found in allowed list for Upload Pilot")
        return response
