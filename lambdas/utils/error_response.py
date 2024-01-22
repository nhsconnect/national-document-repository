import json


class ErrorResponse:
    def __init__(self, err_code: str, message: str) -> None:
        self.err_code = err_code
        self.message = message

    def create(self) -> str:
        return json.dumps({"message": self.message, "err_code": self.err_code})

    def __eq__(self, other):
        return self.err_code == other.err_code and self.message == other.message
