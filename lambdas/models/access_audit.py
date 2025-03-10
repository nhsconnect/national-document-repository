from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_pascal


class AccessAuditReason(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_pascal)

    type: str
    user_session_id: str
    user_id: str
    user_ods_code: str
    timestamp: datetime = int(datetime.now().timestamp())
    reason_codes: list[str]
    custom_reason: str | None = None

    @computed_field(alias="ID")
    def id(self) -> str:
        return f"{self.user_session_id}#{self.timestamp}"
