import os
from typing import List

import boto3
from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from models.feedback_model import Feedback
from pydantic import ValidationError
from services.base.ssm_service import SSMService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import SendFeedbackException

logger = LoggingService(__name__)
failure_msg = "Failed to send feedback by email"


class SendFeedbackService:
    def __init__(self):
        self.ses_client = boto3.client("ses")
        self.sender_email: str = os.environ["FROM_EMAIL_ADDRESS"]
        self.email_subject: str = os.environ["EMAIL_SUBJECT"]
        self.recipient_email_list: list[str] = self.get_email_recipients_list()

    def process_feedback(self, body: str):
        logger.info("Parsing feedback content...")
        try:
            feedback = Feedback.model_validate_json(body)
        except ValidationError as e:
            logger.error(e)
            logger.error(
                LambdaError.FeedbackInvalidBody.to_str(),
                {"Result": failure_msg},
            )
            raise SendFeedbackException(400, LambdaError.FeedbackInvalidBody)

        email_body_html = self.build_email_body(feedback)
        self.send_feedback_by_email(email_body_html)

    @staticmethod
    def get_email_recipients_list() -> List[str]:
        try:
            ssm_service = SSMService()
            email_recipient_ssm_param_key = os.environ["EMAIL_RECIPIENT_SSM_PARAM_KEY"]

            recipients = ssm_service.get_ssm_parameter(email_recipient_ssm_param_key)
            return recipients.split(",")
        except ClientError as e:
            logger.error(e)
            logger.error(
                LambdaError.FeedbackFetchParamFailure.to_str(),
                {"Result": failure_msg},
            )
            raise SendFeedbackException(500, LambdaError.FeedbackFetchParamFailure)

    @staticmethod
    def build_email_body(feedback: Feedback) -> str:
        email_body_html = "<html><body>"
        if feedback.respondent_name:
            email_body_html += f"<h2>Name</h2><p>{feedback.respondent_name}</p>"
        if feedback.respondent_email:
            email_body_html += (
                f"<h2>Email Address</h2><p>{feedback.respondent_email}</p>"
            )

        email_body_html += f"<h2>Feedback</h2><p>{feedback.feedback_content}</p>"
        email_body_html += f"<h2>Overall Experience</h2><p>{feedback.experience}</p>"
        email_body_html += "</html></body>"

        return email_body_html

    def send_feedback_by_email(self, email_body_html: str):
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
            logger.error(
                LambdaError.FeedbackSESFailure.to_str(),
                {"Result": failure_msg},
            )
            raise SendFeedbackException(500, LambdaError.FeedbackSESFailure)
