class LambdaException(Exception):
    def __init__(
        self,
        status_code,
        err_code: str,
        message: str | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.err_code = err_code


class CreateDocumentRefException(LambdaException):
    pass


class SearchPatientException(LambdaException):
    pass


class InvalidDocTypeException(LambdaException):
    pass


class LoginRedirectException(LambdaException):
    pass


class DocumentManifestServiceException(LambdaException):
    pass


class LoginException(LambdaException):
    pass


class LGStitchServiceException(LambdaException):
    pass


class DocumentRefSearchException(LambdaException):
    pass


class DocumentDeletionServiceException(LambdaException):
    pass
