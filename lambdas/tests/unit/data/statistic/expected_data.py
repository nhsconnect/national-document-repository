from datetime import datetime

from models.statistics import RecordStoreData
from unit.data.statistic.s3_list_objects_result import (
    TOTAL_FILE_SIZE_FOR_H81109,
    TOTAL_FILE_SIZE_FOR_Y12345,
)

TODAY_DATE = datetime.today().strftime("%Y%m%d")

MOCK_RECORD_STORE_DATA = [
    RecordStoreData(
        statistic_id="uuid1",
        date=TODAY_DATE,
        ods_code="H81109",
        total_number_of_records=6,
        number_of_document_types=2,
        total_size_of_records_in_megabytes=TOTAL_FILE_SIZE_FOR_H81109,
        average_size_of_documents_per_patient_in_megabytes=TOTAL_FILE_SIZE_FOR_H81109
        / 2,
    ),
    RecordStoreData(
        statistic_id="uuid2",
        date=TODAY_DATE,
        ods_code="Y12345",
        total_number_of_records=2,
        number_of_document_types=2,
        total_size_of_records_in_megabytes=TOTAL_FILE_SIZE_FOR_Y12345,
        average_size_of_documents_per_patient_in_megabytes=TOTAL_FILE_SIZE_FOR_Y12345,
    ),
]
