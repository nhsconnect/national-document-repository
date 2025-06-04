import uuid
import logging
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def test_logging_into_new_correlation(mocker):
    tracking_id = "TEST-1"
    log_message = "This is a log message"
    logger_info_mock = mocker.patch.object(logger.logger, "info")
    mock_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    mocker.patch("uuid.uuid4", return_value=mock_uuid)

    logger.info_with_correlation(log_message, tracking_id)

    written_message = logger_info_mock.call_args[0][0]
    assert written_message == f"[{tracking_id}-{mock_uuid}] - {log_message}"

def test_logging_into_existing_correlation(mocker):
    tracking_id = "TEST-1"
    log_message = "This is a log message"
    mock_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")
    mocker.patch("uuid.uuid4", return_value=mock_uuid)
    second_log_message = "This is a second log message"

    correlation = logger.info_with_correlation(log_message, tracking_id)
    logger_info_mock = mocker.patch.object(logger.logger, "info")

    logger.info_in_correlation(second_log_message, correlation)

    written_message = logger_info_mock.call_args[0][0]
    assert written_message == f"[{tracking_id}-{mock_uuid}] - {second_log_message}"
