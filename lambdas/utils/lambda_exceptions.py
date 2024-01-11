class LambdaException(Exception):
    def __init__(self, status_code, message, err_code: str | None = None):
        self.status_code = status_code
        self.err_code = err_code
        self.message = message

    def __str__(self):
        return repr(self.err_code + ": " + self.message)


class CreateDocumentRefException(LambdaException):
    pass


class SearchPatientException(LambdaException):
    def __init__(self, status_code, message):
        LambdaException.__init__(self, status_code, message, "ERR_SEARCH")


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
