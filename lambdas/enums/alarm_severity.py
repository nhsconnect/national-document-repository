from utils.multi_value_enum import MultiValueEnum


class AlarmSeverity(MultiValueEnum):
    HIGH = "\U0001F534", "red_circle"
    MEDIUM = "\U0001F7E0", "large_orange_circle"
    LOW = "\U0001F7E1", "large_yellow_circle"
    OK = "\U0001F7E2", "large_green_circle"
    # TODO PRM-134 add 'insufficient data' grey circle
