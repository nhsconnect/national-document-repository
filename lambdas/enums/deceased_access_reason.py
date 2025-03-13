from utils.multi_value_enum import MultiValueEnum


class DeceasedAccessReason(MultiValueEnum):
    MEDICAL = "01", "Coroner or medical examiner request"
    LEGAL = "02", "Legal or insurance request"
    PERSONAL = "03", "Family member or personal representation request"
    INTERNAL = "04", "Internal NHS request"
    MANAGE = "05", "Manage this record at the end of its retention period"
    OTHER = "99", "Another reason"
