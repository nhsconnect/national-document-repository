import json
import logging

from utils.request_context import request_context


class LoggingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record)
        d = {
            "correlation_id": request_context.request_id,
            "auth": request_context.authorization,

            **record.__dict__.get('custom_args', {}),
            "Message": s
        }
        return json.dumps(d)