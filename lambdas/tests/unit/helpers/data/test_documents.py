from typing import Dict, Optional

from models.document_reference import DocumentReference
from tests.unit.conftest import MOCK_LG_BUCKET
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE


def create_test_doc_store_refs():
    return [
        DocumentReference.model_validate(result)
        for result in MOCK_SEARCH_RESPONSE["Items"]
    ]


def create_test_lloyd_george_doc_store_refs(override: Optional[Dict] = None):
    refs = create_test_doc_store_refs()

    filename_1 = "1of3_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"
    filename_2 = "2of3_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"
    filename_3 = "3of3_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"

    refs[0].file_name = filename_1
    refs[0].file_location = f"s3://{MOCK_LG_BUCKET}/test-key-423"
    refs[1].file_name = filename_2
    refs[1].file_location = f"s3://{MOCK_LG_BUCKET}/test-key-523"
    refs[2].file_name = filename_3
    refs[2].file_location = f"s3://{MOCK_LG_BUCKET}/test-key-623"

    if override:
        refs = [doc_ref.model_copy(update=override) for doc_ref in refs]
    return refs
