import os
from uuid import uuid4

from pypdf import PdfReader, PdfWriter
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def stitch_pdf(filenames: list[str], temp_folder: str = "/tmp/") -> str:
    # Given a list of local pdf files, stitch them into one file and return the local file path of resulting file.
    # Using /tmp/ as it is the only writable location on lambdas.
    merger = PdfWriter()
    for filename in filenames:
        merger.append(filename)
    output_filename = os.path.join(temp_folder, f"{str(uuid4())}.pdf")
    merger.write(output_filename)
    return output_filename


def count_page_number(filename: str) -> int:
    return len(PdfReader(filename).pages)
