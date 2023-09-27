import logging

from utils.order_response_by_filenames import order_response_by_filenames


def build_expected_output(total_page_number: int) -> list[dict]:
    output = []
    for i in range(total_page_number):
        output.append(build_dynamo_response_item(i + 1, total_page_number))
    return output


def build_dynamo_response_item(curr_page_number: int, total_page_number: int) -> dict:
    return {
        "ID": "some_uuid",
        "NhsNumber": "1234567890",
        "FileLocation": "s3://ndr-dev-lloyd-george-store/9e9867f0-9767-402d-a4d6-c1af4575a6bf",
        "FileName": f"{curr_page_number}of{total_page_number}_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019].pdf",
    }


def test_order_response_by_filenames_base_case():
    dynamo_response_not_in_order = [
        build_dynamo_response_item(curr_page_number=i, total_page_number=3)
        for i in [3, 1, 2]
    ]

    expected = build_expected_output(total_page_number=3)
    actual = order_response_by_filenames(dynamo_response_not_in_order)

    assert actual == expected


def test_order_response_by_filenames_more_then_10_pages():
    dynamo_response_not_in_order = [
        build_dynamo_response_item(curr_page_number=i, total_page_number=15)
        for i in [6, 7, 10, 11, 12, 1, 8, 3, 4, 5, 13, 9, 2, 14, 15]
    ]

    expected = build_expected_output(total_page_number=15)
    actual = order_response_by_filenames(dynamo_response_not_in_order)

    assert actual == expected


def test_order_response_by_filenames_missing_page(caplog):
    dynamo_response_missing_page_10_to_12 = [
        build_dynamo_response_item(curr_page_number=i, total_page_number=15)
        for i in [6, 7, 1, 8, 3, 4, 5, 13, 9, 2, 14, 15]
    ]
    all_pages_in_order = build_expected_output(total_page_number=15)
    expected = all_pages_in_order[0:9] + all_pages_in_order[12:]

    actual = order_response_by_filenames(dynamo_response_missing_page_10_to_12)

    assert actual == expected


def test_warning_message_logged_when_some_pages_missing(caplog):
    dynamo_response_missing_page_10_to_12 = [
        build_dynamo_response_item(curr_page_number=i, total_page_number=15)
        for i in [6, 7, 1, 8, 3, 4, 5, 13, 9, 2, 14, 15]
    ]
    with caplog.at_level(logging.INFO):
        order_response_by_filenames(dynamo_response_missing_page_10_to_12)
    assert "something" in caplog.text
    # or, if you really need to check the log-level
    assert caplog.records[-1].message == "Some pages of the Lloyd George document appear missing"
    assert caplog.records[-1].levelname == "WARNING"
