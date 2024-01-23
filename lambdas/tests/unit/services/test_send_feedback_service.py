import json

from models.feedback import Feedback
from services.send_feedback_service import SendFeedbackService


# def test_send_feedback():
    # service = SendFeedbackService()
    # feedback_body = json.dumps(
    #     {
    #         "feedbackContent": "Mock feedback content",
    #         "howSatisfied": "Very Satisfied",
    #         "respondentName": "Jane Smith§",
    #         "respondentEmail": "jane_smith@testing.com",
    #     }
    # )
    # Feedback.model_validate_json(feedback_body)
    # service.process_feedback(feedback_body)
