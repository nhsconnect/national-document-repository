from enums.mns_notification_types import MNSNotificationTypes
from models.mns_sqs_message import MNSSQSMessage
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class MNSNotificationService:
    def __init__(self):
        self.message = None

    def handle_mns_notification(self, message: MNSSQSMessage):
        action = {
            MNSNotificationTypes.CHANGE_OF_GP.value: self.handle_gp_change_notification,
            MNSNotificationTypes.DEATH_NOTIFICATION.value: self.handle_death_notification,
        }
        action.get(message.type)(message)

    def handle_gp_change_notification(self, message):
        pass

    def handle_death_notification(self, message):
        pass
