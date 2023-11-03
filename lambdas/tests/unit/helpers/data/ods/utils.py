import json


def load_ods_response_data():
    mock_responses = {}

    test_cases = [
        "gp_org",
        "ods_response_pcse_org",
        "not_gp_or_pcse",
    ]

    for test_case in test_cases:
        with open(f"tests/unit/helpers/data/ods/ods_response_{test_case}.json") as f:
            mock_responses[test_case] = json.load(f)

    return mock_responses
