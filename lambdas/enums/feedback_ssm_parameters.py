from enum import Enum


class FeedbackSSMParameter(str, Enum):
    SENDER_EMAIL = "/prs/dev/user-input/feedback-sender-email"
    RECIPIENT_EMAIL_LIST = "/prs/dev/user-input/feedback-recipient-email-list"
    EMAIL_SUBJECT = "/prs/dev/user-input/feedback-email-subject"
