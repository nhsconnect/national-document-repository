import json
import logging

from utils.request_context import request_context


class LoggingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        auth = "No Auth"
        request_id = "No Request"
        patient_nhs_no = "No NHS number"
        app_interaction = "Missing app interaction"
        if getattr(request_context, "authorization", None) is not None:
            auth = request_context.authorization
        if getattr(request_context, "request_id", None) is not None:
            request_id = request_context.request_id
        if getattr(request_context, "patient_nhs_no", None) is not None:
            patient_nhs_no = request_context.patient_nhs_no
        if getattr(request_context, "app_interaction", None) is not None:
            app_interaction = request_context.app_interaction

        d = {
            "Message": record.getMessage(),
            "App Interaction": app_interaction,
            "Correlation Id": request_id,
            "Authorisation": auth,
            "Patient NHS number": patient_nhs_no,
        }

        if record.__dict__.get("custom_args", {}) is not None:
            d.update(record.__dict__.get("custom_args", {}))

        return json.dumps(d)
