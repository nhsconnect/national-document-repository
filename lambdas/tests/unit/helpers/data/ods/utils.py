import json


def load_ods_response_data():
    mock_responses = {}

    test_cases = [
        "with_valid_gp_role",
        "with_valid_pcse_role",
        "with_multiple_valid_roles",
        "with_no_valid_roles",
    ]

    for test_case in test_cases:
        with open(f"tests/unit/helpers/data/ods/ods_response_{test_case}.json") as f:
            mock_responses[test_case] = json.load(f)

    return mock_responses
