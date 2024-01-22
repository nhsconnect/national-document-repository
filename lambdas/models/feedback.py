from typing import Optional

from pydantic import BaseModel


class Feedback(BaseModel):
    feedback_content: str
    experience: str
    email: Optional[str]
    name: Optional[str]
