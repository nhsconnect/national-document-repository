class PatientNotFoundException(Exception):
    pass


class InvalidResourceIdException(Exception):
    pass


class PdsErrorException(Exception):
    pass


class DynamoDbException(Exception):
    pass


class S3DownloadException(Exception):
    pass


class S3UploadException(Exception):
    pass


class ManifestDownloadException(Exception):
    pass


class MissingEnvVarException(Exception):
    pass


class InvalidParamException(Exception):
    pass


class FileProcessingException(Exception):
    pass
