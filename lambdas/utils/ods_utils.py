"""
On PDS, GP ODS codes must be 6 characters long, see the 'epraccur' document here for info:
https://digital.nhs.uk/services/organisation-data-service/export-data-files/csv-downloads/gp-and-gp-practice-related-data

Sometimes, a patient will not have a generalPractitioner on PDS. Internally, we can also add "SUSP", "DECE" codes to
mark suspended and deceased patients for reporting purposes. The only values that should be considered 'active' is a
valid ODS code.
"""
def is_ods_code_active(gp_ods) -> bool:
    if gp_ods in PatientOdsInactiveStatus.list():
        return False

    return len(gp_ods or '') == 6