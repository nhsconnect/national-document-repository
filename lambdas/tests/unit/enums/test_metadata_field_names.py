from enums.metadata_field_names import DynamoField


def test_can_get_one_field_name():
    subject = DynamoField['NHS_NUMBER']
    assert subject.field_name == "NhsNumber"
    assert subject.field_alias == "#nhsNumber"


def test_returns_all_as_list():
    subject = DynamoField.list()
    assert len(subject) == 10
    assert DynamoField.FILE_NAME in subject
    assert DynamoField.CREATED in subject
    assert DynamoField.LOCATION in subject
