import boto3

from models.feedback import Feedback
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class SendFeedbackService:
    def __init__(self):
        self.ses_client = boto3.client("ses")

    def process_feedback(self, body: str):
        feedback = Feedback.model_validate_json(body)
        email_body = self.build_email_body(feedback)

        email_subject = "Digitised Lloyd George feedback"
        from_address = "feedback@access-request-fulfilment.patient-deductions.nhs.uk"
        to_address = "joe.fong1@nhs.net"

        print(f"sending email:\n{email_body}")

        response = self.ses_client.send_email(
            Source=from_address,
            Destination={"ToAddresses": [to_address]},
            Message={
                "Subject": {"Data": email_subject},
                "Body": {"Html": {"Data": email_body}},
            },
        )
        print(response)

    def build_email_body(self, feedback: Feedback) -> str:
        email_body_html = "<html><body>"
        if feedback.name:
            email_body_html += f"<h2>Name</h2><p>{feedback.name}</p>"
        if feedback.email:
            email_body_html += f"<h2>Email Address</h2><p>{feedback.email}</p>"

        email_body_html += f"<h2>Feedback</h2><p>{feedback.feedback_content}</p>"
        email_body_html += f"<h2>Overall Experience</h2><p>{feedback.experience}</p>"
        email_body_html += "</html></body>"

        return email_body_html
