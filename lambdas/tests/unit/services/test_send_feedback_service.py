from services.send_feedback_service import SendFeedbackService


def test_send_feedback():
    service = SendFeedbackService()
    feedback_body = {
        'feedback_content': 'test0987',
        'experience': 'Very satisfied',
        'email': 'test1234@test_email.com',
        'name': 'Jane Smith'
    }
    service.process_feedback(feedback_body)
