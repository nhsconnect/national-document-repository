from enums.metadata_field_names import DocumentReferenceMetadataFields


def test_can_get_one_field_name():
    subject = DocumentReferenceMetadataFields["NHS_NUMBER"]
    assert subject.field_name == "NhsNumber"
    assert subject.field_alias == "#nhsNumber"


def test_returns_all_as_list():
    subject = DocumentReferenceMetadataFields.list()
    assert len(subject) == 8
    assert DocumentReferenceMetadataFields.FILE_NAME in subject
    assert DocumentReferenceMetadataFields.CREATED in subject
    assert DocumentReferenceMetadataFields.FILE_LOCATION in subject
