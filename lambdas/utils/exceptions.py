class PatientNotFoundException(Exception):
    pass


class InvalidResourceIdException(Exception):
    pass


class PdsErrorException(Exception):
    pass


class DynamoDbException(Exception):
    pass
