from typing import Dict, List, Optional

from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from models.nhs_document_reference import NHSDocumentReference
from tests.unit.conftest import (
    MOCK_LG_BUCKET,
    MOCK_LG_STAGING_STORE_BUCKET_ENV_NAME,
    TEST_NHS_NUMBER,
    TEST_UUID,
)
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE


def create_test_doc_store_refs():
    return [
        DocumentReference.model_validate(result)
        for result in MOCK_SEARCH_RESPONSE["Items"]
    ]


def create_test_lloyd_george_doc_store_refs(
    override: Optional[Dict] = None,
) -> List[DocumentReference]:
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


def create_test_doc_refs(override: Optional[Dict] = None) -> List[NHSDocumentReference]:
    file_names = [
        f"{i}of3_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"
        for i in range(1, 4)
    ]
    arguments = {
        "nhs_number": TEST_NHS_NUMBER,
        "s3_bucket_name": MOCK_LG_STAGING_STORE_BUCKET_ENV_NAME,
        "sub_folder": "upload",
        "reference_id": TEST_UUID,
        "content_type": "application/pdf",
        "doc_type": SupportedDocumentTypes.LG.value,
        "uploading": True,
        **override,
    }

    list_of_doc_ref = [
        NHSDocumentReference(file_name=file_name, **arguments)
        for file_name in file_names
    ]

    return list_of_doc_ref


def create_test_doc_refs_as_dict(override: Optional[Dict] = None) -> List[Dict]:
    test_doc_refs = create_test_doc_refs(override)
    return [doc_ref.to_dict() for doc_ref in test_doc_refs]
