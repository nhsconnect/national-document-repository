import unicodedata
from typing import List, Optional

REGEX_ACCENT_MARKS_IN_NFD = "".join(
    chr(code_point) for code_point in range(0x0300, 0x0370)
)
REGEX_ACCENT_CHARS_IN_NFC = "À-ž"
REGEX_PATIENT_NAME_PATTERN = (
    f"[-'A-Za-z {REGEX_ACCENT_CHARS_IN_NFC}{REGEX_ACCENT_MARKS_IN_NFD}]+"
)


def remove_accent_glyphs(input_str: str) -> str:
    """
    Return the input string with all diacritical marks (= accent glyphs) removed.
    Characters like é will be replaced by e, and characters like æ will be simply removed.
    """
    return (
        unicodedata.normalize("NFD", input_str)
        .encode("ASCII", "ignore")
        .decode("utf-8")
    )


def contains_accent_char(input_str: str) -> bool:
    """
    Detect whether the input string contains an accented characters
    """
    return input_str != remove_accent_glyphs(input_str)


def convert_to_nfc_form(input_str: str) -> str:
    """
    Convert a string to the NFC normalization form

    >>> cafe_as_nfd_form = b'cafe\xcc\x81'.decode('utf8')   # 'café'
    >>> cafe_as_nfc_form = b'caf\xc3\xa9'.decode('utf8')   # 'café'

    >>> convert_to_nfc_form(cafe_as_nfd_form) == cafe_as_nfc_form
    True

    """
    return unicodedata.normalize("NFC", input_str)


def find_possible_match_of_same_accent_string(
    input_str: str, list_of_candidates: List[str]
) -> Optional[str]:
    """
    Given a string A with accent char, and a list of possible candidates strings,
    find and return the first match which is string A's canonical equivalent.

    If no match was found, return None.

    Example:

    >>> cafe_as_nfc_form = b'caf\xc3\xa9'.decode('utf8')   # 'café'
    >>> cafe_as_nfd_form = b'cafe\xcc\x81'.decode('utf8')   # 'café'
    >>> find_possible_match_of_same_accent_string(
        cafe_as_nfc_form, ["cafe", "cáfe", cafe_as_nfd_form]
    )
    "café"  # in nfd form

    >>> find_possible_match_of_same_accent_string(
        cafe_as_nfc_form, ["cafe", "cáfe", cafe_as_nfc_form]
    )
    "café"  # in nfc form

    >>> find_possible_match_of_same_accent_string(
        cafe_as_nfc_form, ["cafe", "cáfe", "Café", "CAFE"]
    )
    None

    """
    input_string_in_nfc_form = convert_to_nfc_form(input_str)
    for candidate in list_of_candidates:
        if convert_to_nfc_form(candidate) == input_string_in_nfc_form:
            return candidate

    return None
