import boto3
from botocore.exceptions import ClientError
from enums.feedback_ssm_parameters import FeedbackSSMParameter
from enums.lambda_error import LambdaError
from models.feedback import Feedback
from pydantic import ValidationError
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import SendFeedbackException

logger = LoggingService(__name__)


class SendFeedbackService:
    def __init__(self):
        self.ses_client = boto3.client("ses")
        send_feedback_parameters = self.get_parameters()

        self.sender_email: str = send_feedback_parameters[
            FeedbackSSMParameter.SENDER_EMAIL
        ]
        self.recipient_email_list: list[str] = send_feedback_parameters[
            FeedbackSSMParameter.RECIPIENT_EMAIL_LIST
        ].split(",")
        self.email_subject: str = send_feedback_parameters[
            FeedbackSSMParameter.EMAIL_SUBJECT
        ]

    def process_feedback(self, body: str):
        logger.info("Parsing feedback content...")
        try:
            feedback = Feedback.model_validate_json(body)
        except ValidationError as e:
            logger.error(e)
            logger.error(f"{LambdaError.FeedbackInvalidBody.to_str}", {"Result": "Sending feedback failed"})
            raise SendFeedbackException(400, LambdaError.FeedbackInvalidBody)

        email_body_html = self.build_email_body(feedback)

        logger.info("Sending feedback by email")
        try:
            self.ses_client.send_email(
                Source=self.sender_email,
                Destination={"ToAddresses": self.recipient_email_list},
                Message={
                    "Subject": {"Data": self.email_subject},
                    "Body": {"Html": {"Data": email_body_html}},
                },
            )
        except ClientError as e:
            logger.error(e)
            logger.error(f"{LambdaError.FeedbackSESFailure.to_str}", {"Result": "Sending feedback failed"})
            raise SendFeedbackException(500, LambdaError.FeedbackSESFailure)

    @staticmethod
    def get_parameters() -> dict:
        try:
            ssm_service = SSMService()
            return ssm_service.get_ssm_parameters(list(FeedbackSSMParameter))
        except ClientError as e:
            logger.error(e)
            logger.error(f"{LambdaError.FeedbackMissingParam.to_str}", {"Result": "Sending feedback failed"})
            raise SendFeedbackException(500, LambdaError.FeedbackMissingParam)

    @staticmethod
    def build_email_body(feedback: Feedback) -> str:
        email_body_html = "<html><body>"
        if feedback.name:
            email_body_html += f"<h2>Name</h2><p>{feedback.name}</p>"
        if feedback.email:
            email_body_html += f"<h2>Email Address</h2><p>{feedback.email}</p>"

        email_body_html += f"<h2>Feedback</h2><p>{feedback.feedback_content}</p>"
        email_body_html += f"<h2>Overall Experience</h2><p>{feedback.experience}</p>"
        email_body_html += "</html></body>"

        return email_body_html
