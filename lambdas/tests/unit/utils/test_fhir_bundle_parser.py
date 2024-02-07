from fhir.resources.STU3.bundle import Bundle
from utils.fhir_bundle_parser import map_bundle_entries_to_dict

with open("tests/unit/data/sqs_messages/gp_change_valid_message.xml") as f:
    _valid_change_of_gp_message = f.read()


def test_map_bundle_entries_to_dict_returns_dict():
    bundle = Bundle.parse_raw(_valid_change_of_gp_message, content_type="text/xml")
    expected_dict_keys = [
        "MessageHeader",
        "HealthcareService",
        "Communication",
        "Patient",
        "Organization",
        "EpisodeOfCare",
    ]
    actual = map_bundle_entries_to_dict(bundle)

    assert list(actual.keys()) == expected_dict_keys
    assert len(actual["Organization"]) == 2
    assert len(actual["MessageHeader"]) == 1
