MB = 1024 * 1024

MOCK_LG_LIST_OBJECTS_RESULT = [
    {"Key": "9000000009/4ac21f7b-abd6-46c9-bf55-e7bafccba2ab", "Size": 1 * MB},
    {"Key": "9000000009/95764e53-b5fd-47b8-8756-1c5604121444", "Size": 2 * MB},
    {"Key": "9000000009/0ab18243-783a-4044-8146-b5b0996d8422", "Size": 3 * MB},
    {"Key": "9000000001/5d5b3c28-e6c8-4d46-8ae3-a2b97321bcf8", "Size": 4 * MB},
    {"Key": "9000000001/2543ba87-dcdb-4583-bae2-e83c4ba7af34", "Size": 5 * MB},
]

MOCK_ARF_LIST_OBJECTS_RESULT = [
    {
        "Key": "9000000005/beec3523-1428-4c5f-b718-6ef25a4db1b9",
        "Size": 1 * MB,
    },
    {
        "Key": "9000000005/d2cf885b-9e78-4c29-bf5a-2a56e5e0df8f",
        "Size": 2 * MB,
    },
    {
        "Key": "9000000009/71e0c54e-5cfc-4260-a538-09eab185a6ed",
        "Size": 6 * MB,
    },
]

TOTAL_FILE_SIZE_FOR_9000000001 = 4 + 5
TOTAL_FILE_SIZE_FOR_9000000009 = 1 + 2 + 3 + 6
TOTAL_FILE_SIZE_FOR_9000000005 = 1 + 2
TOTAL_FILE_SIZE_FOR_H81109 = (
    TOTAL_FILE_SIZE_FOR_9000000001 + TOTAL_FILE_SIZE_FOR_9000000009
)
TOTAL_FILE_SIZE_FOR_Y12345 = TOTAL_FILE_SIZE_FOR_9000000005
