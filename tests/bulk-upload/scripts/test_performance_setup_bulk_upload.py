import os
import sys
import tempfile
from datetime import date
from unittest.mock import patch

import pytest
from performance_setup_bulk_upload import (
    S3_STORAGE_CLASS,
    STAGING_BUCKET,
    build_file_path,
    build_metadata_csv_row,
    check_confirmation,
    create_test_file_keys_and_metadata_rows,
    delete_file_from_staging,
    generate_file_name,
    generate_nhs_number,
    generate_random_name,
    get_user_input,
    inflate_pdf_file,
    pairing_nhs_number_digit,
    upload_lg_files_to_staging,
    upload_metadata_to_s3,
    upload_source_file_to_staging,
)


def test_generate_random_name_format():
    name = generate_random_name()
    assert len(name.split()) == 2


@pytest.mark.parametrize(
    "nhs_base, expected",
    [
        (123456789, -1),
        (111111111, 1),
        (123456782, 2),
        (123456780, 6),
        (0, -1),
        (999999999, 9),
    ],
)
def test_pairing_nhs_number_digit(nhs_base, expected):
    assert pairing_nhs_number_digit(nhs_base) == expected


@pytest.mark.parametrize(
    "input_nhs_number, mock_return_values, expected_output",
    [
        ("1234567880", [1], "1234567891"),
        ("1234567890", [-1, -1, 5], "1234567925"),
        ("0000000000", [-1, 0], "0000000020"),
        ("9999999999", [-1, -1, -1, 1], "9999999999"),
    ],
)
def test_generate_nhs_number(
    mocker, input_nhs_number, mock_return_values, expected_output
):
    mocker.patch(
        "performance_setup_bulk_upload.pairing_nhs_number_digit",
        side_effect=mock_return_values,
    )
    result = generate_nhs_number(input_nhs_number)
    assert result == expected_output


@pytest.mark.parametrize(
    "current_file_number, number_of_files, person_name, nhs_number, expected",
    [
        (
            1,
            5,
            "Alice Smith",
            "1234567890",
            "1of5_Lloyd_George_Record_[Alice Smith]_[1234567890]_[22-10-2010].pdf",
        ),
        (
            10,
            10,
            "Bob",
            "9876543210",
            "10of10_Lloyd_George_Record_[Bob]_[9876543210]_[22-10-2010].pdf",
        ),
        (
            3,
            7,
            "Élodie",
            "0001112223",
            "3of7_Lloyd_George_Record_[Élodie]_[0001112223]_[22-10-2010].pdf",
        ),
        (
            0,
            1,
            "Test User",
            "9999999999",
            "0of1_Lloyd_George_Record_[Test User]_[9999999999]_[22-10-2010].pdf",
        ),
    ],
)
def test_generate_file_name(
    current_file_number, number_of_files, person_name, nhs_number, expected
):
    assert (
        generate_file_name(
            current_file_number, number_of_files, person_name, nhs_number
        )
        == expected
    )


@pytest.mark.parametrize(
    "nhs_number, file_name, expected",
    [
        ("1234567890", "file1.pdf", "1234567890/file1.pdf"),
        ("9999999999", "", "9999999999/"),
        ("", "empty_nhs.pdf", "/empty_nhs.pdf"),
    ],
)
def test_build_file_path(nhs_number, file_name, expected):
    assert build_file_path(nhs_number, file_name) == expected


def test_create_test_file_keys_and_metadata_rows_calls(mocker):
    mock_generate_random_name = mocker.patch(
        "performance_setup_bulk_upload.generate_random_name", return_value="Alice"
    )
    mock_generate_nhs_number = mocker.patch(
        "performance_setup_bulk_upload.generate_nhs_number",
        side_effect=lambda number: number + "1",
    )
    mock_generate_file_name = mocker.patch(
        "performance_setup_bulk_upload.generate_file_name", return_value="file1.pdf"
    )
    mock_build_file_path = mocker.patch(
        "performance_setup_bulk_upload.build_file_path", return_value="NH123/file1.pdf"
    )
    mock_build_metadata_csv_row = mocker.patch(
        "performance_setup_bulk_upload.build_metadata_csv_row", return_value="row"
    )

    requested_patients_number = 2
    number_of_files_for_each_patient = 3

    create_test_file_keys_and_metadata_rows(
        requested_patients_number=requested_patients_number,
        number_of_files_for_each_patient=number_of_files_for_each_patient,
    )

    assert mock_generate_random_name.call_count == requested_patients_number
    assert mock_generate_nhs_number.call_count == requested_patients_number

    expected_file_calls = requested_patients_number * number_of_files_for_each_patient
    assert mock_generate_file_name.call_count == expected_file_calls
    assert mock_build_file_path.call_count == expected_file_calls
    assert mock_build_metadata_csv_row.call_count == expected_file_calls


def test_inflate_pdf_file_creates_file_with_expected_size():
    target_size_mb = 0.5
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as source:
        source.write(b"%PDF-1.4\n%Mock content\n")
        source_path = source.name

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as target:
        target_path = target.name

    try:
        inflate_pdf_file(source_path, target_path, target_size_mb)

        expected_min_size = int(target_size_mb * 1024 * 1024)
        actual_size = os.path.getsize(target_path)
        assert (
            actual_size >= expected_min_size
        ), f"Expected at least {expected_min_size} bytes, got {actual_size} bytes"

    finally:
        os.remove(source_path)
        os.remove(target_path)


def test_upload_source_file_to_staging_calls(mocker):
    current_dir = os.path.dirname(__file__)
    source_pdf_path = os.path.abspath(
        os.path.join(current_dir, "..", "source_to_copy_from.pdf")
    )
    file_key = "1234567890/test.pdf"

    mock_client = mocker.patch("performance_setup_bulk_upload.client")
    mocker.patch("performance_setup_bulk_upload.STAGING_BUCKET", "test-bucket")
    mocker.patch(
        "performance_setup_bulk_upload.S3_STORAGE_CLASS", "INTELLIGENT_TIERING"
    )
    mocker.patch(
        "performance_setup_bulk_upload.S3_SCAN_TAGS",
        [{"Key": "ScanStatus", "Value": "Clean"}],
    )

    upload_source_file_to_staging(source_pdf_path, file_key)

    assert mock_client.put_object.call_count == 1
    assert mock_client.put_object_tagging.call_count == 1


def test_delete_file_from_staging_calls_client_delete_object_once():
    file_key = "some/file/key.pdf"

    with patch("performance_setup_bulk_upload.client") as mock_client:
        delete_file_from_staging(file_key)

        calls = mock_client.delete_object.call_count
        assert calls == 1, f"Expected 1 call to delete_object, got {calls}"


def test_upload_lg_files_to_staging_calls_client_methods(mocker):
    mock_client = mocker.patch("performance_setup_bulk_upload.client")

    lg_file_keys = ["file1.pdf", "file2.pdf", "file3.pdf"]
    source_pdf_file_key = "source.pdf"

    upload_lg_files_to_staging(lg_file_keys, source_pdf_file_key)

    assert mock_client.copy_object.call_count == 3
    assert mock_client.put_object_tagging.call_count == 3


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("Y", True),
        ("y", True),
        ("Yes", True),
        ("YES", True),
        ("  yEs  ", True),
        ("n", False),
        ("No", False),
        ("yeah", False),
        ("", False),
        ("maybe", False),
    ],
)
def test_check_confirmation(input_str, expected):
    assert check_confirmation(input_str) is expected


def test_get_user_input_with_mocker(mocker):
    test_args = [
        "script_name",
        "--environment",
        "prod",
        "--delete-table",
        "--download-data",
        "--build-files",
        "--num-patients",
        "100",
        "--num-files",
        "5",
        "--file-size",
        "1.5",
        "--empty-lloydgeorge-store",
        "--upload",
    ]

    mocker.patch.object(sys, "argv", test_args)

    args = get_user_input()

    assert args.environment == "prod"
    assert args.delete_table is True
    assert args.download_data is True
    assert args.build_files is True
    assert args.num_patients == "100"
    assert args.num_files == "5"
    assert args.file_size == 1.5
    assert args.empty_lloydgeorge_store is True
    assert args.upload is True


def test_build_metadata_csv_row():
    file_key = "some/path/file.pdf"
    file_count = 3
    nhs_number = "1234567890"

    expected_date = date.today().strftime("%d/%m/%Y")
    expected_row = ",".join(
        [
            file_key,
            str(file_count),
            "M85143",
            nhs_number,
            "LG",
            "",
            "01/01/2023",
            "NEC",
            "NEC",
            expected_date,
        ]
    )

    result = build_metadata_csv_row(file_key, file_count, nhs_number)
    assert result == expected_row


def test_upload_metadata_to_s3_calls_put_object_with_correct_args(mocker):
    test_body = "some,csv,content\n1,2,3"

    mock_client = mocker.patch("performance_setup_bulk_upload.client")

    upload_metadata_to_s3(test_body)

    mock_client.put_object.assert_called_once_with(
        Bucket=STAGING_BUCKET,
        Key="metadata.csv",
        Body=test_body,
        ContentType="text/csv",
        StorageClass=S3_STORAGE_CLASS,
    )
