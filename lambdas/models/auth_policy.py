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
import re


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
    aws_account_id = ""
    principal_id = ""
    version = "2012-10-17"
    path_regex = r"^[/.a-zA-Z0-9-*]+$"
    allow_methods = []
    deny_methods = []

    restApiId = "<<restApiId>"
    region = os.getenv("AWS_DEFAULT_REGION", "eu-west-2")
    stage = "dev"

    def __init__(self, aws_account_id):
        self.aws_account_id = aws_account_id
        self.allow_methods = []
        self.deny_methods = []

    def _add_method(self, effect, verb, resource, conditions):
        """Adds a method to the internal lists of allowed or denied methods. Each object in
        the internal list contains a resource ARN and a condition statement. The condition
        statement can be null."""
        if verb != "*" and not hasattr(HttpVerb, verb):
            raise NameError(
                "Invalid HTTP verb " + verb + ". Allowed verbs in HttpVerb class"
            )
        resource_pattern = re.compile(self.path_regex)
        if not resource_pattern.match(resource):
            raise NameError(
                "Invalid resource path: "
                + resource
                + ". Path should match "
                + self.path_regex
            )

        if resource[:1] == "/":
            resource = resource[1:]

        resource_arn = (
            "arn:aws:execute-api:"
            + self.region
            + ":"
            + self.aws_account_id
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
            self.allow_methods.append(
                {"resourceArn": resource_arn, "conditions": conditions}
            )
        elif effect.lower() == "deny":
            self.deny_methods.append(
                {"resourceArn": resource_arn, "conditions": conditions}
            )

    def _get_empty_statement(self, effect):
        """Returns an empty statement object prepopulated with the correct action and the
        desired effect."""
        statement = {
            "Action": "execute-api:Invoke",
            "Effect": effect[:1].upper() + effect[1:].lower(),
            "Resource": [],
        }

        return statement

    def _get_statement_for_effect(self, effect, methods):
        """This function loops over an array of objects containing a resourceArn and
        conditions statement and generates the array of statements for the policy."""
        statements = []

        if len(methods) > 0:
            statement = self._get_empty_statement(effect)

            for cur_method in methods:
                if (
                    cur_method["conditions"] is None
                    or len(cur_method["conditions"]) == 0
                ):
                    statement["Resource"].append(cur_method["resourceArn"])
                else:
                    conditional_statement = self._get_empty_statement(effect)
                    conditional_statement["Resource"].append(cur_method["resourceArn"])
                    conditional_statement["Condition"] = cur_method["conditions"]
                    statements.append(conditional_statement)

            statements.append(statement)

        return statements

    def allow_all_methods(self):
        """Adds a '*' allow to the policy to authorize access to all methods of an API"""
        self._add_method("Allow", HttpVerb.ALL, "*", [])

    def deny_all_methods(self):
        """Adds a '*' allow to the policy to deny access to all methods of an API"""
        self._add_method("Deny", HttpVerb.ALL, "*", [])

    def allow_method(self, verb, resource):
        """Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods for the policy"""
        self._add_method("Allow", verb, resource, [])

    def deny_method(self, verb, resource):
        """Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods for the policy"""
        self._add_method("Deny", verb, resource, [])

    def build(self):
        """Generates the policy document based on the internal lists of allowed and denied
        conditions. This will generate a policy with two main statements for the effect:
        one statement for Allow and one statement for Deny.
        Methods that includes conditions will have their own statement in the policy."""
        if (self.allow_methods is None or len(self.allow_methods) == 0) and (
            self.deny_methods is None or len(self.deny_methods) == 0
        ):
            raise NameError("No statements defined for the policy")

        policy = {
            "principalId": self.principal_id,
            "policyDocument": {"Version": self.version, "Statement": []},
        }

        policy["policyDocument"]["Statement"].extend(
            self._get_statement_for_effect("Allow", self.allow_methods)
        )
        policy["policyDocument"]["Statement"].extend(
            self._get_statement_for_effect("Deny", self.deny_methods)
        )

        return policy
