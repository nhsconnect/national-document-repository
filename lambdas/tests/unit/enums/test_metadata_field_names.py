from enums.metadata_field_names import DynamoDocumentMetadataTableFields


def test_can_get_one_field_name():
    subject = DynamoDocumentMetadataTableFields["NHS_NUMBER"]
    assert subject.field_name == "NhsNumber"
    assert subject.field_alias == "#nhsNumber"


def test_returns_all_as_list():
    subject = DynamoDocumentMetadataTableFields.list()
    assert len(subject) == 10
    assert DynamoDocumentMetadataTableFields.FILE_NAME in subject
    assert DynamoDocumentMetadataTableFields.CREATED in subject
    assert DynamoDocumentMetadataTableFields.LOCATION in subject
