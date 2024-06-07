from decimal import Decimal

import polars as pl
from models.statistics import ApplicationData, OrganisationData, RecordStoreData

MOCK_RECORD_STORE_DATA_1 = RecordStoreData(
    statistic_id="974b1ca0-8e5e-4d12-9673-93050f0fee71",
    date="20240510",
    ods_code="Y12345",
    total_number_of_records=25,
    number_of_document_types=1,
    total_size_of_records_in_megabytes=Decimal("1.23"),
)

MOCK_RECORD_STORE_DATA_2 = RecordStoreData(
    statistic_id="e02ec4db-8a7d-4f84-a4b3-875a526b37d4",
    date="20240510",
    ods_code="Z56789",
    total_number_of_records=18,
    number_of_document_types=1,
    total_size_of_records_in_megabytes=Decimal("1.7578678131103515625"),
)

MOCK_RECORD_STORE_DATA_3 = RecordStoreData(
    statistic_id="c2841ca0-8e5e-4d12-9673-93050f0fee71",
    date="20240511",
    ods_code="Y12345",
    total_number_of_records=20,
    number_of_document_types=2,
    total_size_of_records_in_megabytes=Decimal("2.34"),
)

EXPECTED_SUMMARY_RECORD_STORE_DATA = pl.DataFrame(
    [
        {
            "ods_code": "Z56789",
            "total_number_of_records": 18,
            "number_of_document_types": 1,
            "total_size_of_records_in_megabytes": 1.7578678131103515625,
        },
        {
            "ods_code": "Y12345",
            "total_number_of_records": 20,
            "number_of_document_types": 2,
            "total_size_of_records_in_megabytes": 2.34,
        },
    ]
)

MOCK_ORGANISATION_DATA_1 = OrganisationData(
    statistic_id="5acda4bf-8b93-4ba0-8410-789aac4fcbae",
    date="20240510",
    ods_code="Z56789",
    number_of_patients=4,
    average_records_per_patient=Decimal("4.5"),
    daily_count_stored=0,
    daily_count_viewed=35,
    daily_count_downloaded=4,
    daily_count_deleted=1,
)
MOCK_ORGANISATION_DATA_2 = OrganisationData(
    statistic_id="9ee2c3d1-97b9-4c34-b75c-83e7d1b442f4",
    date="20240510",
    ods_code="Y12345",
    number_of_patients=9,
    average_records_per_patient=Decimal("2.777777777777777777777777778"),
    daily_count_stored=0,
    daily_count_viewed=15,
    daily_count_downloaded=1,
    daily_count_deleted=1,
)

MOCK_APPLICATION_DATA_1 = ApplicationData(
    statistic_id="12d92f26-47c3-452c-923b-819cfcc27c79",
    date="20240510",
    ods_code="Y12345",
    active_user_ids_hashed=[
        "a873620d0b476b13ee571a28cc315870",
        "ba81803adac3c816b6cbaf67bf33022a",
    ],
)
MOCK_APPLICATION_DATA_2 = ApplicationData(
    statistic_id="d495959f-93dc-4f05-a869-43d8711ca120",
    date="20240510",
    ods_code="Z56789",
    active_user_ids_hashed=["cf1af742e351ce63d8ed275d4bec8d8f"],
)

SERIALISED_APPLICATION_DATA = [
    {
        "Date": "20240510",
        "OdsCode": "Y12345",
        "StatisticID": "ApplicationData#12d92f26-47c3-452c-923b-819cfcc27c79",
        "ActiveUserIdsHashed": [
            "a873620d0b476b13ee571a28cc315870",
            "ba81803adac3c816b6cbaf67bf33022a",
        ],
    },
    {
        "Date": "20240510",
        "OdsCode": "Z56789",
        "StatisticID": "ApplicationData#d495959f-93dc-4f05-a869-43d8711ca120",
        "ActiveUserIdsHashed": ["cf1af742e351ce63d8ed275d4bec8d8f"],
    },
]

SERIALISED_ORGANISATION_DATA = [
    {
        "Date": "20240510",
        "DailyCountStored": 0,
        "NumberOfPatients": 4,
        "AverageRecordsPerPatient": Decimal("4.5"),
        "DailyCountDownloaded": 4,
        "DailyCountViewed": 35,
        "OdsCode": "Z56789",
        "DailyCountDeleted": 1,
        "StatisticID": "OrganisationData#5acda4bf-8b93-4ba0-8410-789aac4fcbae",
    },
    {
        "Date": "20240510",
        "DailyCountStored": 0,
        "NumberOfPatients": 9,
        "AverageRecordsPerPatient": Decimal("2.777777777777777777777777778"),
        "DailyCountDownloaded": 1,
        "DailyCountViewed": 15,
        "OdsCode": "Y12345",
        "DailyCountDeleted": 1,
        "StatisticID": "OrganisationData#9ee2c3d1-97b9-4c34-b75c-83e7d1b442f4",
    },
]

SERIALISED_RECORD_STORE_DATA = [
    {
        "TotalSizeOfRecordsInMegabytes": Decimal("1.23"),
        "AverageSizeOfDocumentsPerPatientInMegabytes": Decimal("0"),
        "Date": "20240510",
        "TotalNumberOfRecords": 25,
        "NumberOfDocumentTypes": 1,
        "OdsCode": "Y12345",
        "StatisticID": "RecordStoreData#974b1ca0-8e5e-4d12-9673-93050f0fee71",
    },
    {
        "TotalSizeOfRecordsInMegabytes": Decimal("1.7578678131103515625"),
        "AverageSizeOfDocumentsPerPatientInMegabytes": Decimal("0"),
        "Date": "20240510",
        "TotalNumberOfRecords": 18,
        "NumberOfDocumentTypes": 1,
        "OdsCode": "Z56789",
        "StatisticID": "RecordStoreData#e02ec4db-8a7d-4f84-a4b3-875a526b37d4",
    },
]

MOCK_DYNAMODB_ITEMS = (
    SERIALISED_APPLICATION_DATA
    + SERIALISED_ORGANISATION_DATA
    + SERIALISED_RECORD_STORE_DATA
)
