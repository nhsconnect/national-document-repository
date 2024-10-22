from enums.lambda_error import LambdaError

ENV = "test"
EXPECTED_ENVIRONMENT = ENV

TABLE_NAME = "CloudFrontEdgeReference"
NHS_DOMAIN = "example.gov.uk"

EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE = LambdaError.EdgeNoClient.value["message"]
EXPECTED_EDGE_NO_CLIENT_ERROR_CODE = LambdaError.EdgeNoClient.value["err_code"]
EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE = LambdaError.EdgeMalformed.value["message"]
EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE = LambdaError.EdgeMalformed.value["err_code"]

EXPECTED_DYNAMO_DB_CONDITION_EXPRESSION = (
    "attribute_not_exists(IsRequested) OR IsRequested = :false"
)
EXPECTED_DYNAMO_DB_EXPRESSION_ATTRIBUTE_VALUES = {":false": False}

EXPECTED_SSM_PARAMETER_KEY = "EDGE_REFERENCE_TABLE"

EXPECTED_SUCCESS_RESPONSE = None

VALID_DOMAIN = "test-lloyd-test-test.s3.eu-west-2.amazonaws.com"
EXPECTED_DOMAIN = VALID_DOMAIN

INVALID_DOMAIN = "invalid-domain.com"
FORMATTED_TABLE_NAME = f"{EXPECTED_ENVIRONMENT}_{TABLE_NAME}"

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
                    "querystring": "x-amz=11111",
                    "uri": "/some/path",
                    "origin": {
                        "s3": {
                            "authMethod": "none",
                            "customHeaders": {},
                            "domainName": VALID_DOMAIN,
                            "path": "",
                        }
                    },
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
