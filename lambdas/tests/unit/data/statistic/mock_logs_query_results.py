import hashlib

USER_ID_1 = "F4A6AF98-4800-4A8A-A6C0-8FE0AC4B994B"
USER_ID_2 = "9E7F1235-3DF1-4822-AFFB-C4FCC88C2690"
HASHED_USER_ID_1 = hashlib.md5(bytes(USER_ID_1, "utf8")).hexdigest()
HASHED_USER_ID_2 = hashlib.md5(bytes(USER_ID_2, "utf8")).hexdigest()

MOCK_UNIQUE_ACTIVE_USER_IDS = [
    {
        "@timestamp": "2024-06-04 09:17:25.245",
        "ods_code": "Y12345",
        "user_id": USER_ID_1,
    },
    {
        "@timestamp": "2024-06-04 11:17:25.245",
        "ods_code": "H81109",
        "user_id": USER_ID_1,
    },
    {
        "@timestamp": "2024-06-04 13:17:25.245",
        "ods_code": "H81109",
        "user_id": USER_ID_2,
    },
]


MOCK_LG_VIEWED = [
    {
        "ods_code": "Y12345",
        "daily_count_viewed": "20",
    },
    {
        "ods_code": "H81109",
        "daily_count_viewed": "40",
    },
]

MOCK_LG_DOWNLOADED = [
    {
        "ods_code": "Y12345",
        "daily_count_downloaded": "10",
    },
    {
        "ods_code": "H81109",
        "daily_count_downloaded": "20",
    },
]

MOCK_LG_DELETED = [
    {
        "ods_code": "Y12345",
        "daily_count_deleted": "1",
    },
    {
        "ods_code": "H81109",
        "daily_count_deleted": "2",
    },
]

MOCK_LG_STORED = [
    {
        "ods_code": "Y12345",
        "daily_count_stored": "2",
    },
    {
        "ods_code": "H81109",
        "daily_count_stored": "4",
    },
]

MOCK_RESPONSE_QUERY_IN_PROGRESS = {"status": "Running"}

MOCK_RESPONSE_QUERY_FAILED = {"status": "Failed"}

MOCK_RESPONSE_QUERY_COMPLETE = {
    "results": [
        [
            {"field": "ods_code", "value": "Y12345"},
            {"field": "daily_count_viewed", "value": "20"},
        ],
        [
            {"field": "ods_code", "value": "H81109"},
            {"field": "daily_count_viewed", "value": "40"},
        ],
    ],
    "statistics": {
        "recordsMatched": 123.0,
        "recordsScanned": 123.0,
        "bytesScanned": 123.0,
    },
    "status": "Complete",
}

EXPECTED_QUERY_RESULT = [
    {
        "ods_code": "Y12345",
        "daily_count_viewed": "20",
    },
    {
        "ods_code": "H81109",
        "daily_count_viewed": "40",
    },
]
