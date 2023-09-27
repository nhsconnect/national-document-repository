import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def order_response_by_filenames(dynamodb_response: list[dict]) -> list[dict]:
    # this method assume the input has a key FileName with the Lloyd George naming convention like this:
    # 1of3_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf

    logger.warning("Some pages of the Lloyd George document appear missing")

    sorted_response = sorted(dynamodb_response, key=lambda item: extract_page_number(item['FileName']))
    return sorted_response


def extract_page_number(filename: str) -> int:
    pos_to_trim = filename.index("of")
    page_number_as_string = filename[0:pos_to_trim]
    return int(page_number_as_string)
