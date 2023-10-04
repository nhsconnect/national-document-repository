from tests.unit.conftest import TEST_NHS_NUMBER

MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {
        "identifier": {
            "value": TEST_NHS_NUMBER
        }
    },
    "content": [
        {
            "attachment": [
                {
                    "fileName": "test1.txt",
                    "contentType": "text/plain",
                    "docType": "ARF"
                },
                {
                    "fileName": "test2.txt",
                    "contentType": "text/plain",
                    "docType": "ARF"
                },
                {
                    "fileName": "test3.txt",
                    "contentType": "text/plain",
                    "docType": "ARF"
                },
                {
                    "fileName": "1of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG"
                },
                {
                    "fileName": "2of3_Lloyd_George_Record_[Joe Test]_[1254563891]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG"
                },
                {
                    "fileName": "3of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG"
                },
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z"
}

LG_MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {
        "identifier": {
            "value": TEST_NHS_NUMBER
        }
    },
    "content": [
        {
            "attachment": [
                {
                    "fileName": "1of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG"
                },
                {
                    "fileName": "2of3_Lloyd_George_Record_[Joe Test]_[1254563891]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG"
                },
                {
                    "fileName": "3of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
                    "contentType": "application/pdf",
                    "docType": "LG"
                },
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z"
}

ARF_MOCK_EVENT_BODY = {
    "resourceType": "DocumentReference",
    "subject": {
        "identifier": {
            "value": TEST_NHS_NUMBER
        }
    },
    "content": [
        {
            "attachment": [
                {
                    "fileName": "test1.txt",
                    "contentType": "text/plain",
                    "docType": "ARF"
                },
                {
                    "fileName": "test2.txt",
                    "contentType": "text/plain",
                    "docType": "ARF"
                },
                {
                    "fileName": "test3.txt",
                    "contentType": "text/plain",
                    "docType": "ARF"
                },
            ]
        }
    ],
    "created": "2023-10-02T15:55:30.650Z"
}

MOCK_PRESIGNED_POST_RESPONSE = {
    "url": "https://ndr-dev-document-store.s3.amazonaws.com/",
    "fields": {
        "key": "0abed67c-0d0b-4a11-a600-a2f19ee61281",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "ASIAXYSUA44VTL5M5LWL/20230911/eu-west-2/s3/aws4_request",
        "x-amz-date": "20230911T084756Z",
        "x-amz-security-token": "test-security-token",
        "policy": "test-policy",
        "x-amz-signature": "b6afcf8b27fc883b0e0a25a789dd2ab272ea4c605a8c68267f73641d7471132f",
    },
}

LG_AND_ARF_MOCK_RESPONSE = {
    "test1.txt": MOCK_PRESIGNED_POST_RESPONSE,
    "test2.txt": MOCK_PRESIGNED_POST_RESPONSE,
    "test3.txt": MOCK_PRESIGNED_POST_RESPONSE,
    "1of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf": MOCK_PRESIGNED_POST_RESPONSE,
    "2of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf": MOCK_PRESIGNED_POST_RESPONSE,
    "3of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf": MOCK_PRESIGNED_POST_RESPONSE
}

ARF_MOCK_RESPONSE = {
    "test1.txt": MOCK_PRESIGNED_POST_RESPONSE,
    "test2.txt": MOCK_PRESIGNED_POST_RESPONSE,
    "test3.txt": MOCK_PRESIGNED_POST_RESPONSE
}

LG_MOCK_RESPONSE = {
    "1of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf": MOCK_PRESIGNED_POST_RESPONSE,
    "2of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf": MOCK_PRESIGNED_POST_RESPONSE,
    "3of3_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf": MOCK_PRESIGNED_POST_RESPONSE
}
