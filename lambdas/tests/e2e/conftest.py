import pytest
from tests.e2e.helpers.lloyd_george_data_helper import LloydGeorgeDataHelper

data_helper = LloydGeorgeDataHelper()

LLOYD_GEORGE_SNOMED = 16521000000101


@pytest.fixture
def test_data():
    test_records = []
    yield test_records
    for record in test_records:
        data_helper.tidyup(record)
