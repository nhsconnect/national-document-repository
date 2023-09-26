from io import BytesIO
from pypdf import PdfWriter, PdfReader
import boto3

from services.s3_service import S3Service


def test_pdf_stitching():
    merger = PdfWriter()
    for file_name in ["file1.pdf", "file2.pdf", "file3.pdf"]:
        file_path = f"tests/unit/helpers/data/pdf/{file_name}"
        merger.append(file_path)

    merger.write("tests/unit/helpers/data/pdf/output.pdf")
    merger.close()

def test_pdf_stitching_with_s3():
    s3_service = S3Service()
    merger = PdfWriter()
    bucket_name = "ndra-lloyd-george-store"
    temp_folder = "tests/unit/helpers/data/pdf/tmp"

    for index, file_name in enumerate(["9000000009/file1.pdf", "9000000009/file2.pdf", "9000000009/file3.pdf"]):
        local_file_path = f"{temp_folder}/{index}.pdf"
        s3_service.download_file(bucket_name, file_name, local_file_path)
        merger.append(local_file_path)

    local_merged_file = f"{temp_folder}/local_merged.pdf"
    merger.write(local_merged_file)

    s3_service.upload_file(local_merged_file, bucket_name, "9000000009/merged_pdf.pdf")
