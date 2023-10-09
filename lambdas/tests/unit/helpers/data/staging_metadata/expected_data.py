from models.staging_metadata import MetadataFile, StagingMetadata

patient_1_file_1 = MetadataFile(
    file_path="/1234567890/1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
    page_count="",
    gp_practice_code="",
    section="LG",
    sub_section="",
    scan_date="03/09/2022",
    scan_id="NEC",
    user_id="NEC",
    upload="04/10/2023",
)
patient_1_file_2 = MetadataFile(
    file_path="/1234567890/2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
    page_count="",
    gp_practice_code="",
    section="LG",
    sub_section="",
    scan_date="03/09/2022",
    scan_id="NEC",
    user_id="NEC",
    upload="04/10/2023",
)

patient_1 = StagingMetadata(
    nhs_number=1234567890, files=[patient_1_file_1, patient_1_file_2]
)

patient_2_file_1 = MetadataFile(
    file_path="1of1_Lloyd_George_Record_[Joe Bloggs_invalid]_[1234567891]_[25-12-2019].txt",
    page_count="",
    gp_practice_code="",
    section="LG",
    sub_section="",
    scan_date="04/09/2022",
    scan_id="NEC",
    user_id="NEC",
    upload="04/10/2023",
)

patient_2 = StagingMetadata(nhs_number=1234567891, files=[patient_2_file_1])

EXPECTED_PARSED_METADATA = [patient_1, patient_2]

EXPECTED_SQS_MSG_FOR_PATIENT_1234567890 = patient_1.model_dump_json()
EXPECTED_SQS_MSG_FOR_PATIENT_1234567891 = patient_2.model_dump_json()
