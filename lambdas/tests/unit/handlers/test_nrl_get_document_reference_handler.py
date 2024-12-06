from unit.conftest import FAKE_URL, TEST_UUID
from unit.services.test_authoriser_service import MOCK_SESSION_ID

MOCK_VALID_EVENT = {
    "resource": "/DocumentReference/{id}",
    "path": "/DocumentReference/2",
    "httpMethod": "GET",
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": f"Bearer {TEST_UUID}",
        "Cache-Control": "no-cache",
        "Host": FAKE_URL,
        "NHSD-Correlation-ID": TEST_UUID,
        "NHSD-ID-Token": f"MOCK_JWT{TEST_UUID}",
        "NHSD-Request-ID": "",
        "NHSD-Session-URID": MOCK_SESSION_ID,
        "NHSD-Session-UUID": MOCK_SESSION_ID,
        "Postman-Token": TEST_UUID,
        "User-Agent": "PostmanRuntime",
        "X-Amzn-Trace-Id": f"Root={TEST_UUID}",
        "X-API-Key": TEST_UUID,
        "X-Forwarded-For": "num",
        "X-Forwarded-Port": "port",
        "X-Forwarded-Proto": "https",
    },
    "multiValueHeaders": {
        "Accept": ["*/*"],
        "Accept-Encoding": ["gzip, deflate, br"],
        "Authorization": [f"Bearer {TEST_UUID}"],
        "Cache-Control": ["no-cache"],
        "Host": [FAKE_URL],
        "NHSD-Correlation-ID": [TEST_UUID],
        "NHSD-ID-Token": [f"MOCK_JWT{TEST_UUID}"],
        "NHSD-Request-ID": [""],
        "NHSD-Session-URID": [MOCK_SESSION_ID],
        "NHSD-Session-UUID": [MOCK_SESSION_ID],
        "Postman-Token": [TEST_UUID],
        "User-Agent": ["PostmanRuntime"],
        "X-Amzn-Trace-Id": [f"Root={TEST_UUID}"],
        "X-API-Key": [TEST_UUID],
        "X-Forwarded-For": ["num"],
        "X-Forwarded-Port": ["num"],
        "X-Forwarded-Proto": ["https"],
    },
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": {"id": TEST_UUID},
    "stageVariables": None,
    "requestContext": {
        "resourceId": TEST_UUID,
        "resourcePath": "/DocumentReference/{id}",
        "httpMethod": "GET",
        "extendedRequestId": "",
        "requestTime": "05/Dec/2024:15:36:37 +0000",
        "path": f"/DocumentReference/{TEST_UUID}",
        "accountId": TEST_UUID,
        "protocol": "HTTP/1.1",
        "stage": "dev",
        "domainPrefix": "ndr-",
        "requestTimeEpoch": 1733412997840,
        "requestId": TEST_UUID,
        "identity": {
            "cognitoIdentityPoolId": None,
            "cognitoIdentityId": None,
            "apiKey": TEST_UUID,
            "principalOrgId": None,
            "cognitoAuthenticationType": None,
            "userArn": None,
            "apiKeyId": TEST_UUID,
            "userAgent": "PostmanRuntime",
            "accountId": None,
            "caller": None,
            "sourceIp": "IP",
            "accessKey": None,
            "cognitoAuthenticationProvider": None,
            "user": None,
        },
        "domainName": FAKE_URL,
        "deploymentId": "????",
        "apiId": TEST_UUID,
    },
    "body": None,
    "isBase64Encoded": False,
}
