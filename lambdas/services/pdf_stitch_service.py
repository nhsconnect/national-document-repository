from uuid import uuid4
import io

from pypdf import PdfReader, PdfWriter
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def stitch_pdf(filenames: list[str]) -> str:
    # Given a list of local pdf files, stitch them into one file and return the local file path of resulting file.
    # Using /tmp/ as it is the only writable location on lambdas.
    output_filename = f"/tmp/{str(uuid4())}.pdf"
    
    merger = PdfWriter()
    for filename in filenames:
        logger.info(f"Adding file contents to pds writter for: {filename}")
        merger.append(filename)
    

    logger.info(f"Writting files as pdf: {filename}")
    response_bytes_stream = io.BytesIO()
    merger.write(response_bytes_stream)
    return output_filename, response_bytes_stream


def count_page_number(filename: str) -> int:
    return len(PdfReader(filename).pages)
