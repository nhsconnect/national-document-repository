# test_enums.py

from enums.lambda_error import LambdaError

ENV = "test"

TABLE_NAME = "CloudFrontEdgeReference"

NHS_DOMAIN = "example.gov.uk"

EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE = LambdaError.EdgeNoClient.value["message"]

EXPECTED_EDGE_NO_CLIENT_ERROR_CODE = LambdaError.EdgeNoClient.value["err_code"]

EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION = (
    "attribute_not_exists(IsRequested) OR IsRequested = :false"
)
EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES = {":false": False}

EXPECTED_SSM_PARAMETER_KEY = "EDGE_REFERENCE_TABLE"

EXPECTED_SUCCESS_RESPONSE = None

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
