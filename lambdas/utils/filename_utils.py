def extract_page_number(filename: str) -> int:
    """
    extract page number from Lloyd George file names

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
    extract total page number from Lloyd George file names

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

def assemble_lg_valid_file_name_full_path(
    file_path_prefix: str,
    first_document_number: int,
    second_document_number: int,
    patient_name: str,
    nhs_number: str,
    day: str,
    month: str,
    year: str,
    file_extension: str,
) -> str:
    """
    Generates a valid file name for Lloyd George records based on provided parameters.

    This function assembles a structured file name by concatenating various
    parameters following a specified format. It ensures that the file name
    contains information like document numbers,
    patient details, and date, along with a custom file extension.

    Parameters:
    file_path_prefix: str
        The prefix or directory path to be included in the file name.
    first_document_number: int
        The number of the current document in the series.
    second_document_number: int
        The total number of documents in the series.
    patient_name: str
        The name of the patient.
    nhs_number: str
        The NHS number corresponding to the patient.
    day: str
        The day of the date to be included in the file name.
    month: str
        The month of the date to be included in the file name.
    year: str
        The year of the date to be included in the file name.
    file_extension: str
        The file extension for the generated file name.

    Returns:
    str
        A formatted string representing the valid Lloyd George record file name.
    """
    return (
        f"{file_path_prefix}"
        f"{first_document_number}of{second_document_number}"
        f"_Lloyd_George_Record_"
        f"[{patient_name}]_"
        f"[{nhs_number}]_"
        f"[{day}-{month}-{year}]"
        f"{file_extension}"
    )
