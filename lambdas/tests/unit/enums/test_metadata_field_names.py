from enums.metadata_field_names import DocumentReferenceMetadataFields


def test_can_get_one_field_name():
    subject = DocumentReferenceMetadataFields["NHS_NUMBER"]
    assert subject.field_name == "NhsNumber"
    assert subject.field_alias == "#nhsNumber"


def test_returns_all_as_list():
    subject = DocumentReferenceMetadataFields.list()
    assert len(subject) == 9
    assert DocumentReferenceMetadataFields.ID in subject
    assert DocumentReferenceMetadataFields.CONTENT_TYPE in subject
    assert DocumentReferenceMetadataFields.CREATED in subject
    assert DocumentReferenceMetadataFields.DELETED in subject
    assert DocumentReferenceMetadataFields.FILE_NAME in subject
    assert DocumentReferenceMetadataFields.FILE_LOCATION in subject
    assert DocumentReferenceMetadataFields.NHS_NUMBER in subject
    assert DocumentReferenceMetadataFields.TYPE in subject
    assert DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT in subject
