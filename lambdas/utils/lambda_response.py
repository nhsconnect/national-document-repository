class ApiGatewayResponse:
    def __init__(self, status_code: int, body: str, methods: str) -> None:
        self.status_code = status_code
        self.body = body
        self.methods = methods

    def create_api_gateway_response(self, headers=None) -> dict:
        if headers is None:
            headers = {}
        return {
            "isBase64Encoded": False,
            "statusCode": self.status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": self.methods,
                "Strict-Transport-Security": "max-age=31536000",
                **headers,
            },
            "body": self.body,
        }

    def __eq__(self, other):
        return (
            self.body == other.body
            and self.status_code == other.status_code
            and self.methods == other.methods
        )
