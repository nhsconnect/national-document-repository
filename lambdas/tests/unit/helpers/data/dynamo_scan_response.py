from copy import deepcopy

from utils.utilities import flatten

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

MOCK_PAGINATED_RESPONSE_1 = {
    "Items": [
        {
            "FileName": "1of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-23T00:38:04.103Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "3of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-22T17:38:31.890Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "5of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-23T00:38:04.095Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "7of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-23T00:38:04.095Z",
            "VirusScannerResult": "Clean",
        },
    ],
    "Count": 4,
    "ScannedCount": 4,
    "LastEvaluatedKey": {"ID": "id_token_for_page_2"},
}


MOCK_PAGINATED_RESPONSE_2 = {
    "Items": [
        {
            "FileName": "2of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-23T00:38:04.103Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "10of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-22T17:38:31.890Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "8of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-23T00:38:04.095Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "6of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-23T00:38:04.095Z",
            "VirusScannerResult": "Clean",
        },
    ],
    "Count": 4,
    "ScannedCount": 4,
    "LastEvaluatedKey": {"ID": "id_token_for_page_3"},
}

MOCK_PAGINATED_RESPONSE_3 = {
    "Items": [
        {
            "FileName": "9of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-23T00:38:04.103Z",
            "VirusScannerResult": "Clean",
        },
        {
            "FileName": "4of10_Lloyd_George_Record_[Jane Smith]_[9000000009]_[22-10-2010].pdf",
            "Created": "2023-08-22T17:38:31.890Z",
            "VirusScannerResult": "Clean",
        },
    ],
    "Count": 2,
    "ScannedCount": 2,
}

EXPECTED_ITEMS_FOR_PAGINATED_RESULTS = flatten(
    [
        response["Items"]
        for response in [
            MOCK_PAGINATED_RESPONSE_1,
            MOCK_PAGINATED_RESPONSE_2,
            MOCK_PAGINATED_RESPONSE_3,
        ]
    ]
)
