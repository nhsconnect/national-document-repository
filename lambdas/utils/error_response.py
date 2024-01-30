import json


class ErrorResponse:
    def __init__(self, err_code: str, message: str, interaction_id: str) -> None:
        self.err_code = err_code
        self.message = message
        self.interaction_id = interaction_id

    def create(self) -> str:
        return json.dumps(
            {
                "message": self.message,
                "err_code": self.err_code,
                "interaction_id": self.interaction_id,
            }
        )

    def __eq__(self, other):
        return self.err_code == other.err_code and self.message == other.message
