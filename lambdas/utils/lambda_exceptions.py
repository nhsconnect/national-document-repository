class LambdaException(Exception):
    def __init__(
        self,
        status_code,
        message: str | None = None,
        err_code: str | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.err_code = err_code

    def __str__(self):
        return repr("Error': " + self.error_code)


class CreateDocumentRefException(LambdaException):
    def __init__(self, status_code, err_code, message):
        LambdaException.__init__(self, status_code, message, err_code)


class SearchPatientException(LambdaException):
    def __init__(self, status_code, err_code, message):
        LambdaException.__init__(self, status_code, message, err_code)


class InvalidDocTypeException(LambdaException):
    def __init__(self, status_code, err_code, message):
        LambdaException.__init__(self, status_code, message, err_code)


class LoginRedirectException(LambdaException):
    def __init__(self, status_code, err_code, message):
        LambdaException.__init__(self, status_code, message, err_code)


class DocumentManifestServiceException(LambdaException):
    def __init__(self, status_code, err_code, message):
        LambdaException.__init__(self, status_code, message, err_code)


class LoginException(LambdaException):
    def __init__(self, status_code, err_code, message):
        LambdaException.__init__(self, status_code, message, err_code)


class LGStitchServiceException(LambdaException):
    pass


class DocumentRefSearchException(LambdaException):
    pass


class DocumentDeletionServiceException(LambdaException):
    pass
