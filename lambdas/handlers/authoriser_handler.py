"""
This code has been modified from AWS blueprint. Below is the original license:
Copyright 2015-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License. A copy of the License is located at
     http://aws.amazon.com/apache2.0/
or in the "license" file accompanying this file.
This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os

from botocore.exceptions import ClientError
from enums.logging_app_interaction import LoggingAppInteraction
from models.auth_policy import AuthPolicy
from services.authoriser_service import AuthoriserService
from utils.audit_logging_setup import LoggingService
from utils.decorators.ensure_env_var import ensure_environment_variables
from utils.decorators.override_error_check import override_error_check
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.exceptions import AuthorisationException
from utils.request_context import request_context

logger = LoggingService(__name__)


@set_request_context_for_logging
@ensure_environment_variables(names=["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"])
@override_error_check
def lambda_handler(event, context):
    request_context.app_interaction = LoggingAppInteraction.LOGIN.value
    logger.info("Authoriser handler triggered")

    authoriser_service = AuthoriserService()

    ssm_jwt_public_key_parameter = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]
    auth_token = event.get("authorizationToken")
    if event.get("methodArn") is None:
        return {"Error": "methodArn is not defined"}
    _, _, _, region, aws_account_id, api_gateway_arn = event.get("methodArn").split(":")
    api_id, stage, _http_verb, _resource_name = api_gateway_arn.split("/")
    path = "/" + _resource_name

    policy = AuthPolicy(aws_account_id)
    policy.restApiId = api_id
    policy.region = region
    policy.stage = stage
    try:
        logger.info("Validating resource req: %s, http: %s" % (path, _http_verb))
        is_allow_policy = authoriser_service.auth_request(
            path, ssm_jwt_public_key_parameter, auth_token
        )
        if is_allow_policy:
            policy.allow_method(_http_verb, path)
        else:
            policy.deny_method(_http_verb, path)

    except (AuthorisationException, ClientError) as e:
        logger.error(str(e), {"Result": "Failed to authenticate user"})
        policy.deny_all_methods()

    auth_response = policy.build()
    return auth_response
