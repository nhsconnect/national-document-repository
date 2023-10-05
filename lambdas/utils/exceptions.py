class PatientNotFoundException(Exception):
    pass


class InvalidResourceIdException(Exception):
    pass


class PdsErrorException(Exception):
    pass


class AuthorisationException(Exception):
    pass


class OrganisationNotFoundException(Exception):
    pass


class OdsErrorException(Exception):
    pass


class DynamoDbException(Exception):
    pass


class ManifestDownloadException(Exception):
    pass
