import json
import logging

from utils.request_context import request_context


class LoggingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:

        auth = "No Auth"
        if request_context.authorization is not None:
            auth = request_context.authorization

        s = super().format(record)
        d = {
            "correlation_id": request_context.request_id,
            "auth": auth,
            "Message": s
        }

        if record.__dict__.get("custom_args", {}) is not None: 
            d.update(record.__dict__.get("custom_args", {}))

        return json.dumps(d)
