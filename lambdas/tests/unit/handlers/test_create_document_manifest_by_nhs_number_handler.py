from handlers.create_document_manifest_by_nhs_number_handler import find_document_locations

NHS_NUMBER = 1111111111


def test_find_docs_retrieves_something():
    actual = find_document_locations(NHS_NUMBER)
    assert len(actual) > 0
    assert actual[0].startswith("s3://")

# Mock the DynamoQueryService for this unit test
# Example below
# with patch.object(DynamoQueryService, "__call__", return_value=MOCK_RESPONSE):
# Refer to test_document_reference_search_handler for examples of patch.object
# We'd like the output to be list of strings, example: <-- might change later, but ok for now
# [
#   's3://rachel-is-cool/abcde-3i421394792837-sdkbcskjdnf',
#   's3://alex-is-cool/abcde-3i421394792837-sdkbcskjdnf',
# ]

# Test it has the s3:// at the start and contains the bucket ID as expected
# Test for empty response (i.e. response with empty Items)
# Write a test to see if it responds correctly whern an exception is thrown from the Dynamo service

