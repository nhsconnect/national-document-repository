import os
import tempfile

import pytest
from pypdf.errors import PyPdfError
from services.pdf_stitch_service import count_page_number, stitch_pdf


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
