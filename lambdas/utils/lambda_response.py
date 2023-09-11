class ApiGatewayResponse:
    def __init__(self, status_code, body, methods, **headers) -> None:
        self.status_code = status_code
        self.body = body
        self.methods = methods
        self.headers = headers

    def create_api_gateway_response(self):
        return {
            "isBase64Encoded": False,
            "statusCode": self.status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": self.methods,
                ** self.headers
            },
            "body": self.body,
        }

    def __eq__(self, other):
        return (
            self.body == other.body
            and self.status_code == other.status_code
            and self.methods == other.methods
        )
