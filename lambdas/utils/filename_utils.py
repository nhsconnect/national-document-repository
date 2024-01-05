def extract_page_number(filename: str) -> int:
    """
    extract page number from lloyd george file names

    example usage:
        filename = "123of456_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf"
        extract_page_number(filename)

    result:
        123
    """
    pos_to_trim = filename.index("of")
    page_number_as_string = filename[0:pos_to_trim]
    return int(page_number_as_string)


def extract_total_pages(filename: str) -> int:
    """
    extract total page number from lloyd george file names

    example usage:
        filename = "123of456_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf"
        extract_total_pages(filename)

    result:
        456
    """
    start_pos = filename.index("of") + 2
    end_pos = filename.index("_")
    page_number_as_string = filename[start_pos:end_pos]
    return int(page_number_as_string)
