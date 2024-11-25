from enum import StrEnum


class MNSNotificationTypes(StrEnum):
    CHANGE_OF_GP = "pds-change-of-gp-1"
    DEATH_NOTIFICATION = "pds-death-notification-1"
    SUBSCRIPTION = "Subscription"

    @staticmethod
    def list() -> [str]:
        return [str(type.value) for type in MNSNotificationTypes]
