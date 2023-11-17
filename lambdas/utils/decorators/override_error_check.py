from typing import Callable

import os
import logging

from utils.error_testing_utils import check_manual_error_conditions

def override_error_check(lambda_func: Callable):
    """A decorator for lambda handler.
    Interceptor to identiy if any manual error throwing has been enabled for testing purposes.
    This should always return to the initial handler call if the conditions are not meet to trigger
    a manual error

    Usage:
    @validate_patient_id
    def lambda_handler(event, context):
        ...
    """

    disabled_workspaces = ["pre-prod", "prod"]

    def interceptor(event, context):
        try:
            workspace = os.environ["WORKSPACE"]
            error_override = os.environ["ERROR_TRIGGER"]

            logging.info(f"workspace: {workspace}")
            logging.info(f"error_override: {error_override}")

            # fail fast if workspace is invalid 
            if workspace == None or workspace in disabled_workspaces:
                return lambda_func(event, context)
            
            logging.info("HERE 1")
            # fail fast if error trigger is not set
            if error_override is None or error_override == "":
                return lambda_func(event, context)
                
            logging.info("HERE 2")
            
            check_manual_error_conditions(error_override)

        except :
            return lambda_func(event, context)

    return interceptor
