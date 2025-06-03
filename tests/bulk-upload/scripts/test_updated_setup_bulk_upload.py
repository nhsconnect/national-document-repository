from updated_setup_bulk_upload import create_test_file_names_and_keys


def test_create_test_file_names_and_keys_returns_correct_filename_and_keys():
    expected = True

    actual = create_test_file_names_and_keys()

    assert actual == expected
