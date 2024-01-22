from html import escape

from pydantic import BaseModel, field_validator


class Feedback(BaseModel):
    feedback_content: str
    experience: str
    email: str
    name: str

    @field_validator("feedback_content", "experience", "email", "name")
    @classmethod
    def sanitise_string(cls, value: str) -> str:
        # run a html entity encode on incoming values to avoid malicious html injection
        return escape(value)
