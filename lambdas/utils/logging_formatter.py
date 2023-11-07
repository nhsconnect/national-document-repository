import json
import logging

from utils.request_context import request_context


class LoggingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:

        auth = "No Auth"
        if request_context.authorization is not None:
            auth = request_context.authorization

        s = super().format(record)
        logging.info("Formatted to S")
        logging.info(f"requestId: {request_context.request_id}")
        logging.info(f"record: {record}")
        logging.info(f"record dict: {record.__dict__}")
        
        d = {
            "correlation_id": request_context.request_id,
            "auth": auth
            **record.__dict__.get("custom_args", {}),
            "Message": s,
        }
        logging.info(f"d: {json.dumps(d)}")
        return json.dumps(d)
