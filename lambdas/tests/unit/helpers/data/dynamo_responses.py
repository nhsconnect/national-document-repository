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
        "fileName": "Screenshot 2023-08-16 at 15.26.11.png",
        "created": "2023-08-23T00:38:04.103Z",
        "virusScannerResult": "Clean",
    },
    {
        "fileName": "GIF.gif",
        "created": "2023-08-22T17:38:31.890Z",
        "virusScannerResult": "Clean",
    },
    {
        "fileName": "Screen Recording 2023-08-15 at 16.18.31.mov",
        "created": "2023-08-23T00:38:04.095Z",
        "virusScannerResult": "Clean",
    },
    {
        "fileName": "screenshot guidance.png",
        "created": "2023-08-22T23:39:27.178Z",
        "virusScannerResult": "Clean",
    },
    {
        "fileName": "Screenshot 2023-08-15 at 16.17.56.png",
        "created": "2023-08-23T00:38:04.101Z",
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
