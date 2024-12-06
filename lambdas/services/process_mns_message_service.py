import os
from datetime import datetime

from botocore.exceptions import ClientError
from enums.death_notification_status import DeathNotificationStatus
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.mns_notification_types import MNSNotificationTypes
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from models.mns_sqs_message import MNSSQSMessage
from services.base.dynamo_service import DynamoDBService
from services.base.sqs_service import SQSService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import PdsErrorException
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class MNSNotificationService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.pds_service = get_pds_service()
        self.sqs_service = SQSService()
        self.queue = os.getenv("MNS_NOTIFICATION_QUEUE_URL")

    def handle_mns_notification(self, message: MNSSQSMessage):
        try:
            match message.type:
                case MNSNotificationTypes.CHANGE_OF_GP:
                    logger.info("Handling GP change notification.")
                    self.handle_gp_change_notification(message)
                case MNSNotificationTypes.DEATH_NOTIFICATION:
                    logger.info("Handling death status notification.")
                    self.handle_death_notification(message)

        except PdsErrorException:
            logger.info("An error occurred when calling PDS")
            self.send_message_back_to_queue(message)

        except ClientError as e:
            logger.info(
                f"Unable to process message: {message.id}, of type: {message.type}"
            )
            logger.info(f"{e}")

    def handle_gp_change_notification(self, message: MNSSQSMessage):
        patient_document_references = self.get_patient_documents(
            message.subject.nhs_number
        )

        if not self.patient_is_present_in_ndr(patient_document_references):
            return

        updated_ods_code = self.get_updated_gp_ods(message.subject.nhs_number)

        for reference in patient_document_references:
            if reference["CurrentGpOds"] is not updated_ods_code:
                self.dynamo_service.update_item(
                    table_name=self.table,
                    key=reference["ID"],
                    updated_fields={
                        DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: updated_ods_code,
                        DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                            datetime.now().timestamp()
                        ),
                    },
                )

        logger.info("Update complete for change of GP")

    def handle_death_notification(self, message: MNSSQSMessage):
        death_notification_type = message.data["deathNotificationStatus"]
        match death_notification_type:
            case DeathNotificationStatus.INFORMAL:
                logger.info(
                    "Patient is deceased - INFORMAL, moving on to the next message."
                )
                return

            case DeathNotificationStatus.REMOVED:
                patient_documents = self.get_patient_documents(
                    message.subject.nhs_number
                )
                if not self.patient_is_present_in_ndr(patient_documents):
                    return

                updated_ods_code = self.get_updated_gp_ods(message.subject.nhs_number)
                self.update_patient_ods_code(patient_documents, updated_ods_code)
                logger.info("Update complete for death notification change.")

            case DeathNotificationStatus.FORMAL:
                patient_documents = self.get_patient_documents(
                    message.subject.nhs_number
                )
                if not self.patient_is_present_in_ndr(patient_documents):
                    return

                self.update_patient_ods_code(
                    patient_documents, PatientOdsInactiveStatus.DECEASED
                )
                logger.info(
                    f"Update complete, patient marked {PatientOdsInactiveStatus.DECEASED}."
                )

    def get_patient_documents(self, nhs_number: str):
        logger.info("Getting patient document references...")
        response = self.dynamo_service.query_table_by_index(
            table_name=self.table,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=nhs_number,
        )
        return response["Items"]

    def update_patient_ods_code(self, patient_documents: list[dict], code: str) -> None:
        for document in patient_documents:
            logger.info("Updating patient document reference...")
            self.dynamo_service.update_item(
                table_name=self.table,
                key=document["ID"],
                updated_fields={
                    DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: code,
                    DocumentReferenceMetadataFields.LAST_UPDATED.value: int(
                        datetime.now().timestamp()
                    ),
                },
            )

    def get_updated_gp_ods(self, nhs_number: str) -> str:
        patient_details = self.pds_service.fetch_patient_details(nhs_number)
        return patient_details.general_practice_ods

    def send_message_back_to_queue(self, message: MNSSQSMessage):
        logger.info("Sending message back to queue...")
        self.sqs_service.send_message_standard(
            queue_url=self.queue, message_body=message.model_dump_json(by_alias=True)
        )

    def patient_is_present_in_ndr(self, dynamo_response):
        if len(dynamo_response) < 1:
            logger.info("Patient is not held in the National Document Repository.")
            logger.info("Moving on to the next message.")
            return False
        else:
            return True
