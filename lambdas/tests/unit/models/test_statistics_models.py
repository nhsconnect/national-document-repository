import pydantic
import pytest
from models.statistics import ApplicationData, RecordStoreData, load_from_dynamodb_items
from unit.helpers.data.statistic_data import (
    mock_application_data_1,
    mock_application_data_2,
    mock_dynamodb_items,
    mock_organisation_data_1,
    mock_organisation_data_2,
    mock_record_store_data_1,
    mock_record_store_data_2,
    serialised_record_store_data,
)


def test_serialise_and_deserialise_record_store_data(mocker):
    mocker.patch("uuid.uuid4", return_value="test_uuid")

    test_data = mock_record_store_data_1

    output = test_data.model_dump(by_alias=True)
    expected = serialised_record_store_data[0]
    assert output == expected

    load_from_deserialised = RecordStoreData.model_validate(output)
    assert test_data == load_from_deserialised


def test_empty_ods_code_will_be_filled_with_an_empty_value(mocker):
    data = RecordStoreData(date="20240516", ods_code="")
    assert data.ods_code == "NO_ODS_CODE"


def test_validation_error_raised_when_try_to_deserialise_to_wrong_type():
    test_data = serialised_record_store_data[0]

    with pytest.raises(pydantic.ValidationError) as e:
        ApplicationData.model_validate(test_data)

    assert "StatisticID must be in the form of `ApplicationData#uuid" in str(e.value)


def test_load_from_dynamodb_items():
    deserialised_data = load_from_dynamodb_items(mock_dynamodb_items)

    assert deserialised_data.record_store_data == [
        mock_record_store_data_1,
        mock_record_store_data_2,
    ]
    assert deserialised_data.organisation_data == [
        mock_organisation_data_1,
        mock_organisation_data_2,
    ]
    assert deserialised_data.application_data == [
        mock_application_data_1,
        mock_application_data_2,
    ]
