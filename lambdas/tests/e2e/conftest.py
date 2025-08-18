import os
import random
import time

import pytest
import requests
from tests.e2e.helpers.lloyd_george_data_helper import LloydGeorgeDataHelper

data_helper = LloydGeorgeDataHelper()

LLOYD_GEORGE_SNOMED = 16521000000101
API_ENDPOINT = os.environ.get("NDR_API_ENDPOINT")
API_KEY = os.environ.get("NDR_API_KEY")
LLOYD_GEORGE_S3_BUCKET = os.environ.get("NDR_S3_BUCKET") or ""
APIM_ENDPOINT = "internal-dev.api.service.nhs.uk"


@pytest.fixture
def test_data():
    test_records = []
    yield test_records
    for record in test_records:
        data_helper.tidyup(record)


def fetch_with_retry(url, condition_func, max_retries=5, delay=10):
    retries = 0
    while retries < max_retries:
        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}
        response = requests.get(url, headers=headers)
        if condition_func(response.json()):
            return response
        time.sleep(delay)
        retries += 1
    raise Exception("Condition not met within retry limit")


def calculate_check_digit(nhs_number_9_digits: str) -> int:
    total = sum(
        int(digit) * weight
        for digit, weight in zip(nhs_number_9_digits, range(10, 1, -1))
    )
    remainder = total % 11
    check_digit = 11 - remainder

    if check_digit == 11:
        return 0
    elif check_digit == 10:
        # Invalid check digit, caller must retry
        raise ValueError("Invalid check digit (10)")
    else:
        return check_digit


def generate_nhs_number() -> str:
    while True:
        nine_digits = "9" + "".join(
            str(random.randint(0, 9)) for _ in range(8)
        )  # Force first digit = 9
        try:
            check_digit = calculate_check_digit(nine_digits)
            return nine_digits + str(check_digit)
        except ValueError:
            # Retry if we hit an invalid check digit (10)
            continue
