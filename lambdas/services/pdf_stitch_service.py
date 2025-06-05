import os
from uuid import uuid4

from pypdf import PdfReader, PdfWriter
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def stitch_pdf(filenames: list[str], temp_folder: str = "/tmp/") -> str:
    """
    Given a list of local PDF files, stitch them into one file and return the local file path of a resulting file.

    Example usage:
        filenames = ["file1.pdf", "file2.pdf", "file3.pdf"]
        tmp_folder = "/tmp/"
        stitch_pdf(filename, tmp_folder)

    Result:
        "/tmp/(filename_of_stitched_file).pdf"
    """
    merger = PdfWriter()
    for filename in filenames:
        merger.append(filename)
    output_filename = os.path.join(temp_folder, f"{str(uuid4())}.pdf")
    merger.write(output_filename)
    return output_filename


def count_page_number(filename: str) -> int:
    """
    Return the total number of pages in a PDF file
    """
    return len(PdfReader(filename).pages)
