import uuid
from decimal import Decimal
from typing import NamedTuple

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pydantic.alias_generators import to_pascal


class StatisticData(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True)
    statistic_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), alias="StatisticID"
    )
    date: str
    ods_code: str

    @field_serializer("statistic_id")
    def serialise_id(self, statistic_id) -> str:
        return f"{self.__class__.__name__}#{statistic_id}"

    # noinspection PyNestedDecorators
    @field_validator("statistic_id")
    @classmethod
    def deserialize_id(cls, raw_statistic_id: str) -> str:
        if "#" in raw_statistic_id:
            record_type, uuid_part = raw_statistic_id.split("#")
            class_name = cls.__name__
            assert (
                record_type == class_name
            ), f"StatisticID must be in the form of `{class_name}#uuid`"
        else:
            uuid_part = raw_statistic_id

        return uuid_part

    # noinspection PyNestedDecorators
    @field_validator("ods_code")
    @classmethod
    def fill_empty_ods_code(cls, ods_code: str) -> str:
        if not ods_code:
            return "NO_ODS_CODE"
        return ods_code


class RecordStoreData(StatisticData):
    total_number_of_records: int = 0
    number_of_document_types: int = 0
    total_size_of_records_in_megabytes: Decimal = Decimal(0)
    average_size_of_documents_per_patient_in_megabytes: Decimal = Decimal(0)


class OrganisationData(StatisticData):
    number_of_patients: int = 0
    average_records_per_patient: Decimal = Decimal(0)
    daily_count_stored: int = 0
    daily_count_viewed: int = 0
    daily_count_downloaded: int = 0
    daily_count_deleted: int = 0
    daily_count_searched: int = 0


class ApplicationData(StatisticData):
    active_user_ids_hashed: list[str] = []


class LoadedStatisticData(NamedTuple):
    record_store_data: list[RecordStoreData]
    organisation_data: list[OrganisationData]
    application_data: list[ApplicationData]


def load_from_dynamodb_items(dynamodb_items: list[dict]) -> LoadedStatisticData:
    output = LoadedStatisticData([], [], [])

    for item in dynamodb_items:
        data_type = item["StatisticID"].split("#")[0]
        match data_type:
            case "RecordStoreData":
                output.record_store_data.append(RecordStoreData.model_validate(item))
            case "OrganisationData":
                output.organisation_data.append(OrganisationData.model_validate(item))
            case "ApplicationData":
                output.application_data.append(ApplicationData.model_validate(item))
            case _:
                raise ValueError(f"unknown type of statistic data: {data_type}")

    return output
