from enums.lambda_error import LambdaError

MOCKED_ENV = "test"
MOCKED_DOMAIN = f"{MOCKED_ENV}-lloyd-test-test.com"

MOCKED_AUTH_QUERY = (
    "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date"
    "&X-Amz-Expires=3600&X-Amz-SignedHeaders=signed"
    "&X-Amz-Signature=sig&X-Amz-Security-Token=token"
)
MOCKED_PARTIAL_QUERY = (
    "X-Amz-Algorithm=algo&X-Amz-Credential=cred&X-Amz-Date=date" "&X-Amz-Expires=3600"
)

MOCKED_HEADERS = {
    "cloudfront-viewer-country": [{"key": "CloudFront-Viewer-Country", "value": "US"}],
    "x-forwarded-for": [{"key": "X-Forwarded-For", "value": "1.2.3.4"}],
    "host": [{"key": "Host", "value": MOCKED_DOMAIN}],
}

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


MOCK_S3_EDGE_EVENT = {
    "Records": [
        {
            "cf": {
                "request": {
                    "headers": MOCKED_HEADERS,
                    "querystring": MOCKED_AUTH_QUERY,
                    "uri": "/some/path",
                    "origin": {
                        "s3": {
                            "authMethod": "none",
                            "customHeaders": {},
                            "domainName": MOCKED_DOMAIN,
                            "path": "",
                        }
                    },
                }
            }
        }
    ]
}
