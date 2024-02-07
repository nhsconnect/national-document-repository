from enums.fhir_resource_types import FHIR_RESOURCE_TYPES
from fhir.resources.STU3.bundle import Bundle
from utils.fhir_bundle_parser import get_bundle_entry, map_bundle_entries_to_dict

with open("tests/unit/data/sqs_messages/invalid_message_with_no_header.xml") as f:
    _message_with_no_header = f.read()
with open("tests/unit/data/sqs_messages/address_change_valid_message.xml") as f:
    _valid_non_change_of_gp_message = f.read()
with open("tests/unit/data/sqs_messages/gp_change_valid_message.xml") as f:
    _valid_change_of_gp_message = f.read()


def test_get_bundle_entry_returns_none():
    bundle = Bundle.parse_raw(_message_with_no_header, content_type="text/xml")
    expected = None

    actual = get_bundle_entry(bundle, FHIR_RESOURCE_TYPES.MessageHeader)
    assert expected == actual


def test_get_bundle_entry_returns_entry():
    bundle = Bundle.parse_raw(_valid_change_of_gp_message, content_type="text/xml")
    expected = bundle.entry[0]

    actual = get_bundle_entry(bundle, FHIR_RESOURCE_TYPES.MessageHeader)
    assert expected == actual


def test_get_bundle_entries_returns_none():
    bundle = Bundle.parse_raw(_message_with_no_header, content_type="text/xml")
    expected = None

    actual = get_bundle_entry(bundle, FHIR_RESOURCE_TYPES.MessageHeader)
    assert expected == actual


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
