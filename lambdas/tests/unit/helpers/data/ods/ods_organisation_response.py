from enums.repository_role import OrganisationRelationship

NON_BSOL_ORGANISATION_RESPONSE = {
    "Name": "Mock GP Practice",
    "Rels": {
        "Rel": [
            {
                "Date": [{"Type": "Operational", "Start": "2020-10-01"}],
                "Status": "Active",
                "Target": {
                    "OrgId": {
                        "root": "2.16.840.1.113883.2.1.3.2.4.18.48",
                        "assigningAuthorityName": "HSCIC",
                        "extension": "RXK",
                    },
                    "PrimaryRoleId": {"id": "RO197", "uniqueRoleId": 131575},
                },
                "id": "RE6",
                "uniqueRelId": 719187,
            }
        ]
    },
}


BSOL_ORGANISATION_RESPONSE = {
    "Name": "Mock GP Practice",
    "Rels": {
        "Rel": [
            {
                "Date": [{"Type": "Operational", "Start": "2020-10-01"}],
                "Status": "Active",
                "Target": {
                    "OrgId": {
                        "root": "2.16.840.1.113883.2.1.3.2.4.18.48",
                        "assigningAuthorityName": "HSCIC",
                        "extension": OrganisationRelationship.BSOL_ORG_ID.value,
                    },
                    "PrimaryRoleId": {"id": "RO197", "uniqueRoleId": 131575},
                },
                "id": OrganisationRelationship.BSOL_REL_ID.value,
                "uniqueRelId": 719187,
            }
        ]
    },
}


RE6_REL_ID_RESPONSE = {
    "Name": "Mock GP Practice",
    "Rels": {
        "Rel": [
            {
                "Date": [{"Type": "Operational", "Start": "2020-10-01"}],
                "Status": "Active",
                "Target": {
                    "OrgId": {
                        "root": "2.16.840.1.113883.2.1.3.2.4.18.48",
                        "assigningAuthorityName": "HSCIC",
                        "extension": OrganisationRelationship.BSOL_ORG_ID.value,
                    },
                    "PrimaryRoleId": {"id": "RO197", "uniqueRoleId": 131575},
                },
                "id": "RE6",
                "uniqueRelId": 719187,
            }
        ]
    },
}

NO_RELS_RESPONSE = {"Name": "Mock GP Practice"}
