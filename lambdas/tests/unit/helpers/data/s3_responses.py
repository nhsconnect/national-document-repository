MOCK_PRESIGNED_URL_RESPONSE = {
    "url": "https://ndr-dev-document-store.s3.amazonaws.com/",
    "fields": {
        "key": "0abed67c-0d0b-4a11-a600-a2f19ee61281",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "ASIAXYSUA44VTL5M5LWL/20230911/eu-west-2/s3/aws4_request",
        "x-amz-date": "20230911T084756Z",
        "x-amz-expires": "1800",
        "x-amz-signed-headers": "test-host",
        "x-amz-signature": "test-signature",
    },
}

MOCK_LIST_OBJECTS_RESPONSE = {
    "ResponseMetadata": {
        "RequestId": "abc",
        "HostId": "xyz",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amz-id-2": "efg",
            "x-amz-request-id": "HIJ",
            "date": "Wed, 04 Jun 2024 13:49:45 GMT",
            "x-amz-bucket-region": "eu-west-2",
            "content-type": "application/xml",
            "transfer-encoding": "chunked",
            "server": "AmazonS3",
        },
        "RetryAttempts": 0,
    },
    "IsTruncated": False,
    "Contents": [
        {
            "Key": "9000000009/2985a5dd-37ac-481a-b847-ee09e4b0817b",
            "ETag": '"ddeafe0237ac7cb097c9a34c0e21a8a9"',
            "Size": 928,
            "StorageClass": "STANDARD",
        },
        {
            "Key": "9000000009/384b886d-bd86-4211-9f43-73f7146fbb9b",
            "ETag": '"ddeafe0237ac7cb097c9a34c0e21a8a9"',
            "Size": 928,
            "StorageClass": "STANDARD",
        },
    ],
    "Name": "test-lg-bucket",
    "Prefix": "",
    "MaxKeys": 1000,
    "EncodingType": "url",
    "KeyCount": 2,
}


MOCK_LIST_OBJECTS_PAGINATED_RESPONSES = [
    {
        "IsTruncated": True,
        "Contents": [
            {
                "Key": "9000000009/2985a5dd-37ac-481a-b847-ee09e4b0817b",
                "Size": 928,
                "StorageClass": "STANDARD",
            },
            {
                "Key": "9000000009/384b886d-bd86-4211-9f43-73f7146fbb9b",
                "Size": 928,
                "StorageClass": "STANDARD",
            },
        ],
    },
    {
        "IsTruncated": True,
        "Contents": [
            {
                "Key": "9000000009/94c93a0c-a322-4eaa-ad0b-29ea876c33a5",
                "Size": 928,
                "StorageClass": "STANDARD",
            },
            {
                "Key": "9000000009/36af7807-7965-4c17-b2eb-0f2ae903196d",
                "Size": 928,
                "StorageClass": "STANDARD",
            },
        ],
    },
]
