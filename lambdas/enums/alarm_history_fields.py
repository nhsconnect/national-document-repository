from enum import StrEnum


class AlarmHistoryFields(StrEnum):
    ALARMNAME = "AlarmName"
    TIMECREATED = "TimeCreated"
    LASTUPDATED = "LastUpdated"
    CHANNELID = "ChannelId"
    HISTORY = "History"
    SLACKTIMESTAMP = "SlackTimestamp"
    TIMETOEXIST = "TimeToExist"
