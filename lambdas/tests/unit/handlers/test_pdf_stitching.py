# import os
# from datetime import datetime
# from io import BytesIO
# from pypdf import PdfWriter
# import boto3
#
# from services.s3_service import S3Service
#
#
# def test_pdf_stitching():
#     merger = PdfWriter()
#     print("FILE PATH HERE! " + os.path.abspath(__file__))
#     for file_name in ["file1.pdf", "file2.pdf", "file3.pdf"]:
#         file_path = f"../../tests/unit/helpers/data/pdf/{file_name}"
#         merger.append(file_path)
#
#     # merger.write("tests/unit/helpers/data/pdf/output.pdf")
#     # merger.close()
#
#     with BytesIO() as bytes_stream:
#         merger.write(bytes_stream)
#         bytes_stream.seek(0)
#
#         s3_client = boto3.client("s3", region_name="eu-west-2")
#         response = s3_client.put_object(
#             Body=bytes_stream,
#             Bucket="ndr-dev-lloyd-george-store",
#             Expires=datetime(2015, 9, 27),
#             Key="alexCool.pdf",
#         )
#
#     print(response)
#
#
# def test_pdf_stitching_with_s3():
#     s3_service = S3Service()
#     merger = PdfWriter()
#     bucket_name = "ndra-lloyd-george-store"
#     temp_folder = "tests/unit/helpers/data/pdf/tmp"
#
#     for index, file_name in enumerate(
#         ["9000000009/file1.pdf", "9000000009/file2.pdf", "9000000009/file3.pdf"]
#     ):
#         local_file_path = f"{temp_folder}/{index}.pdf"
#         s3_service.download_file(bucket_name, file_name, local_file_path)
#         merger.append(local_file_path)
#
#     # local_merged_file = f"{temp_folder}/local_merged.pdf"
#     # merger.write(local_merged_file)
#
#     with BytesIO() as bytes_stream:
#         merger.write(bytes_stream)
#         bytes_stream.seek(0)
#
#         s3_client = boto3.client("s3", region_name="eu-west-2")
#         response = s3_client.put_object(
#             Body=bytes_stream,
#             Bucket="ndr-dev-lloyd-george-store",
#             Expires=datetime(2015, 9, 27),
#             Key="alexCool.pdf",
#         )
#         print(response)
#
#     # s3_service.upload_file("AlexTest,pdf", bucket_name, "9000000009/merged_pdf.pdf")
