import json
import os


def readfile(filename: str) -> str:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r") as f:
        return f.read()


MOCK_VALID_FEEDBACK_BODY_JSON_STR = readfile("valid_feedback_body.json")
MOCK_VALID_FEEDBACK_BODY = json.loads(MOCK_VALID_FEEDBACK_BODY_JSON_STR)
MOCK_EXPECTED_EMAIL_BODY = readfile("expected_email_body.txt")

MOCK_VALID_SEND_FEEDBACK_EVENT = {
    "body": MOCK_VALID_FEEDBACK_BODY_JSON_STR,
    "httpMethod": "POST",
}
