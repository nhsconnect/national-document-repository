from pydantic import BaseModel


class LambdaResponseError(BaseModel):
    type: str
    message: str


class LambdaResponse(BaseModel):
    status: int
    message: str
    errors: list[LambdaResponseError] = []

    def build_response(self):
        response = self.model_dump()
        if not self.errors:
            del response["errors"]
        return response
