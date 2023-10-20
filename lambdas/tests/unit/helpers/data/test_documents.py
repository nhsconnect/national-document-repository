from models.document_reference import DocumentReference
from tests.unit.helpers.data.dynamo_responses import MOCK_SEARCH_RESPONSE


def create_test_doc_store_refs():
    return [
        DocumentReference.model_validate(result)
        for result in MOCK_SEARCH_RESPONSE["Items"]
    ]


def create_test_lloyd_george_doc_store_refs():
    refs = create_test_doc_store_refs()

    refs[
        0
    ].file_name = "1of3_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"
    refs[0].file_location = "s3://test-lg-bucket/test-key-423"
    refs[
        1
    ].file_name = "2of3_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"
    refs[1].file_location = "s3://test-lg-bucket/test-key-523"
    refs[
        2
    ].file_name = "3of3_Lloyd_George_Record_[Joe Bloggs]_[9000000009]_[30-12-2019].pdf"
    refs[2].file_location = "s3://test-lg-bucket/test-key-623"

    return refs
