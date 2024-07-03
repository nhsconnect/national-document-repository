import re

import pytest
from utils.unicode_utils import (
    REGEX_PATIENT_NAME_PATTERN,
    contains_accent_char,
    convert_to_nfc_form,
    convert_to_nfd_form,
    name_ends_with,
    name_starts_with,
    names_are_matching,
    remove_accent_glyphs,
)

NAME_WITH_ACCENT_NFC_FORM = "Évèlynêë François Ågāřdñ"
NAME_WITH_ACCENT_NFD_FORM = "Évèlynêë François Ågāřdñ"
NAME_WITHOUT_ACCENT_CHARS = "Evelynee Francois Agardn"


@pytest.mark.parametrize(
    ["input_str", "expected"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITHOUT_ACCENT_CHARS),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITHOUT_ACCENT_CHARS),
        (NAME_WITHOUT_ACCENT_CHARS, NAME_WITHOUT_ACCENT_CHARS),
    ],
)
def test_remove_accent_chars(input_str, expected):
    actual = remove_accent_glyphs(input_str)

    assert actual == expected


@pytest.mark.parametrize(
    ["input_str", "expected"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, True),
        (NAME_WITH_ACCENT_NFD_FORM, True),
        (NAME_WITHOUT_ACCENT_CHARS, False),
    ],
)
def test_contains_accent_char(input_str, expected):
    test_string = f"/9000000002/1of1_Lloyd_George_Record_[{input_str}]_[9000000002]_[25-12-2019].pdf"
    actual = contains_accent_char(test_string)

    assert actual == expected


@pytest.mark.parametrize(
    ["name_a", "name_b", "expected"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITH_ACCENT_NFD_FORM, True),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITH_ACCENT_NFC_FORM, True),
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITHOUT_ACCENT_CHARS, False),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITHOUT_ACCENT_CHARS, False),
    ],
)
def test_names_are_matching_handles_different_normalisation_forms(
    name_a, name_b, expected
):
    actual = names_are_matching(name_a, name_b)

    assert actual == expected


def test_names_are_matching_handles_letter_case_difference():
    name_a = NAME_WITH_ACCENT_NFC_FORM.upper()
    name_b = NAME_WITH_ACCENT_NFD_FORM.title()
    expected = True

    actual = names_are_matching(name_a, name_b)

    assert actual == expected


@pytest.mark.parametrize(
    ["full_name", "partial_name", "expected"],
    [
        ("Jane Bob Smith Anderson", "Jane", True),
        ("Jane Bob Smith Anderson", "Bob", False),
        ("Jane Bob Smith Anderson", "jane", True),
        ("jane Bob Smith Anderson", "Jane Bob", True),
        ("jane Bob Smith Anderson", "Jane-Bob", False),
        ("Jàne Bob Smith Anderson", "Jane", False),
        ("Jàne Bob Smith Anderson", "Jàne", True),  # NFC <-> NFD
        ("Jàne Bob Smith Anderson", "Jàne", True),  # NFD <-> NFC
    ],
)
def test_name_starts_with(full_name, partial_name, expected):
    actual = name_starts_with(full_name, partial_name)

    assert actual == expected


@pytest.mark.parametrize(
    ["full_name", "partial_name", "expected"],
    [
        ("Jane Bob Smith Anderson", "Anderson", True),
        ("Jane Bob Smith Anderson", "Smith", False),
        ("Jane Bob Smith Anderson", "anderson", True),
        ("jane Bob Smith Anderson", "Smith Anderson", True),
        ("jane Bob Smith Anderson", "Smith-Anderson", False),
        ("Jane Bob Smith Andèrson", "Anderson", False),
        ("Jane Bob Smith Andèrson", "Andèrson", True),  # NFC <-> NFD
        ("Jane Bob Smith Andèrson", "Andèrson", True),  # NFD <-> NFC
    ],
)
def test_name_ends_with(full_name, partial_name, expected):
    actual = name_ends_with(full_name, partial_name)
    assert actual == expected


@pytest.mark.parametrize(
    ["input_str", "expected"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITH_ACCENT_NFC_FORM),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITH_ACCENT_NFC_FORM),
        (NAME_WITHOUT_ACCENT_CHARS, NAME_WITHOUT_ACCENT_CHARS),
    ],
)
def test_convert_to_nfc_form(input_str, expected):
    actual = convert_to_nfc_form(input_str)

    assert actual == expected


@pytest.mark.parametrize(
    ["input_str", "expected"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITH_ACCENT_NFD_FORM),
        (NAME_WITH_ACCENT_NFD_FORM, NAME_WITH_ACCENT_NFD_FORM),
        (NAME_WITHOUT_ACCENT_CHARS, NAME_WITHOUT_ACCENT_CHARS),
    ],
)
def test_convert_to_nfd_form(input_str, expected):
    actual = convert_to_nfd_form(input_str)

    assert actual == expected


def test_regex_pattern_for_matching_patient_names():
    name_with_apostrophe = "Smith O'Brien"
    name_with_hyphen = "David Lloyd-George"
    test_patient_names = [
        NAME_WITHOUT_ACCENT_CHARS,
        NAME_WITH_ACCENT_NFC_FORM,
        NAME_WITH_ACCENT_NFD_FORM,
        name_with_apostrophe,
        name_with_hyphen,
    ]

    for name in test_patient_names:
        actual = re.match(REGEX_PATIENT_NAME_PATTERN, name)
        assert actual is not None, "Name should be matched by regex pattern"
        assert actual.group() == name, "Regex pattern should capture the whole name"
