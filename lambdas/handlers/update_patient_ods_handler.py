from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def update_patient_ods_handler(event, context):

    logger.info("Updating patient ods codes")
