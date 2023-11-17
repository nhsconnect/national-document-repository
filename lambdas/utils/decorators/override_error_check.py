from typing import Callable

import os
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

            # fail fast if workspace is invalid 
            if workspace == None or workspace in disabled_workspaces:
                return lambda_func(event, context)
            
            # fail fast if error trigger is not set
            if error_override is None or error_override == "":
                return lambda_func(event, context)
                
            check_manual_error_conditions(error_override)

        except :
            return lambda_func(event, context)

    return interceptor
