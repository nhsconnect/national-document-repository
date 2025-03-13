from utils.multi_value_enum import MultiValueEnum


class MockEnumColour(MultiValueEnum):
    RED = (1, "FF0000")
    GREEN = (2, "00FF00")
    BLUE = (3, "0000FF")


def test_multi_value_enum_creation():
    assert MockEnumColour.RED.value == 1
    assert MockEnumColour.RED.additional_value == "FF0000"
    assert MockEnumColour.GREEN.value == 2
    assert MockEnumColour.GREEN.additional_value == "00FF00"
    assert MockEnumColour.BLUE.value == 3
    assert MockEnumColour.BLUE.additional_value == "0000FF"


def test__multi_value_enum_list():
    assert MockEnumColour.list() == [1, 2, 3]


def test__multi_value_enum_enum_members():
    assert MockEnumColour.RED in MockEnumColour
    assert MockEnumColour.GREEN in MockEnumColour
    assert MockEnumColour.BLUE in MockEnumColour
