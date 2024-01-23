import json

import pytest
from pydantic import ValidationError

from models.feedback_model import Feedback


def test_feedback_model_parse_json_from_frontend():
    mock_feedback_json_string = (
        '{"feedbackContent": "Mock feedback content", "howSatisfied": "Very Satisfied", '
        '"respondentName": "Jane Smith", "respondentEmail": "jane_smith@testing.com"}'
    )

    expected = Feedback(
        feedback_content="Mock feedback content",
        experience="Very Satisfied",
        respondent_name="Jane Smith",
        respondent_email="jane_smith@testing.com",
    )

    actual = Feedback.model_validate_json(mock_feedback_json_string)

    assert actual == expected


def test_feedback_model_sanitise_strings():
    mock_input = json.dumps(
        {
            "feedbackContent": '<script type="text/javascript">some malicious script</script>',
            "howSatisfied": "Very Satisfied",
            "respondentName": "",
            "respondentEmail": "",
        }
    )
    expected_sanitised_string = (
        "&lt;script type=&quot;"
        "text/javascript&quot;&gt;some malicious script&lt;/script&gt;"
    )
    actual = Feedback.model_validate_json(mock_input)
    assert actual.feedback_content == expected_sanitised_string


def test_feedback_model_raise_validation_error_for_invalid_input():
    mock_input = '{"key": {"some value"}}'

    with pytest.raises(ValidationError):
        Feedback.model_validate_json(mock_input)
