from enum import StrEnum


class AlarmHistoryField(StrEnum):
    ALARMNAMEMETRIC = "AlarmNameMetric"
    TIMECREATED = "TimeCreated"
    LASTUPDATED = "LastUpdated"
    CHANNELID = "ChannelId"
    HISTORY = "History"
    SLACKTIMESTAMP = "SlackTimestamp"
    TIMETOEXIST = "TimeToExist"
