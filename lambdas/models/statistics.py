import uuid
from decimal import Decimal

from models.config import to_capitalized_camel
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class StatisticData(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_capitalized_camel, populate_by_name=True
    )
    statistic_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str

    @field_serializer("statistic_id")
    def serialise_id(self, statistic_id) -> str:
        return f"{self.__class__.__name__}#{statistic_id}"


class RecordStoreData(StatisticData):
    ods_code: str
    total_number_of_records: int = 0
    number_of_document_types: int = 0
    total_size_of_records_in_megabytes: Decimal = Decimal(0)


class OrganisationData(StatisticData):
    ods_code: str
    number_of_patients: int = 0
    average_records_per_patient: Decimal = Decimal(0)
    daily_count_stored: int = 0
    daily_count_viewed: int = 0
    daily_count_downloaded: int = 0
    daily_count_deleted: int = 0


class ApplicationData(StatisticData):
    ods_code: str
    active_user_ids_hashed: list[str]
