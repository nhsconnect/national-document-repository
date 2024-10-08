import copy

PDS_PATIENT = {
    "resourceType": "Patient",
    "id": "9000000009",
    "meta": {
        "versionId": "2",
        "security": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
                "code": "U",
                "display": "unrestricted",
            }
        ],
    },
    "name": [
        {
            "id": "123",
            "use": "usual",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "given": ["Jane"],
            "family": "Smith",
            "prefix": ["Mrs"],
            "suffix": ["MBE"],
        },
        {
            "id": "1234",
            "use": "other",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "given": ["Jim"],
            "family": "Stevens",
            "prefix": ["Mr"],
            "suffix": ["MBE"],
        },
    ],
    "gender": "female",
    "birthDate": "2010-10-22",
    "multipleBirthInteger": 1,
    "generalPractitioner": [
        {
            "id": "254406A3",
            "type": "Organization",
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "Y12345",
                "period": {"start": "2020-01-01"},
            },
        }
    ],
    "managingOrganization": {
        "type": "Organization",
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "Y12345",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
        },
    },
    "extension": [
        {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NominatedPharmacy",
            "valueReference": {
                "identifier": {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "Y12345",
                }
            },
        },
        {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-PreferredDispenserOrganization",
            "valueReference": {
                "identifier": {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "Y23456",
                }
            },
        },
        {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-MedicalApplianceSupplier",
            "valueReference": {
                "identifier": {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "Y34567",
                }
            },
        },
        {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication",
            "extension": [
                {
                    "url": "language",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-HumanLanguage",
                                "version": "1.0.0",
                                "code": "fr",
                                "display": "French",
                            }
                        ]
                    },
                },
                {"url": "interpreterRequired", "valueBoolean": "True"},
            ],
        },
        {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ContactPreference",
            "extension": [
                {
                    "url": "PreferredWrittenCommunicationFormat",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-PreferredWrittenCommunicationFormat",
                                "code": "12",
                                "display": "Braille",
                            }
                        ]
                    },
                },
                {
                    "url": "PreferredContactMethod",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-PreferredContactMethod",
                                "code": "1",
                                "display": "Letter",
                            }
                        ]
                    },
                },
                {"url": "PreferredContactTimes", "valueString": "Not after 7pm"},
            ],
        },
        {
            "url": "http://hl7.org/fhir/StructureDefinition/patient-birthPlace",
            "valueAddress": {
                "city": "Manchester",
                "district": "Greater Manchester",
                "country": "GBR",
            },
        },
        {
            "url": "https://fhir.nhs.uk/StructureDefinition/Extension-PDS-RemovalFromRegistration",
            "extension": [
                {
                    "url": "removalFromRegistrationCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/CodeSystem/PDS-RemovalReasonExitCode",
                                "code": "SCT",
                                "display": "Transferred to Scotland",
                            }
                        ]
                    },
                },
                {
                    "url": "effectiveTime",
                    "valuePeriod": {
                        "start": "2020-01-01T00:00:00+00:00",
                        "end": "2021-12-31T00:00:00+00:00",
                    },
                },
            ],
        },
    ],
    "address": [
        {
            "id": "456",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "use": "home",
            "line": [
                "1 Trevelyan Square",
                "Boar Lane",
                "City Centre",
                "Leeds",
                "West Yorkshire",
            ],
            "postalCode": "LS1 6AE",
            "extension": [
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey",
                    "extension": [
                        {
                            "url": "type",
                            "valueCoding": {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AddressKeyType",
                                "code": "PAF",
                            },
                        },
                        {"url": "value", "valueString": "12345678"},
                    ],
                },
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey",
                    "extension": [
                        {
                            "url": "type",
                            "valueCoding": {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AddressKeyType",
                                "code": "UPRN",
                            },
                        },
                        {"url": "value", "valueString": "123456789012"},
                    ],
                },
            ],
        },
        {
            "id": "T456",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "use": "temp",
            "text": "Student Accommodation",
            "line": [
                "1 Trevelyan Square",
                "Boar Lane",
                "City Centre",
                "Leeds",
                "West Yorkshire",
            ],
            "postalCode": "LS1 6AE",
            "extension": [
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey",
                    "extension": [
                        {
                            "url": "type",
                            "valueCoding": {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AddressKeyType",
                                "code": "PAF",
                            },
                        },
                        {"url": "value", "valueString": "12345678"},
                    ],
                },
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey",
                    "extension": [
                        {
                            "url": "type",
                            "valueCoding": {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AddressKeyType",
                                "code": "UPRN",
                            },
                        },
                        {"url": "value", "valueString": "123456789012"},
                    ],
                },
            ],
        },
    ],
}

PDS_PATIENT_RESTRICTED = {
    "resourceType": "Patient",
    "id": "9000000025",
    "identifier": [
        {
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": "9000000025",
            "extension": [
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatus",
                                "version": "1.0.0",
                                "code": "01",
                                "display": "Number present and verified",
                            }
                        ]
                    },
                }
            ],
        }
    ],
    "meta": {
        "versionId": "2",
        "security": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
                "code": "R",
                "display": "restricted",
            }
        ],
    },
    "name": [
        {
            "id": "123",
            "use": "usual",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "given": ["Janet"],
            "family": "Smythe",
            "prefix": ["Mrs"],
            "suffix": ["MBE"],
        }
    ],
    "gender": "female",
    "birthDate": "2010-10-22",
    "multipleBirthInteger": 1,
    "extension": [],
}
PDS_PATIENT_WITHOUT_ACTIVE_GP = {
    "resourceType": "Patient",
    "id": "9000000009",
    "meta": {
        "versionId": "2",
        "security": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
                "code": "U",
                "display": "unrestricted",
            }
        ],
    },
    "name": [
        {
            "id": "123",
            "use": "usual",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "given": ["Jane"],
            "family": "Smith",
            "prefix": ["Mrs"],
            "suffix": ["MBE"],
        },
        {
            "id": "1234",
            "use": "other",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "given": ["Jim"],
            "family": "Stevens",
            "prefix": ["Mr"],
            "suffix": ["MBE"],
        },
    ],
    "gender": "female",
    "birthDate": "2010-10-22",
    "multipleBirthInteger": 1,
    "generalPractitioner": [],
    "managingOrganization": {
        "type": "Organization",
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "Y12345",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
        },
    },
}

PDS_PATIENT_WITH_GP_END_DATE = {
    "resourceType": "Patient",
    "id": "9000000009",
    "meta": {
        "versionId": "2",
        "security": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
                "code": "U",
                "display": "unrestricted",
            }
        ],
    },
    "name": [
        {
            "id": "123",
            "use": "usual",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "given": ["Jane"],
            "family": "Smith",
            "prefix": ["Mrs"],
            "suffix": ["MBE"],
        },
        {
            "id": "1234",
            "use": "other",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
            "given": ["Jim"],
            "family": "Stevens",
            "prefix": ["Mr"],
            "suffix": ["MBE"],
        },
    ],
    "gender": "female",
    "birthDate": "2010-10-22",
    "multipleBirthInteger": 1,
    "generalPractitioner": [
        {
            "id": "254406A3",
            "type": "Organization",
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "Y12345",
                "period": {"start": "2020-01-01", "end": "2021-12-31"},
            },
        }
    ],
    "managingOrganization": {
        "type": "Organization",
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "Y12345",
            "period": {"start": "2020-01-01", "end": "2021-12-31"},
        },
    },
}
PDS_PATIENT_WITH_MIDDLE_NAME = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_WITH_MIDDLE_NAME["name"][0]["given"].append("Jake")

PDS_PATIENT_WITHOUT_ADDRESS = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_WITHOUT_ADDRESS.pop("address")

PDS_PATIENT_NO_PERIOD_IN_NAME_MODEL = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_NO_PERIOD_IN_NAME_MODEL["name"] = [
    {
        "id": "123",
        "use": "usual",
        "given": ["Jane"],
        "family": "Smith",
    },
]

PDS_PATIENT_NO_GIVEN_NAME_IN_HISTORIC_NAME = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_NO_GIVEN_NAME_IN_HISTORIC_NAME["name"] = [
    {
        "id": "123",
        "use": "usual",
        "period": {"start": "2022-01-01"},
        "given": ["Jane"],
        "family": "Smith",
        "prefix": ["Mrs"],
        "suffix": ["MBE"],
    },
    {
        "id": "1234",
        "use": "other",
        "period": {"start": "2020-01-01", "end": "2021-12-31"},
        "family": "Stevens",
    },
]


PDS_PATIENT_NO_GIVEN_NAME_IN_CURRENT_NAME = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_NO_GIVEN_NAME_IN_CURRENT_NAME["name"] = [
    {
        "id": "123",
        "use": "usual",
        "period": {"start": "2022-01-01"},
        "family": "Smith",
        "prefix": ["Mrs"],
        "suffix": ["MBE"],
    },
    {
        "id": "1234",
        "use": "other",
        "period": {"start": "2020-01-01", "end": "2021-12-31"},
        "given": ["Jim"],
        "family": "Stevens",
        "prefix": ["Mr"],
        "suffix": ["MBE"],
    },
]

PDS_PATIENT_NO_PERIOD_IN_GENERAL_PRACTITIONER_IDENTIFIER = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_NO_PERIOD_IN_GENERAL_PRACTITIONER_IDENTIFIER["generalPractitioner"] = [
    {
        "id": "254406A3",
        "type": "Organization",
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "H81109",
        },
    },
    {
        "id": "254406A3",
        "type": "Organization",
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "Y12345",
            "period": {"start": "2020-01-01"},
        },
    },
]

DECEASED_DATE_TIME = "2010-10-22T00:00:00+00:00"

PDS_PATIENT_DECEASED_FORMAL = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_DECEASED_FORMAL["deceasedDateTime"] = DECEASED_DATE_TIME
PDS_PATIENT_DECEASED_FORMAL["extension"].append(
    {
        "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus",
        "extension": [
            {
                "url": "deathNotificationStatus",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-DeathNotificationStatus",
                            "version": "1.0.0",
                            "code": "2",
                            "display": "Formal - death notice received from Registrar of Deaths",
                        }
                    ]
                },
            },
            {
                "url": "systemEffectiveDate",
                "valueDateTime": DECEASED_DATE_TIME,
            },
        ],
    }
)
PDS_PATIENT_DECEASED_FORMAL.pop("generalPractitioner")

PDS_PATIENT_DECEASED_INFORMAL = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_DECEASED_INFORMAL["deceasedDateTime"] = DECEASED_DATE_TIME
PDS_PATIENT_DECEASED_INFORMAL["extension"].append(
    {
        "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus",
        "extension": [
            {
                "url": "deathNotificationStatus",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-DeathNotificationStatus",
                            "version": "1.0.0",
                            "code": "1",
                            "display": "Informal - death notice received via an update from a local NHS "
                            "Organisation such as GENERAL PRACTITIONER or NHS Trust",
                        }
                    ]
                },
            },
            {
                "url": "systemEffectiveDate",
                "valueDateTime": DECEASED_DATE_TIME,
            },
        ],
    }
)

PDS_PATIENT_SUSPENDED = copy.deepcopy(PDS_PATIENT)
PDS_PATIENT_SUSPENDED["generalPractitioner"][0]["identifier"].pop("period")
