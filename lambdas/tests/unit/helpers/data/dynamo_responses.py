MOCK_SEARCH_RESPONSE = {
    "Items": [
        {
            "ID": "3d8683b9-1665-40d2-8499-6e8302d507ff",
            "ContentType": "type",
            "Created": "2023-08-23T13:38:04.095Z",
            "Deleted": "",
            "FileLocation": "s3://test_s3_bucket/test-key-123",
            "FileName": "document.csv",
            "NhsNumber": "9000000009",
            "VirusScannerResult": "Clean",
            "TTL": "",
        },
        {
            "ID": "4d8683b9-1665-40d2-8499-6e8302d507ff",
            "ContentType": "type",
            "Created": "2023-08-23T13:38:04.095Z",
            "Deleted": "",
            "FileLocation": "s3://test_s3_bucket/test-key-223",
            "FileName": "results.pdf",
            "NhsNumber": "9000000009",
            "VirusScannerResult": "Clean",
            "TTL": "",
        },
        {
            "ID": "5d8683b9-1665-40d2-8499-6e8302d507ff",
            "ContentType": "type",
            "Created": "2023-08-24T14:38:04.095Z",
            "Deleted": "",
            "FileLocation": "s3://test_s3_bucket/test-key-323",
            "FileName": "output.csv",
            "NhsNumber": "9000000009",
            "VirusScannerResult": "Clean",
            "TTL": "",
        },
    ],
    "Count": 3,
    "ScannedCount": 3,
    "ResponseMetadata": {
        "RequestId": "VNS38QDVQCIQ1EMGKQ1EA2E5MVVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "server": "Server",
            "date": "Thu, 07 Sep 2023 11:14:01 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "583",
            "connection": "keep-alive",
            "x-amzn-requestid": "VNS38QDVQCIQ1EMGKQ1EA2E5MVVV4KQNSO5AEMVJF66Q9ASUAAJG",
            "x-amz-crc32": "2636774765",
        },
        "RetryAttempts": 0,
    },
}

MOCK_EMPTY_RESPONSE = {
    "Items": [],
    "Count": 0,
    "ScannedCount": 0,
    "ResponseMetadata": {
        "RequestId": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "server": "Server",
            "date": "Tue, 29 Aug 2023 11:08:21 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "510",
            "connection": "keep-alive",
            "x-amzn-requestid": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
            "x-amz-crc32": "820258331",
        },
        "RetryAttempts": 0,
    },
}

EXPECTED_RESPONSE = [
    {
        "created": "2023-08-23T13:38:04.095Z",
        "fileName": "document.csv",
        "virusScannerResult": "Clean",
    },
    {
        "created": "2023-08-23T13:38:04.095Z",
        "fileName": "results.pdf",
        "virusScannerResult": "Clean",
    },
    {
        "created": "2023-08-24T14:38:04.095Z",
        "fileName": "output.csv",
        "virusScannerResult": "Clean",
    },
]

UNEXPECTED_RESPONSE = {
    "Sentences": [
        "Gerbil took the top head!",
        "Jumble grand. Up and loose and heavy treats sandwich.",
        "Hotly! Dirt arrange you.",
        "School bearing, boy boy. I's many cauterizing loops through and about. Wind and windy, Mitchell.",
        "Spider Time!",
        "Lady, you are school and dirt for loosing.",
    ],
    "Count": 6,
    "ScannedCount": 6,
    "ResponseMetadata": {
        "RequestId": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "server": "Server",
            "date": "Tue, 29 Aug 2023 11:08:21 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "510",
            "connection": "keep-alive",
            "x-amzn-requestid": "JHJBP4GU007VMB2V8C9NEKUL8VVV4KQNSO5AEMVJF66Q9ASUAAJG",
            "x-amz-crc32": "820258331",
        },
        "RetryAttempts": 0,
    },
}
