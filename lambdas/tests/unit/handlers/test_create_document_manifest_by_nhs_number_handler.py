from handlers.create_document_manifest_by_nhs_number_handler import find_document_locations

NHS_NUMBER = 1111111111


def test_find_docs_retrieves_something():
    actual = find_document_locations(NHS_NUMBER)
    assert len(actual) > 0
    assert actual[0].startswith("s3://")
