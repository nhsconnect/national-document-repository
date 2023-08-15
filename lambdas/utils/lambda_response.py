class ApiGatewayResponse:
    def __init__(self, status_code, body, methods) -> None:
        self.status_code = status_code
        self.body = body
        self.methods = methods

    def create_api_gateway_response(self):
        return {
            "isBase64Encoded": False,
            "statusCode": self.status_code,
            "headers": {
                "Content-Type": "application/fhir+json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": self.methods,
            },
            "body": self.body,
        }
