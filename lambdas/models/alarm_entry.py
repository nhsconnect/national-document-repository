from typing import Optional

from enums.alarm_severity import AlarmSeverity
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal


class AlarmEntry(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True)
    alarm_name_metric: str
    time_created: int
    history: list[AlarmSeverity] = Field(
        default_factory=list, exclude=True
    )  # stored in the database as a list of Strings containing the AlarmSeverity.name
    last_updated: Optional[int] = None
    slack_timestamp: Optional[str] = None
    channel_id: str
    time_to_exist: Optional[int] = None

    def to_dynamo(self):
        return {
            **self.model_dump(exclude={"history"}, by_alias=True),
            "history": self.get_alarm_severity_list_as_string(),
        }

    @classmethod
    def from_dynamo(cls, dynamo_entry):
        dynamo_entry["history"] = [
            AlarmSeverity[name] for name in dynamo_entry["history"]
        ]
        return cls(**dynamo_entry)

    def get_alarm_severity_list_as_string(self):
        return [severity.name for severity in self.history]
