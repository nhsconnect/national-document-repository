from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ValidationScore(Enum):
    NO_MATCH = 0
    PARTIAL_MATCH = 1
    MIXED_FULL_MATCH = 2
    FULL_MATCH = 3


class ValidationResult(BaseModel):
    given_name_match: list[str] = []
    family_name_match: Optional[str] = None
    score: ValidationScore = ValidationScore.NO_MATCH
