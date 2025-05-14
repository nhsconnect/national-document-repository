from utils.file_utils import convert_csv_dictionary_to_bytes


def test_convert_csv_dictionary_to_bytes():
    headers = ["id", "name", "age"]
    metadata_csv_data = [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
    ]

    result_bytes = convert_csv_dictionary_to_bytes(
        headers=headers, csv_dict_data=metadata_csv_data, encoding="utf-8"
    )

    result_str = result_bytes.decode("utf-8")
    expected_output = "id,name,age\r\n1,Alice,30\r\n2,Bob,25\r\n"

    assert result_str == expected_output
