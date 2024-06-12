import math
import random
import uuid
from typing import Tuple

PDF_MIME_TYPE = "application/pdf"


def build_mock_results(
    ods_code: str,
    nhs_number: str,
    number_of_files: int = 3,
    total_file_size_in_mb: int = 5,
) -> Tuple[list[dict], list[dict]]:
    file_ids = [uuid.uuid4() for _ in range(number_of_files)]
    file_size_randoms = [random.randint(1, 10) for _ in range(number_of_files)]
    total_file_size = total_file_size_in_mb * 1024 * 1024
    file_sizes = [
        math.floor(x * total_file_size / sum(file_size_randoms))
        for x in file_size_randoms
    ]
    file_sizes[-1] = total_file_size - sum(file_sizes[:-1])

    dynamodb_scan_result = [
        {
            "CurrentGpOds": ods_code,
            "ContentType": PDF_MIME_TYPE,
            "FileLocation": f"s3://test-lg-table/{nhs_number}/{file_id}",
            "NhsNumber": nhs_number,
        }
        for file_id in file_ids
    ]

    s3_list_objects_result = [
        {
            "Key": f"{nhs_number}/{file_ids[index]}",
            "Size": file_sizes[index],
        }
        for index in range(number_of_files)
    ]

    return dynamodb_scan_result, s3_list_objects_result


MOCK_LG_SCAN_RESULT = [
    {
        "CurrentGpOds": "H81109",
        "ContentType": PDF_MIME_TYPE,
        "FileLocation": "s3://test-lg-table/9000000009/4ac21f7b-abd6-46c9-bf55-e7bafccba2ab",
        "NhsNumber": "9000000009",
    },
    {
        "CurrentGpOds": "H81109",
        "ContentType": PDF_MIME_TYPE,
        "FileLocation": "s3://test-lg-table/9000000009/95764e53-b5fd-47b8-8756-1c5604121444",
        "NhsNumber": "9000000009",
    },
    {
        "CurrentGpOds": "H81109",
        "ContentType": PDF_MIME_TYPE,
        "FileLocation": "s3://test-lg-table/9000000009/0ab18243-783a-4044-8146-b5b0996d8422",
        "NhsNumber": "9000000009",
    },
    {
        "CurrentGpOds": "H81109",
        "ContentType": PDF_MIME_TYPE,
        "FileLocation": "s3://test-lg-table/9000000001/5d5b3c28-e6c8-4d46-8ae3-a2b97321bcf8",
        "NhsNumber": "9000000001",
    },
    {
        "CurrentGpOds": "H81109",
        "ContentType": PDF_MIME_TYPE,
        "FileLocation": "s3://test-lg-table/9000000001/2543ba87-dcdb-4583-bae2-e83c4ba7af34",
        "NhsNumber": "9000000001",
    },
]

MOCK_ARF_SCAN_RESULT = [
    {
        "CurrentGpOds": "Y12345",
        "ContentType": "application/msword",
        "FileLocation": "s3://test-arf-table/9000000005/beec3523-1428-4c5f-b718-6ef25a4db1b9",
        "NhsNumber": "9000000005",
    },
    {
        "CurrentGpOds": "Y12345",
        "ContentType": "image/jpeg",
        "FileLocation": "s3://test-arf-table/9000000005/d2cf885b-9e78-4c29-bf5a-2a56e5e0df8f",
        "NhsNumber": "9000000005",
    },
    {
        "CurrentGpOds": "H81109",
        "ContentType": "image/bmp",
        "FileLocation": "s3://test-arf-table/9000000009/71e0c54e-5cfc-4260-a538-09eab185a6ed",
        "NhsNumber": "9000000009",
    },
]

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
