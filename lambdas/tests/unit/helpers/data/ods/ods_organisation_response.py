from enums.repository_role import OrganisationRelationship

MOCK_GP_NAME = "Mock GP Practice"


ORGANISATION_RESPONSE = {
    "Name": MOCK_GP_NAME,
    "Rels": {
        "Rel": [
            {
                "Date": [{"Type": "Operational", "Start": "2020-10-01"}],
                "Status": "Active",
                "Target": {
                    "OrgId": {
                        "root": "2.16.840.1.113883.2.1.3.2.4.18.48",
                        "assigningAuthorityName": "HSCIC",
                        "extension": "ICB_ODS_CODE",
                    },
                    "PrimaryRoleId": {"id": "RO98", "uniqueRoleId": 131575},
                },
                "id": OrganisationRelationship.COMMISSIONED_BY.value,
                "uniqueRelId": 719187,
            }
        ]
    },
}


RE6_REL_ID_RESPONSE = {
    "Name": MOCK_GP_NAME,
    "Rels": {
        "Rel": [
            {
                "Date": [{"Type": "Operational", "Start": "2020-10-01"}],
                "Status": "Active",
                "Target": {
                    "OrgId": {
                        "root": "2.16.840.1.113883.2.1.3.2.4.18.48",
                        "assigningAuthorityName": "HSCIC",
                        "extension": "ICB_ODS_CODE",
                    },
                    "PrimaryRoleId": {"id": "RO197", "uniqueRoleId": 131575},
                },
                "id": "RE6",
                "uniqueRelId": 719187,
            }
        ]
    },
}

NO_RELS_RESPONSE = {"Name": MOCK_GP_NAME}
