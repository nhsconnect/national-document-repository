import re

import pytest
from utils.unicode_utils import (REGEX_PATIENT_NAME_PATTERN,
                                 contains_accent_char,
                                 find_possible_match_of_same_accent_string,
                                 remove_accent_glyphs)

NAME_WITH_ACCENT_NFC_FORM = "Évèlynêë François Ågāřdñ"
NAME_WITH_ACCENT_NFD_FORM = "Évèlynêë François Ågāřdñ"
NAME_WITHOUT_ACCENT_CHARS = "Evelynee Francois Agardn"


@pytest.mark.parametrize(
    ["input_str", "expected"],
    [
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITHOUT_ACCENT_CHARS),
        (NAME_WITH_ACCENT_NFC_FORM, NAME_WITHOUT_ACCENT_CHARS),
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


def test_find_possible_match_of_same_accent_string__match_same_normalization_form():
    input_str = NAME_WITH_ACCENT_NFC_FORM
    candidates = [
        NAME_WITHOUT_ACCENT_CHARS,
        NAME_WITHOUT_ACCENT_CHARS.upper(),
        NAME_WITH_ACCENT_NFC_FORM,
        "unrelated_string",
    ]
    expected = NAME_WITH_ACCENT_NFC_FORM

    actual = find_possible_match_of_same_accent_string(input_str, candidates)

    assert actual == expected


def test_find_possible_match_of_same_accent_string__match_different_normalization_form():
    input_str = NAME_WITH_ACCENT_NFD_FORM
    candidates = [
        NAME_WITHOUT_ACCENT_CHARS,
        NAME_WITHOUT_ACCENT_CHARS.upper(),
        "unrelated_string",
        NAME_WITH_ACCENT_NFC_FORM,
        "another_unrelated_string",
    ]
    expected = NAME_WITH_ACCENT_NFC_FORM

    actual = find_possible_match_of_same_accent_string(input_str, candidates)

    assert actual == expected


def test_find_possible_match_of_same_accent_string__return_none_if_no_match_was_found():
    input_str = NAME_WITH_ACCENT_NFD_FORM
    candidates = [
        "unrelated_string",
        NAME_WITHOUT_ACCENT_CHARS,
        NAME_WITH_ACCENT_NFD_FORM.upper(),
        NAME_WITHOUT_ACCENT_CHARS.upper(),
        "another_unrelated_string",
    ]
    expected = None

    actual = find_possible_match_of_same_accent_string(input_str, candidates)

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
