import os

from botocore.exceptions import ClientError
from enums.death_notification_status import DeathNotificationStatus
from enums.mns_notification_types import MNSNotificationTypes
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from models.mns_sqs_message import MNSSQSMessage
from services.base.dynamo_service import DynamoDBService
from services.base.nhs_oauth_service import NhsOauthService
from services.base.sqs_service import SQSService
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import PdsErrorException
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class MNSNotificationService:
    def __init__(self):
        self.message = None
        self.dynamo_service = DynamoDBService()
        self.table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        pds_service_class = get_pds_service()
        ssm_service = SSMService()
        auth_service = NhsOauthService(ssm_service)
        self.pds_service = pds_service_class(ssm_service, auth_service)
        self.unprocessed_message = []
        self.sqs_service = SQSService()
        self.queue = os.getenv("MNS_NOTIFICATION_QUEUE_URL")

    def handle_mns_notification(self, message: MNSSQSMessage):
        try:
            if message.type == MNSNotificationTypes.CHANGE_OF_GP.value:
                logger.info("Handling GP change notification.")
                self.handle_gp_change_notification(message)

            if message.type == MNSNotificationTypes.DEATH_NOTIFICATION.value:
                logger.info("Handling death status notification.")
                self.handle_death_notification(message)

        except PdsErrorException("Error when requesting patient from PDS"):
            self.send_message_back_to_queue(message)

        except Exception as e:
            logger.info(
                f"Unable to process message: {message.id}, of type: {message.type}"
            )
            logger.info(f"{e}")
            return

    def handle_gp_change_notification(self, message: MNSSQSMessage):

        patient_document_references = self.get_patient_documents(
            message.subject.nhs_number
        )

        if len(patient_document_references) < 1:
            logger.info("Patient is not held in the National Document Repository.")
            logger.info("Moving on to the next message.")
            return

        updated_ods_code = self.get_updated_gp_ods(message.subject.nhs_number)

        for reference in patient_document_references:
            if reference["CurrentGpOds"] is not updated_ods_code:
                self.dynamo_service.update_item(
                    table_name=self.table,
                    key=reference["ID"],
                    updated_fields={"CurrentGpOds": updated_ods_code},
                )

        logger.info("Update complete for change of GP")

    def handle_death_notification(self, message: MNSSQSMessage):
        if self.is_informal_death_notification(message):
            logger.info(
                "Patient is deceased - INFORMAL, moving on to the next message."
            )
            return

        try:
            patient_documents = self.get_patient_documents(message.subject.nhs_number)

            if len(patient_documents) < 1:
                logger.info("Patient is not held in the National Document Repository.")
                logger.info("Moving on to the next message.")
                return

            if (
                message.data["deathNotificationStatus"]
                == DeathNotificationStatus.FORMAL.value
            ):
                self.update_patient_details(
                    patient_documents, PatientOdsInactiveStatus.DECEASED.value
                )
                logger.info("Update complete, patient marked DECE.")
                return

            if (
                message.data["deathNotificationStatus"]
                == DeathNotificationStatus.REMOVED.value
            ):
                update_ods_code = self.get_updated_gp_ods(message.subject.nhs_number)
                self.update_patient_details(patient_documents, update_ods_code)
                logger.info("Update complete for death notification change.")
        except ClientError as e:
            logger.error(f"{e}")

    def is_informal_death_notification(self, message: MNSSQSMessage) -> bool:
        return (
            message.data["deathNotificationStatus"]
            == DeathNotificationStatus.INFORMAL.value
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

    def update_patient_details(self, patient_documents: list[dict], code: str) -> None:
        for document in patient_documents:
            logger.info("Updating patient document reference...")
            try:
                self.dynamo_service.update_item(
                    table_name=self.table,
                    key=document["ID"],
                    updated_fields={"CurrentGpOds": code},
                )
            except ClientError as e:
                logger.error("Unable to update patient document reference")
                raise e

    def get_updated_gp_ods(self, nhs_number: str) -> str:
        patient_details = self.pds_service.fetch_patient_details(nhs_number)
        return patient_details.general_practice_ods

    def send_message_back_to_queue(self, message: MNSSQSMessage):
        logger.info("Sending message back to queue...")
        self.sqs_service.send_message_standard(
            queue_url=self.queue, message_body=message.model_dump_json(by_alias=True)
        )
