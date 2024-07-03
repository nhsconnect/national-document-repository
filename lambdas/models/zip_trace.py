import uuid
from datetime import datetime, timezone

from enums.zip_trace import ZipTraceStatus
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal

# class ZipTrace:
#     def __init__(self, files_to_download: dict[str, str]):
#         self.id = uuid.uuid4()
#         self.job_id = uuid.uuid4()
#         self.created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
#         self.status = ZipTraceStatus.PENDING.value
#         self.zip_location = (
#             f"s3://{os.environ['ZIPPED_STORE_BUCKET_NAME']}/{self.job_id}"
#         )
#         self.files_to_download: dict[str, str] = files_to_download
#
#     def to_dict(self):
#         zip_trace_metadata = {
#             ZipTraceFields.ID.value: str(self.id),
#             ZipTraceFields.JOB_ID.value: str(self.job_id),
#             ZipTraceFields.CREATED.value: self.created,
#             ZipTraceFields.STATUS.value: self.status,
#             ZipTraceFields.ZIP_FILE_LOCATION.value: self.zip_location,
#             ZipTraceFields.FILES_TO_DOWNLOAD.value: self.files_to_download,
#         }
#         return zip_trace_metadata


class DocumentManifestZipTrace(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal)

    id: str = Field(alias="ID", default_factory=lambda: str(uuid.uuid4()))
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    files_to_download: dict[str, str]
    status: str = Field(default=ZipTraceStatus.PENDING.value)
    zip_file_location: str = ""


data = {
    "Id": "c7b9348a-73cd-4b28-b583-432ba5683d2e",
    "JobId": "b23beda1-ca44-4fe0-afb2-6ad1ccdad89a",
    "Created": "2024-07-02T15:41:32.017828Z",
    "FilesToDownload": {
        "s3://test-location": "test1",
        "s3://test-location2": "test2",
        "s3://test-location3": "test3",
    },
    "Status": "Processing",
    "ZipFileLocation": "s3://test-location",
    "Invalid": "test",
}
zip_trace = DocumentManifestZipTrace.model_validate(data)
#
# # documents_to_download = {'s3://ndrc-lloyd-george-store/9000000004/f2a8e23d-80b1-4682-9ccb-ee84d65b6937':
# '1of5_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf'}
# # zip_trace = DocumentManifestZipTrace(FilesToDownload=documents_to_download)
#
# print(zip_trace.model_dump(by_alias=True))
