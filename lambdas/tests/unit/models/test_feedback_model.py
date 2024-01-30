import json

import pytest
from models.feedback_model import Feedback
from pydantic import ValidationError


def test_feedback_model_parse_json_from_frontend():
    mock_feedback = json.dumps(
        {
            "feedbackContent": "Mock feedback content",
            "howSatisfied": "Very Satisfied",
            "respondentName": "Jane Smith",
            "respondentEmail": "jane_smith@testing.com",
        }
    )

    expected = Feedback(
        feedback_content="Mock feedback content",
        experience="Very Satisfied",
        respondent_name="Jane Smith",
        respondent_email="jane_smith@testing.com",
    )

    actual = Feedback.model_validate_json(mock_feedback)

    assert actual == expected


def test_feedback_model_sanitise_strings():
    mock_input = json.dumps(
        {
            "feedbackContent": '<script type="text/javascript">some malicious script</script>',
            "howSatisfied": "Neither satisfied or dissatisfied",
            "respondentName": "Janet Smith",
            "respondentEmail": "janet_smith@testing.com",
        }
    )
    expected_sanitised_string = (
        "&lt;script type=&quot;"
        "text/javascript&quot;&gt;some malicious script&lt;/script&gt;"
    )
    actual = Feedback.model_validate_json(mock_input)
    assert actual.feedback_content == expected_sanitised_string


def test_feedback_model_allows_email_and_name_to_be_blank():
    mock_feedback = json.dumps(
        {
            "feedbackContent": "Mock feedback content 2",
            "howSatisfied": "Satisfied",
            "respondentName": "",
            "respondentEmail": "",
        }
    )

    expected = Feedback(
        feedback_content="Mock feedback content 2",
        experience="Satisfied",
        respondent_name="",
        respondent_email="",
    )

    actual = Feedback.model_validate_json(mock_feedback)

    assert actual == expected


def test_feedback_model_allows_email_and_name_to_be_omitted():
    mock_feedback = json.dumps(
        {
            "feedbackContent": "Mock feedback content 3",
            "howSatisfied": "Dissatisfied",
        }
    )

    expected = Feedback(
        feedback_content="Mock feedback content 3",
        experience="Dissatisfied",
        respondent_name="",
        respondent_email="",
    )

    actual = Feedback.model_validate_json(mock_feedback)

    assert actual == expected


def test_feedback_model_raise_validation_error_for_invalid_email_address():
    mock_feedback = json.dumps(
        {
            "feedbackContent": "Mock feedback content 4",
            "howSatisfied": "Very dissatisfied",
            "respondentName": "somebody",
            "respondentEmail": "not a valid email",
        }
    )

    with pytest.raises(ValidationError):
        Feedback.model_validate_json(mock_feedback)


def test_feedback_model_raise_validation_error_for_invalid_input():
    mock_input = '{"key": {"some value"}}'

    with pytest.raises(ValidationError):
        Feedback.model_validate_json(mock_input)
