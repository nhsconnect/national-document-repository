from models.document import Document

NHS_NUMBER = "1111111111"

TEST_ARF_DOCS = [
    Document(
        NHS_NUMBER,
        "document.csv",
        "Clean",
        file_location="s3://test-bucket/test-key-123",
    ),
    Document(
        NHS_NUMBER,
        "results.pdf",
        "Clean",
        file_location="s3://test-bucket/test-key-456",
    ),
    Document(
        NHS_NUMBER,
        "output.csv",
        "Clean",
        file_location="s3://test-bucket/test-key-789",
    ),
]
TEST_LG_DOCS = [
    Document(
        NHS_NUMBER,
        "lg-file.csv",
        "Clean",
        file_location="s3://prmd-110-zip-test/00000000-0000-0000-0000-000000000004",
    ),
    Document(
        NHS_NUMBER,
        "lg-document.csv",
        "Clean",
        file_location="s3://prmd-110-zip-test/00000000-0000-0000-0000-000000000005",
    ),
    Document(
        NHS_NUMBER,
        "lg-results.csv",
        "Clean",
        file_location="s3://prmd-110-zip-test/00000000-0000-0000-0000-000000000006",
    ),
]
