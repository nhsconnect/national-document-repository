from typing import Dict, Optional

from pydantic import BaseModel


class FlagStatus(BaseModel):
    enabled: bool


class FeatureFlag(BaseModel):
    feature_flags: Optional[Dict[str, FlagStatus]] = {}

    def format_flags(self):
        return {key: value.enabled for key, value in self.feature_flags.items()}
