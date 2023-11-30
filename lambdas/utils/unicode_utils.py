import unicodedata

REGEX_ACCENT_MARKS_IN_NFD = "".join(
    chr(code_point) for code_point in range(0x0300, 0x0370)
)
REGEX_ACCENT_CHARS_IN_NFC = "À-ž"
REGEX_PATIENT_NAME_PATTERN = (
    rf"[-'A-Za-z {REGEX_ACCENT_CHARS_IN_NFC}{REGEX_ACCENT_MARKS_IN_NFD}\-']+"
)


def remove_accent_glyphs(input_str: str) -> str:
    """
    Return the input string with all diacritical marks (= accent glyphs) removed.
    Characters like é will be replaced by e, and characters like æ will be simply removed.
    """
    return convert_to_nfd_form(input_str).encode("ASCII", "ignore").decode("utf-8")


def contains_accent_char(input_str: str) -> bool:
    """
    Detect whether the input string contains an accented characters
    """
    return input_str != remove_accent_glyphs(input_str)


def names_are_matching(name_a: str, name_b: str) -> bool:
    """
    Determine whether two names are matching.
    This function account for differences in letter cases and unicode normalisation forms.

    >>> name_in_nfc_and_proper_case = 'León Mórwyn'
    >>> name_in_nfd_and_all_caps = 'LEÓN MÓRWYN'
    >>> name_without_grave_accent_char = 'Leon Morwyn'

    >>> names_are_matching(name_in_nfc_and_proper_case, name_in_nfd_and_all_caps)
    True

    >>> names_are_matching(name_in_nfc_and_proper_case, name_without_grave_accent_char)
    False
    """
    return (
        convert_to_nfd_form(name_a).casefold() == convert_to_nfd_form(name_b).casefold()
    )


def convert_to_nfc_form(input_str: str) -> str:
    """
    Convert a string to the NFC normalization form

    >>> cafe_as_nfc_form = b'caf\xc3\xa9'.decode('utf8')   # 'café'
    >>> cafe_as_nfd_form = b'cafe\xcc\x81'.decode('utf8')   # 'café'

    >>> convert_to_nfc_form(cafe_as_nfd_form) == cafe_as_nfc_form
    True

    """
    return unicodedata.normalize("NFC", input_str)


def convert_to_nfd_form(input_str: str) -> str:
    """
    Convert a string to the NFD normalization form

    >>> cafe_as_nfc_form = b'caf\xc3\xa9'.decode('utf8')   # 'café'
    >>> cafe_as_nfd_form = b'cafe\xcc\x81'.decode('utf8')   # 'café'

    >>> convert_to_nfd_form(cafe_as_nfc_form) == cafe_as_nfd_form
    True

    """
    return unicodedata.normalize("NFD", input_str)
