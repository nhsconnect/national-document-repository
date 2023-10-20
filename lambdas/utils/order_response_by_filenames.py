import logging

from enums.metadata_field_names import DocumentReferenceMetadataFields

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# this method assume the input has a key FileName with the Lloyd George naming convention like this:
# 1of3_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf
def order_response_by_filenames(dynamodb_response: list[dict]) -> list[dict]:
    filename_key = DocumentReferenceMetadataFields.FILE_NAME.value
    sorted_response = sorted(
        dynamodb_response, key=lambda item: extract_page_number(item[filename_key])
    )
    if len(dynamodb_response) != extract_total_pages(
        dynamodb_response[0][filename_key]
    ):
        logger.warning("Some pages of the Lloyd George document appear missing")
    return sorted_response


def extract_page_number(filename: str) -> int:
    pos_to_trim = filename.index("of")
    page_number_as_string = filename[0:pos_to_trim]
    return int(page_number_as_string)


def extract_total_pages(filename: str) -> int:
    start_pos = filename.index("of") + 2
    end_pos = filename.index("_")
    page_number_as_string = filename[start_pos:end_pos]
    return int(page_number_as_string)
