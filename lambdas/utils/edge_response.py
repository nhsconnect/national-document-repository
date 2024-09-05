class EdgeResponse:
    def __init__(self, status_code: int, body: str, methods: str) -> None:
        self.status_code = status_code
        self.body = body
        self.methods = methods

    def create_edge_response(self, headers=None) -> dict:
        if headers is None:
            headers = {}
        return {
            "isBase64Encoded": False,
            "status": self.status_code,
            "headers": {
                "content-type": [
                    {"key": "Content-Encoding", "value": "application/fhir+json"}
                ],
                "content-encoding": [{"key": "Content-Encoding", "value": "UTF-8"}],
            },
            "body": self.body,
        }

    def __eq__(self, other):
        return (
            self.status_code == other.status_code
            and self.body == other.body
            and self.methods == other.methods
        )
