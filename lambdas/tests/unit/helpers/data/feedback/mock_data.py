import json
import os

from models.feedback_model import Feedback


def readfile(filename: str) -> str:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r") as f:
        return f.read()


MOCK_VALID_FEEDBACK_BODY_JSON_STR = readfile("valid_feedback_body.json")
MOCK_VALID_FEEDBACK_BODY = json.loads(MOCK_VALID_FEEDBACK_BODY_JSON_STR)
MOCK_EMAIL_BODY = readfile("expected_email_body.txt")

MOCK_VALID_FEEDBACK_BODY_ANONYMOUS_JSON_STR = readfile(
    "valid_feedback_body_anonymous.json"
)

MOCK_VALID_SEND_FEEDBACK_EVENT = {
    "body": MOCK_VALID_FEEDBACK_BODY_JSON_STR,
    "httpMethod": "POST",
}
MOCK_PARSED_FEEDBACK = Feedback.model_validate_json(MOCK_VALID_FEEDBACK_BODY_JSON_STR)
MOCK_PARSED_FEEDBACK_ANONYMOUS = Feedback.model_validate_json(
    MOCK_VALID_FEEDBACK_BODY_ANONYMOUS_JSON_STR
)
