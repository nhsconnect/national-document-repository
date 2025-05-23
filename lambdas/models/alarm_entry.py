from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal


class AlarmEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True)
    alarm_name: str
    time_created: int
    history: list[str] = []
    last_updated: Optional[int] = None
    slack_timestamp: Optional[str] = None
    channel_id: str
    time_to_exist: Optional[int] = None
