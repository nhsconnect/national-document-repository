import csv
import json
from typing import Optional
from pydantic import BaseModel

class MetadataFile(BaseModel):
    file_path: str
    page_count: str
    gp_practice_code: str
    section: str
    sub_section: Optional[str]
    scan_date: str
    scan_id: str
    user_id: str
    upload: str

class StagingMetadata(BaseModel):
    nhs_number: int
    files: list[MetadataFile]


def csv_to_json(csv_file_path):
    results = {}
    with open(csv_file_path, mode='r') as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)

        for row in csv_reader:
            file_metadata = MetadataFile.model_validate(row)
            nhs_number = row['nhs_number']
            if nhs_number not in results:
                results[nhs_number] = [file_metadata]
            else:
                results[nhs_number] += [file_metadata]

        return [json.dumps(StagingMetadata(nhs_number=nhs_number, files=results[nhs_number])) for nhs_number in results]