import logging

from utils.logging_formatter import LoggingFormatter


class LoggingService:
    audit_logger = None

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.formatter = LoggingFormatter()
        logging.Formatter.format = self.formatter.format

    def info(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.info(message, extra={"custom_args": custom_args}, *args, **kwargs)

    def error(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.error(message, extra={"custom_args": custom_args}, *args, **kwargs)

    def warning(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.warning(
            message, extra={"custom_args": custom_args}, *args, **kwargs
        )

    def debug(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.debug(message, extra={"custom_args": custom_args}, *args, **kwargs)

    def exception(
        self, message, custom_args: dict = None, *args, exc_info=True, **kwargs
    ):
        self.logger.exception(
            message, exc_info, extra={"custom_args": custom_args}, *args, **kwargs
        )

    def critical(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.critical(
            message, extra={"custom_args": custom_args}, *args, **kwargs
        )
