from enum import StrEnum


class AlarmState(StrEnum):
    OK = "OK"
    ALARM = "ALARM"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
