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

import logging
import os
import re
import time

import boto3
import botocore.exceptions
import jwt
from boto3.dynamodb.conditions import Key

from enums.permitted_role import PermittedRole
from utils.exceptions import AuthorisationException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    user_roles = []
    ssm_public_key_parameter_name = os.environ["SSM_PARAM_JWT_TOKEN_PUBLIC_KEY"]

    try:
        client = boto3.client("ssm", region_name="eu-west-2")
        ssm_response = client.get_parameter(
            Name=ssm_public_key_parameter_name, WithDecryption=True
        )
        public_key = ssm_response["Parameter"]["Value"]

        decoded = jwt.decode(
            event["authorizationToken"], public_key, algorithms=["RS256"]
        )

        ndr_session_id = decoded["ndr_session_id"]

        logger.debug("Retrieving session for session ID ending in: " + ndr_session_id[-4:])

        # TODO: add this env var to terraform
        # TODO: switch to use the DynamoDBService from other branch once we merge with other branch
        session_table_name = os.environ["AUTH_SESSION_TABLE_NAME"]
        temp_dynamo_resource = boto3.resource("dynamodb")
        session_table = temp_dynamo_resource.Table(session_table_name)
        query_response = session_table.query(KeyConditionExpression=Key("NDRSessionId").eq(ndr_session_id))

        if "Count" not in query_response or query_response["Count"] == 0:
            raise AuthorisationException(f"Unable to find session for session ID ending in: {ndr_session_id[-4:]}")

        current_session = query_response['Items'][0]
        expiry_time = current_session['TimeToExist']
        time_now = time.time()
        if expiry_time <= time_now:
            raise AuthorisationException(f"The session is already expired for session ID ending in: {ndr_session_id[-4:]}")

        # if user has a valid session, assign their role
        user_roles = [org['role'] for org in decoded["organisations"]]

        logger.info(f"decoded JWT: {decoded}")
    except AuthorisationException as e:
        logger.error(e)
    except botocore.exceptions.ClientError as e:
        logger.error(e)
    except jwt.PyJWTError as e:
        logger.error(f"error while decoding JWT: {e}")
    except (KeyError, IndexError) as e:
        logger.error(e)

    principal_id = ""
    _, _, _, region, aws_account_id, api_gateway_arn = event["methodArn"].split(":")
    api_id, stage, http_verb, resource_name = api_gateway_arn.split("/")

    policy = AuthPolicy(principal_id, aws_account_id)
    policy.restApiId = api_id
    policy.region = region
    policy.stage = stage

    # for now, allow all method for GP and DEV role, and allow only search document for PCSE
    if PermittedRole.DEV.name in user_roles:
        policy.allowAllMethods()
    elif PermittedRole.GP.name in user_roles:
        policy.allowAllMethods()
    elif PermittedRole.PCSE.name in user_roles:
        policy.allowMethod(HttpVerb.GET, "/SearchDocumentReferences")
    else:
        policy.denyAllMethods()

    auth_response = policy.build()

    return auth_response


class HttpVerb:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    HEAD = "HEAD"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    ALL = "*"


class AuthPolicy(object):
    awsAccountId = ""
    principalId = ""
    version = "2012-10-17"
    pathRegex = r"^[/.a-zA-Z0-9-*]+$"
    allowMethods = []
    denyMethods = []

    restApiId = "<<restApiId>"
    region = "eu-west-2"
    stage = "dev"

    def __init__(self, principal, awsAccountId):
        self.awsAccountId = awsAccountId
        self.principalId = principal
        self.allowMethods = []
        self.denyMethods = []

    def _addMethod(self, effect, verb, resource, conditions):
        """Adds a method to the internal lists of allowed or denied methods. Each object in
        the internal list contains a resource ARN and a condition statement. The condition
        statement can be null."""
        if verb != "*" and not hasattr(HttpVerb, verb):
            raise NameError(
                "Invalid HTTP verb " + verb + ". Allowed verbs in HttpVerb class"
            )
        resourcePattern = re.compile(self.pathRegex)
        if not resourcePattern.match(resource):
            raise NameError(
                "Invalid resource path: "
                + resource
                + ". Path should match "
                + self.pathRegex
            )

        if resource[:1] == "/":
            resource = resource[1:]

        resourceArn = (
            "arn:aws:execute-api:"
            + self.region
            + ":"
            + self.awsAccountId
            + ":"
            + self.restApiId
            + "/"
            + self.stage
            + "/"
            + verb
            + "/"
            + resource
        )

        if effect.lower() == "allow":
            self.allowMethods.append(
                {"resourceArn": resourceArn, "conditions": conditions}
            )
        elif effect.lower() == "deny":
            self.denyMethods.append(
                {"resourceArn": resourceArn, "conditions": conditions}
            )

    def _getEmptyStatement(self, effect):
        """Returns an empty statement object prepopulated with the correct action and the
        desired effect."""
        statement = {
            "Action": "execute-api:Invoke",
            "Effect": effect[:1].upper() + effect[1:].lower(),
            "Resource": [],
        }

        return statement

    def _getStatementForEffect(self, effect, methods):
        """This function loops over an array of objects containing a resourceArn and
        conditions statement and generates the array of statements for the policy."""
        statements = []

        if len(methods) > 0:
            statement = self._getEmptyStatement(effect)

            for curMethod in methods:
                if curMethod["conditions"] is None or len(curMethod["conditions"]) == 0:
                    statement["Resource"].append(curMethod["resourceArn"])
                else:
                    conditionalStatement = self._getEmptyStatement(effect)
                    conditionalStatement["Resource"].append(curMethod["resourceArn"])
                    conditionalStatement["Condition"] = curMethod["conditions"]
                    statements.append(conditionalStatement)

            statements.append(statement)

        return statements

    def allowAllMethods(self):
        """Adds a '*' allow to the policy to authorize access to all methods of an API"""
        self._addMethod("Allow", HttpVerb.ALL, "*", [])

    def denyAllMethods(self):
        """Adds a '*' allow to the policy to deny access to all methods of an API"""
        self._addMethod("Deny", HttpVerb.ALL, "*", [])

    def allowMethod(self, verb, resource):
        """Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods for the policy"""
        self._addMethod("Allow", verb, resource, [])

    def denyMethod(self, verb, resource):
        """Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods for the policy"""
        self._addMethod("Deny", verb, resource, [])

    def build(self):
        """Generates the policy document based on the internal lists of allowed and denied
        conditions. This will generate a policy with two main statements for the effect:
        one statement for Allow and one statement for Deny.
        Methods that includes conditions will have their own statement in the policy."""
        if (self.allowMethods is None or len(self.allowMethods) == 0) and (
            self.denyMethods is None or len(self.denyMethods) == 0
        ):
            raise NameError("No statements defined for the policy")

        policy = {
            "principalId": self.principalId,
            "policyDocument": {"Version": self.version, "Statement": []},
        }

        policy["policyDocument"]["Statement"].extend(
            self._getStatementForEffect("Allow", self.allowMethods)
        )
        policy["policyDocument"]["Statement"].extend(
            self._getStatementForEffect("Deny", self.denyMethods)
        )

        return policy
