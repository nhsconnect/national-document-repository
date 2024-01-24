import html

from models.config import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    validate_email,
)


class Feedback(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    feedback_content: str
    experience: str = Field(alias="howSatisfied")
    respondent_email: str
    respondent_name: str

    @field_validator(
        "feedback_content", "experience", "respondent_email", "respondent_name"
    )
    @classmethod
    def sanitise_string(cls, value: str) -> str:
        # run a html entity encode on incoming values to avoid malicious html injection
        return html.escape(value)

    @field_validator("respondent_email")
    @classmethod
    def validate_email_and_allow_blank(cls, email: str) -> str:
        if email == "":
            return email
        return validate_email(email)[1]
