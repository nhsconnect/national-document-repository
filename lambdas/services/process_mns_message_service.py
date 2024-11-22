import os

from enums.death_notification_status import DeathNotificationStatus
from enums.mns_notification_types import MNSNotificationTypes
from models.mns_sqs_message import MNSSQSMessage
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class MNSNotificationService:
    def __init__(self):
        self.message = None
        self.dynamo_service = DynamoDBService()
        self.table = os.getenv("LLOYD_GEORGE_DYNAMODB_TABLE")

    def handle_mns_notification(self, message: MNSSQSMessage):
        action = {
            MNSNotificationTypes.CHANGE_OF_GP.value: self.handle_gp_change_notification,
            MNSNotificationTypes.DEATH_NOTIFICATION.value: self.handle_death_notification,
        }
        action.get(message.type)(message)

    def handle_subscription_notification(self, message):
        pass

    def handle_gp_change_notification(self, message: MNSSQSMessage):
        pass

    def handle_death_notification(self, message: MNSSQSMessage):
        if self.is_informal_death_notification(message):
            return

        if not self.have_patient_in_table(message):
            return

    def is_informal_death_notification(self, message: MNSSQSMessage) -> bool:
        return (
            message.data["deathNotificationStatus"]
            == DeathNotificationStatus.INFORMAL.value
        )

    def have_patient_in_table(self, message: MNSSQSMessage):
        response = self.dynamo_service.query_table_by_index(
            table_name=self.table,
            index_name="NhsNumberIndex",
            search_key="NhsNumber",
            search_condition=message.subject.nhs_number,
        )
        return len(response["Items"]) < 1

    def update_dynamo_table(self, code):
        pass

    def get_current_ods_code(self):
        pass
