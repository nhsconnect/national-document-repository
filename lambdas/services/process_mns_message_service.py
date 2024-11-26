import os
import time
from urllib.error import HTTPError

from botocore.exceptions import ClientError
from enums.death_notification_status import DeathNotificationStatus
from enums.mns_notification_types import MNSNotificationTypes
from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from models.mns_sqs_message import MNSSQSMessage
from models.pds_models import Patient
from pydantic_core._pydantic_core import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.nhs_oauth_service import NhsOauthService
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import PdsErrorException, PdsResponseValidationException
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

    def handle_mns_notification(self, message: MNSSQSMessage):
        try:
            if message.type == MNSNotificationTypes.CHANGE_OF_GP.value:
                self.handle_gp_change_notification(message)

            if message.type == MNSNotificationTypes.DEATH_NOTIFICATION.value:
                self.handle_death_notification(message)

        except Exception as e:
            logger.info(
                f"Unable to process message: {message.id}, of type: {message.type}"
            )
            logger.info(f"{e}")
            return

    def handle_subscription_notification(self, message):
        pass

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
        time.sleep(0.2)  # buffer to avoid over stretching PDS API
        logger.info("Getting the latest ODS code from PDS...")

        try:
            pds_response = self.pds_service.pds_request(
                nhs_number=nhs_number, retry_on_expired=True
            )
            pds_response.raise_for_status()

            pds_response_json = pds_response.json()

            patient = Patient.model_validate(pds_response_json)

            return patient.get_ods_code_or_inactive_status_for_gp()
        except HTTPError as e:
            raise PdsErrorException(
                f"PDS returned a {e.response.status_code} code response for patient with NHS number {nhs_number}"
            )
        except ValidationError:
            raise PdsResponseValidationException(
                f"PDS returned an invalid response for patient with NHS number {nhs_number}"
            )
