import json

from tests.unit.conftest import TEST_FILE_KEY, TEST_NHS_NUMBER

MOCK_VALID_LG_EVENT_BODY = {
    "patientId": TEST_NHS_NUMBER,
    "documents": {"LG": [TEST_FILE_KEY]},
}
MOCK_VALID_LG_EVENT = {"body": json.dumps(MOCK_VALID_LG_EVENT_BODY)}

MOCK_VALID_ARF_EVENT_BODY = {
    "patientId": TEST_NHS_NUMBER,
    "documents": {"ARF": [TEST_FILE_KEY, TEST_FILE_KEY]},
}
MOCK_VALID_ARF_EVENT = {
    "httpMethod": "POST",
    "body": json.dumps(MOCK_VALID_ARF_EVENT_BODY),
}

MOCK_MISSING_NHS_NUMBER_BODY = {"documents": {"ARF": [TEST_FILE_KEY, TEST_FILE_KEY]}}
MOCK_MISSING_NHS_NUMBER_EVENT = {
    "httpMethod": "POST",
    "body": json.dumps(MOCK_MISSING_NHS_NUMBER_BODY),
}

MOCK_INVALID_NHS_NUMBER_BODY = {
    "patientId": "900000000040",
    "documents": {"ARF": [TEST_FILE_KEY, TEST_FILE_KEY]},
}
MOCK_INVALID_NHS_NUMBER_EVENT = {
    "httpMethod": "POST",
    "body": json.dumps(MOCK_INVALID_NHS_NUMBER_BODY),
}

MOCK_MISSING_DOCUMENTS_BODY = {"patientId": TEST_NHS_NUMBER}
MOCK_MISSING_DOCUMENTS_EVENT = {
    "httpMethod": "POST",
    "body": json.dumps(MOCK_MISSING_DOCUMENTS_BODY),
}

MOCK_MISSING_BODY_EVENT = {"httpMethod": "POST", "body": "test"}
