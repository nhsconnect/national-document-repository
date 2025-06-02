import os
import tempfile
from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PyPdfError
from services.pdf_stitch_service import (
    count_page_number,
    stitch_pdf,
    stitch_pdf_into_steam,
)


def test_stitch_pdf():
    test_pdf_folder = "tests/unit/helpers/data/pdf/"
    input_test_files = [
        f"{test_pdf_folder}/{filename}"
        for filename in ["file1.pdf", "file2.pdf", "file3.pdf"]
    ]

    stitched_file = stitch_pdf(input_test_files)
    assert count_page_number(stitched_file) == sum(
        count_page_number(filepath) for filepath in input_test_files
    )

    os.remove(stitched_file)


def test_stitch_pdf_with_given_desc_folder():
    test_pdf_folder = "tests/unit/helpers/data/pdf/"
    test_desc_folder = tempfile.mkdtemp()

    input_test_files = [
        f"{test_pdf_folder}/{filename}"
        for filename in ["file1.pdf", "file2.pdf", "file3.pdf"]
    ]

    stitched_file = stitch_pdf(input_test_files, test_desc_folder)

    assert stitched_file.startswith(test_desc_folder)

    os.remove(stitched_file)


def test_stitch_pdf_raise_error_if_fail_to_perform_stitching():
    test_pdf_folder = "tests/unit/helpers/data/pdf/"
    input_test_files = [
        f"{test_pdf_folder}/{filename}" for filename in ["invalid_pdf.pdf", "file1.pdf"]
    ]

    with pytest.raises(PyPdfError):
        stitch_pdf(input_test_files)


def test_stitch_pdf_raise_error_when_input_file_not_found():
    test_file = "non-exist-file.pdf"

    with pytest.raises(FileNotFoundError):
        stitch_pdf([test_file])


def create_in_memory_pdf(page_count: int = 1) -> BytesIO:
    # Creates a PDF in memory with the received number of pages
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=72, height=72)

    stream = BytesIO()
    writer.write(stream)
    stream.seek(0)
    return stream


def test_stitch_pdf_into_stream_returns_combined_pdf():
    pdf_streams = [
        create_in_memory_pdf(1),
        create_in_memory_pdf(2),
        create_in_memory_pdf(3),
    ]

    result_stream = stitch_pdf_into_steam(pdf_streams)

    result_reader = PdfReader(result_stream)
    assert len(result_reader.pages) == 6
