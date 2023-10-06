import logging
from uuid import uuid4

from pypdf import PdfReader, PdfWriter

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def stitch_pdf(filenames: list[str]) -> str:
    # Given a list of local pdf files, stitch them into one file and return the local file path of resulting file.
    # Using /tmp/ as it is the only writable location on lambdas.
    merger = PdfWriter()
    for filename in filenames:
        merger.append(filename)
    output_filename = f"/tmp/{str(uuid4())}.pdf"
    merger.write(output_filename)
    return output_filename


def count_page_number(filename: str) -> int:
    return len(PdfReader(filename).pages)
