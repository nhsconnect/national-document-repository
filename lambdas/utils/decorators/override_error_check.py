import os
from typing import Callable

from utils.audit_logging_setup import LoggingService
from utils.error_testing_utils import check_manual_error_conditions

logger = LoggingService(__name__)


def override_error_check(lambda_func: Callable):
    """A decorator for lambda handler.
    Interceptor to identify if any manual error throwing has been enabled for testing purposes.
    This should always return to the initial handler call if the conditions are not meet to trigger
    a manual error

    Usage:
    @validate_patient_id
    def lambda_handler(event, context):
        ...
    """

    disabled_workspaces = ["pre-prod", "prod"]

    def interceptor(event, context):
        workspace = os.getenv("WORKSPACE")
        error_override = os.getenv("ERROR_TRIGGER")

        logger.info(f"workspace: {workspace}")
        logger.info(f"error_override: {error_override}")

        # fail fast if workspace is invalid
        if workspace is None or workspace in disabled_workspaces:
            return lambda_func(event, context)

        # fail fast if error trigger is not set
        if error_override is None or error_override == "":
            return lambda_func(event, context)

        check_manual_error_conditions(error_override)

        return lambda_func(event, context)

    return interceptor
