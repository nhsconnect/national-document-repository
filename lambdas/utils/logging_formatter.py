import json
import logging

from utils.request_context import request_context


class LoggingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        auth = getattr(request_context, "authorization", "No Auth")
        request_id = getattr(request_context, "request_id", "No Request")
        patient_nhs_no = getattr(request_context, "patient_nhs_no", "No NHS number")
        app_interaction = getattr(
            request_context, "app_interaction", "Missing app interaction"
        )

        log_content = {
            "Message": record.getMessage(),
            "App Interaction": app_interaction,
            "Correlation Id": request_id,
            "Authorisation": auth,
            "Patient NHS number": patient_nhs_no,
        }

        if record.__dict__.get("custom_args", {}) is not None:
            log_content.update(record.__dict__.get("custom_args", {}))

        return json.dumps(log_content)
