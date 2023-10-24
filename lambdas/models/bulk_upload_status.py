from datetime import datetime
from typing import List, Literal, TypeAlias, Union

from models.config import to_capwords
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from utils.utilities import create_reference_id


class UploadStatusBaseClass(BaseModel):
    model_config = ConfigDict(alias_generator=to_capwords, populate_by_name=True)
    id: str = Field(alias="ID", default_factory=create_reference_id)
    nhs_number: str
    timestamp: str = Field(default_factory=lambda: timestamp_as_string(now()))
    date: str = Field(default_factory=lambda: date_as_string(now()))
    file_path: str


class SuccessfulUpload(UploadStatusBaseClass):
    upload_status: Literal["complete"] = "complete"


class FailedUpload(UploadStatusBaseClass):
    upload_status: Literal["failed"] = "failed"
    failure_reason: str


UploadStatus = TypeAdapter(Union[SuccessfulUpload, FailedUpload])

UploadStatusListType: TypeAlias = List[Union[SuccessfulUpload, FailedUpload]]
UploadStatusList = TypeAdapter(UploadStatusListType)

FieldsToReport = []


def now() -> datetime:
    """Helper func for easier mocking, as datetime.now is immutable"""
    return datetime.now()


def timestamp_as_string(time_now: datetime) -> str:
    return str(time_now.timestamp())


def date_as_string(time_now: datetime) -> str:
    return time_now.strftime("%Y-%m-%d")


# def dump_upload_status_list_as_csv(
#     upload_status_list: UploadStatusList, csv_file_path: str
# ):
#     pass
#
#
# def store(persons: Iterable[Person]):
#     fieldnames = list(Person.schema()["properties"].keys())
#
#     with open("test.csv", "w") as fp:
#         writer = csv.DictWriter(fp, fieldnames=fieldnames)
#         writer.writeheader()
#         for person in persons:
#             writer.writerow(json.loads(PersonOut(**person.dict()).json()))
