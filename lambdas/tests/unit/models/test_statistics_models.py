import pydantic
import pytest
from models.statistics import ApplicationData, RecordStoreData, load_from_dynamodb_items
from tests.unit.helpers.data.statistic.mock_statistic_data import (
    MOCK_APPLICATION_DATA_1,
    MOCK_APPLICATION_DATA_2,
    MOCK_APPLICATION_DATA_3,
    MOCK_DYNAMODB_ITEMS,
    MOCK_ORGANISATION_DATA_1,
    MOCK_ORGANISATION_DATA_2,
    MOCK_ORGANISATION_DATA_3,
    MOCK_RECORD_STORE_DATA_1,
    MOCK_RECORD_STORE_DATA_2,
    MOCK_RECORD_STORE_DATA_3,
    SERIALISED_RECORD_STORE_DATA,
)


def test_serialise_and_deserialise_record_store_data(mocker):
    mocker.patch("uuid.uuid4", return_value="test_uuid")

    test_data = MOCK_RECORD_STORE_DATA_1

    output = test_data.model_dump(by_alias=True)
    expected = SERIALISED_RECORD_STORE_DATA[0]
    assert output == expected

    load_from_deserialised = RecordStoreData.model_validate(output)
    assert test_data == load_from_deserialised


def test_empty_ods_code_will_be_filled_with_an_empty_value():
    data = RecordStoreData(date="20240516", ods_code="")
    assert data.ods_code == "NO_ODS_CODE"


def test_validation_error_raised_when_try_to_deserialise_to_wrong_type():
    test_data = SERIALISED_RECORD_STORE_DATA[0]

    with pytest.raises(pydantic.ValidationError) as e:
        ApplicationData.model_validate(test_data)

    assert "StatisticID must be in the form of `ApplicationData#uuid" in str(e.value)


def test_load_from_dynamodb_items():
    deserialised_data = load_from_dynamodb_items(MOCK_DYNAMODB_ITEMS)

    assert deserialised_data.record_store_data == [
        MOCK_RECORD_STORE_DATA_1,
        MOCK_RECORD_STORE_DATA_2,
        MOCK_RECORD_STORE_DATA_3,
    ]
    assert deserialised_data.organisation_data == [
        MOCK_ORGANISATION_DATA_1,
        MOCK_ORGANISATION_DATA_2,
        MOCK_ORGANISATION_DATA_3,
    ]
    assert deserialised_data.application_data == [
        MOCK_APPLICATION_DATA_1,
        MOCK_APPLICATION_DATA_2,
        MOCK_APPLICATION_DATA_3,
    ]
