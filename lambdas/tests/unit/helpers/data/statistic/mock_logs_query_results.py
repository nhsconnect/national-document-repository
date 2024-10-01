USER_ID_1 = "F4A6AF98-4800-4A8A-A6C0-8FE0AC4B994B"
USER_ID_2 = "9E7F1235-3DF1-4822-AFFB-C4FCC88C2690"
HASHED_USER_ID_1 = "3192b6cf7ef953cf1a1f0945a83b55ab2cb8bae95cac6548ae5412aaa4c67677"
HASHED_USER_ID_2 = "a89d1cb4ac0776e45131c65a69e8b1a48026e9b497c94409e480588418a016e4"

MOCK_UNIQUE_ACTIVE_USER_IDS = [
    {
        "ods_code": "Y12345",
        "user_id": USER_ID_1,
    },
    {
        "ods_code": "H81109",
        "user_id": USER_ID_1,
    },
    {
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

MOCK_PATIENT_SEARCHED = [
    {
        "ods_code": "Y12345",
        "daily_count_searched": "50",
    },
    {
        "ods_code": "H81109",
        "daily_count_searched": "30",
    },
]

MOCK_USER_LOGIN = []

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
