class ApiGatewayResponse:
    def __init__(
        self, status_code: int, body: str, methods: str, err_code: str | None = None
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.err_code = err_code
        self.methods = methods

    def create_api_gateway_response(self, headers=None) -> dict:
        if headers is None:
            headers = {}
        res = {
            "isBase64Encoded": False,
            "statusCode": self.status_code,
            "errCode": self.err_code or "OK",
            "headers": {
                "Content-Type": "application/fhir+json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": self.methods,
                "Strict-Transport-Security": "max-age=63072000",
                **headers,
            },
            "body": self.body,
        }
        return res

    def __eq__(self, other):
        return (
            self.status_code == other.status_code
            and self.body == other.body
            and self.methods == other.methods
            and self.err_code == other.err_code
        )
