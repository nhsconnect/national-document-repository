# test_enums.py

from enums.lambda_error import LambdaError

ENV = "test"

# Common Table Name
TABLE_NAME = "CloudFrontEdgeReference"

# Common NHS Domain
NHS_DOMAIN = "example.gov.uk"

# Expected LambdaError values for tests
EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE = LambdaError.EdgeNoClient.value["message"]
EXPECTED_EDGE_NO_CLIENT_ERROR_CODE = LambdaError.EdgeNoClient.value["err_code"]

# Expected successful request/response parameters
EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION = (
    "attribute_not_exists(IsRequested) OR IsRequested = :false"
)
EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES = {":false": False}

# SSM parameter key for CloudFront Edge Reference
EXPECTED_SSM_PARAMETER_KEY = "EDGE_REFERENCE_TABLE"

# Expected success response from attempt_url_update
EXPECTED_SUCCESS_RESPONSE = None

# Mock event models for testing
VALID_EVENT_MODEL = {
    "Records": [
        {
            "cf": {
                "request": {
                    "headers": {
                        "authorization": [
                            {"key": "Authorization", "value": "Bearer token"}
                        ],
                        "host": [{"key": "Host", "value": NHS_DOMAIN}],
                    },
                    "querystring": f"origin=https://test.{NHS_DOMAIN}&other=param",
                    "uri": "/some/path",
                }
            }
        }
    ]
}

MISSING_ORIGIN_EVENT_MODEL = {
    "Records": [
        {
            "cf": {
                "request": {
                    "headers": {
                        "authorization": [
                            {"key": "Authorization", "value": "Bearer token"}
                        ],
                        "host": [{"key": "Host", "value": NHS_DOMAIN}],
                    },
                    "querystring": "other=param",
                    "uri": "/some/path",
                }
            }
        }
    ]
}
