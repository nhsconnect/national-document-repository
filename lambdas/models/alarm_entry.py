from typing import Optional

from enums.alarm_severity import AlarmSeverity
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal


class AlarmEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True)
    alarm_name_metric: str
    time_created: int
    history: list[AlarmSeverity] = []
    last_updated: Optional[int] = None
    slack_timestamp: Optional[str] = None
    channel_id: str
    time_to_exist: Optional[int] = None
