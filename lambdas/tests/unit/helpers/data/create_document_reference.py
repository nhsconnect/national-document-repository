from tests.unit.conftest import TEST_NHS_NUMBER
from tests.unit.helpers.data.s3_responses import MOCK_PRESIGNED_URL_RESPONSE

MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": TEST_NHS_NUMBER}},
    "content": [
        {
            "attachment": [
                {
                    "fileName": "test1.txt",
                    "contentType": "text/plain",
                    "docType": "ARF",
                },
                {
                    "fileName": "test2.txt",
                    "contentType": "text/plain",
                    "docType": "ARF",
                },
                {
                    "fileName": "test3.txt",
                    "contentType": "text/plain",
                    "docType": "ARF",
                },
                {
                    "fileName": f"1of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG",
                },
                {
                    "fileName": f"2of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG",
                },
                {
                    "fileName": f"3of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG",
                },
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z",
}
LG_FILE_LIST = [
    {
        "fileName": f"1of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
        "contentType": "application/pdf",
        "docType": "LG",
    },
    {
        "fileName": f"2of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
        "contentType": "application/pdf",
        "docType": "LG",
    },
    {
        "fileName": f"3of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
        "contentType": "application/pdf",
        "docType": "LG",
    },
]

LG_MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": TEST_NHS_NUMBER}},
    "content": [{"attachment": LG_FILE_LIST}],
    "created": "2023-10-02T15:55:30.650Z",
}

LG_MOCK_BAD_FILE_TYPE_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": TEST_NHS_NUMBER}},
    "content": [
        {
            "attachment": [
                {
                    "fileName": f"1of1_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "text/plain",
                    "docType": "LG",
                }
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z",
    "httpMethod": "POST",
}

LG_MOCK_BAD_FILE_NAME_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": TEST_NHS_NUMBER}},
    "content": [
        {
            "attachment": [
                {
                    "fileName": f"1of1_BAD_NAME_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG",
                }
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z",
    "httpMethod": "POST",
}

LG_MOCK_MISSING_FILES_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": TEST_NHS_NUMBER}},
    "content": [
        {
            "attachment": [
                {
                    "fileName": f"1of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG",
                }
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z",
    "httpMethod": "POST",
}

LG_MOCK_DUPLICATE_FILES_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": TEST_NHS_NUMBER}},
    "content": [
        {
            "attachment": [
                {
                    "fileName": f"1of2_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG",
                },
                {
                    "fileName": f"1of2_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG",
                },
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z",
    "httpMethod": "POST",
}
ARF_FILE_LIST = [
    {
        "fileName": "test1.txt",
        "contentType": "text/plain",
        "docType": "ARF",
    },
    {
        "fileName": "test2.txt",
        "contentType": "text/plain",
        "docType": "ARF",
    },
    {
        "fileName": "test3.txt",
        "contentType": "text/plain",
        "docType": "ARF",
    },
]

ARF_MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {"identifier": {"value": TEST_NHS_NUMBER}},
    "content": [{"attachment": ARF_FILE_LIST}],
    "created": "2023-10-02T15:55:30.650Z",
}

LG_AND_ARF_MOCK_RESPONSE = {
    "test1.txt": MOCK_PRESIGNED_URL_RESPONSE,
    "test2.txt": MOCK_PRESIGNED_URL_RESPONSE,
    "test3.txt": MOCK_PRESIGNED_URL_RESPONSE,
    f"1of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf": MOCK_PRESIGNED_URL_RESPONSE,
    f"2of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf": MOCK_PRESIGNED_URL_RESPONSE,
    f"3of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf": MOCK_PRESIGNED_URL_RESPONSE,
}

ARF_MOCK_RESPONSE = {
    "test1.txt": MOCK_PRESIGNED_URL_RESPONSE,
    "test2.txt": MOCK_PRESIGNED_URL_RESPONSE,
    "test3.txt": MOCK_PRESIGNED_URL_RESPONSE,
}

LG_MOCK_RESPONSE = {
    f"1of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf": MOCK_PRESIGNED_URL_RESPONSE,
    f"2of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf": MOCK_PRESIGNED_URL_RESPONSE,
    f"3of3_Lloyd_George_Record_[Joe Bloggs]_[{TEST_NHS_NUMBER}]_[25-12-2019].pdf": MOCK_PRESIGNED_URL_RESPONSE,
}
