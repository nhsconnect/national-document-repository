import os
from datetime import datetime

from botocore.exceptions import ClientError
from enums.death_notification_status import DeathNotificationStatus
from enums.mns_notification_types import MNSNotificationTypes
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from models.document_reference import DocumentReference
from models.sqs.mns_sqs_message import MNSSQSMessage
from services.base.sqs_service import SQSService
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import PdsErrorException
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class MNSNotificationService:
    def __init__(self):
        self.document_service = DocumentService()
        self.table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.pds_service = get_pds_service()
        self.sqs_service = SQSService()
        self.queue = os.getenv("MNS_NOTIFICATION_QUEUE_URL")
        self.DOCUMENT_UPDATE_FIELDS = {"current_gp_ods", "custodian", "last_updated"}
        self.PCSE_ODS = "X4S4L"

    def handle_mns_notification(self, message: MNSSQSMessage):
        try:
            match message.type:
                case MNSNotificationTypes.CHANGE_OF_GP:
                    logger.info("Handling GP change notification.")
                    self.handle_gp_change_notification(message)
                case MNSNotificationTypes.DEATH_NOTIFICATION:
                    logger.info("Handling death status notification.")
                    self.handle_death_notification(message)

        except PdsErrorException as e:
            logger.info("An error occurred when calling PDS")
            logger.info(
                f"Unable to process message: {message.id}, of type: {message.type}"
            )
            logger.info(f"{e}")
            raise e

        except ClientError as e:
            logger.info(
                f"Unable to process message: {message.id}, of type: {message.type}"
            )
            logger.info(f"{e}")
            raise e

    def handle_gp_change_notification(self, message: MNSSQSMessage) -> None:
        patient_document_references = self.get_patient_documents(
            message.subject.nhs_number
        )

        if not patient_document_references:
            return

        updated_ods_code = self.get_updated_gp_ods(message.subject.nhs_number)
        self.update_patient_ods_code(patient_document_references, updated_ods_code)
        logger.info("Update complete for change of GP")

    def handle_death_notification(self, message: MNSSQSMessage) -> None:
        death_notification_type = message.data["deathNotificationStatus"]
        nhs_number = message.subject.nhs_number

        match death_notification_type:
            case DeathNotificationStatus.INFORMAL:
                logger.info(
                    "Patient is deceased - INFORMAL, moving on to the next message."
                )

            case DeathNotificationStatus.REMOVED:
                patient_document_references = self.get_patient_documents(nhs_number)
                if patient_document_references:
                    updated_ods_code = self.get_updated_gp_ods(nhs_number)
                    self.update_patient_ods_code(
                        patient_document_references, updated_ods_code
                    )
                    logger.info("Update complete for death notification change.")

            case DeathNotificationStatus.FORMAL:
                patient_document_references = self.get_patient_documents(nhs_number)
                if patient_document_references:
                    self.update_patient_ods_code(
                        patient_document_references, PatientOdsInactiveStatus.DECEASED
                    )
                    logger.info(
                        f"Update complete, patient marked {PatientOdsInactiveStatus.DECEASED}."
                    )

    def update_patient_ods_code(
        self, patient_documents: list[DocumentReference], updated_ods_code: str
    ) -> None:
        if not patient_documents:
            return
        for reference in patient_documents:
            logger.info("Updating patient document reference...")

            if (
                reference.current_gp_ods != updated_ods_code
                or reference.custodian != updated_ods_code
            ):
                updated_custodian = updated_ods_code
                if updated_ods_code in [
                    PatientOdsInactiveStatus.DECEASED,
                    PatientOdsInactiveStatus.SUSPENDED,
                ]:
                    updated_custodian = self.PCSE_ODS
                reference.current_gp_ods = updated_ods_code
                reference.custodian = updated_custodian
                reference.last_updated = int(datetime.now().timestamp())

                self.document_service.update_document(
                    self.table,
                    reference,
                    self.DOCUMENT_UPDATE_FIELDS,
                )

    def get_updated_gp_ods(self, nhs_number: str) -> str:
        patient_details = self.pds_service.fetch_patient_details(nhs_number)
        return patient_details.general_practice_ods

    def get_patient_documents(self, nhs_number: str) -> list[DocumentReference]:
        """Fetch patient documents and return them if they exist."""
        return self.document_service.fetch_documents_from_table_with_nhs_number(
            nhs_number, self.table
        )
