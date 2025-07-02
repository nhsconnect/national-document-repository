import csv
from io import BytesIO, TextIOWrapper


def convert_csv_dictionary_to_bytes(
    headers: list[str], csv_dict_data: list[dict], encoding: str = "utf-8"
) -> bytes:
    csv_buffer = BytesIO()
    csv_text_wrapper = TextIOWrapper(csv_buffer, encoding=encoding, newline="")
    fieldnames = headers if headers else []

    writer = csv.DictWriter(csv_text_wrapper, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(csv_dict_data)

    csv_text_wrapper.flush()
    csv_buffer.seek(0)

    result = csv_buffer.getvalue()
    csv_buffer.close()

    return result
