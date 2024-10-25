from enums.lambda_error import LambdaError

ENV = "test"
EXPECTED_ENVIRONMENT = ENV

TABLE_NAME = "CloudFrontEdgeReference"
NHS_DOMAIN = "example.gov.uk"
S3_DOMAIN = "example.gov.uk"


EXPECTED_EDGE_NO_QUERY_MESSAGE = LambdaError.EdgeNoQuery.value["message"]
EXPECTED_EDGE_NO_QUERY_ERROR_CODE = LambdaError.EdgeNoQuery.value["err_code"]
EXPECTED_EDGE_MALFORMED_QUERY_MESSAGE = LambdaError.EdgeRequiredQuery.value["message"]
EXPECTED_EDGE_MALFORMED_QUERY_ERROR_CODE = LambdaError.EdgeRequiredQuery.value[
    "err_code"
]
EXPECTED_EDGE_MALFORMED_HEADER_MESSAGE = LambdaError.EdgeRequiredHeaders.value[
    "message"
]
EXPECTED_EDGE_MALFORMED_HEADER_ERROR_CODE = LambdaError.EdgeRequiredHeaders.value[
    "err_code"
]
EXPECTED_EDGE_NO_ORIGIN_ERROR_MESSAGE = LambdaError.EdgeNoOrigin.value["message"]
EXPECTED_EDGE_NO_ORIGIN_ERROR_CODE = LambdaError.EdgeNoOrigin.value["err_code"]

EXPECTED_EDGE_NO_CLIENT_ERROR_MESSAGE = LambdaError.EdgeNoClient.value["message"]
EXPECTED_EDGE_NO_CLIENT_ERROR_CODE = LambdaError.EdgeNoClient.value["err_code"]
EXPECTED_EDGE_MALFORMED_ERROR_MESSAGE = LambdaError.EdgeMalformed.value["message"]
EXPECTED_EDGE_MALFORMED_ERROR_CODE = LambdaError.EdgeMalformed.value["err_code"]

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
                        "host": [{"key": "Host", "value": S3_DOMAIN}],
                    },
                    "querystring": "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date"
                    "&X-Amz-Expires=3600&X-Amz-SignedHeaders=signed"
                    "&X-Amz-Signature=sig&X-Amz-Security-Token=token",
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
