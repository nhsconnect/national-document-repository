from copy import deepcopy

MOCK_RESPONSE = {
    "Items": [
        {
            "FileName": "Screenshot 2023-08-16 at 15.26.11.png",
            "Created": "2023-08-23T00:38:04.103Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "GIF.gif",
            "Created": "2023-08-22T17:38:31.890Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "Screen Recording 2023-08-15 at 16.18.31.mov",
            "Created": "2023-08-23T00:38:04.095Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "screenshot guidance.png",
            "Created": "2023-08-22T23:39:27.178Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "Screenshot 2023-08-15 at 16.17.56.png",
            "Created": "2023-08-23T00:38:04.101Z",
            "VirusScannerResult": "Clean",
        },
    ],
    "Count": 5,
    "ScannedCount": 5,
}

MOCK_RESPONSE_WITH_LAST_KEY = deepcopy(MOCK_RESPONSE)
MOCK_RESPONSE_WITH_LAST_KEY.update(
    {"LastEvaluatedKey": {"FileName": "Screenshot 2023-08-15 at 16.17.56.png"}}
)

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
        "FileName": "Screenshot 2023-08-16 at 15.26.11.png",
        "Created": "2023-08-23T00:38:04.103Z",
        "VirusScannerResult": "Clean",
    },
    {
        "FileName": "GIF.gif",
        "Created": "2023-08-22T17:38:31.890Z",
        "VirusScannerResult": "Clean",
    },
    {
        "FileName": "Screen Recording 2023-08-15 at 16.18.31.mov",
        "Created": "2023-08-23T00:38:04.095Z",
        "VirusScannerResult": "Clean",
    },
    {
        "FileName": "screenshot guidance.png",
        "Created": "2023-08-22T23:39:27.178Z",
        "VirusScannerResult": "Clean",
    },
    {
        "FileName": "Screenshot 2023-08-15 at 16.17.56.png",
        "Created": "2023-08-23T00:38:04.101Z",
        "VirusScannerResult": "Clean",
    },
]

UNEXPECTED_RESPONSE = {
    "Sentences": [
        "commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nasce!",
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
