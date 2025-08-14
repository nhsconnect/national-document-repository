from typing import Callable

import jwt
from utils.request_context import request_context


def set_request_context_for_logging(lambda_func: Callable) -> Callable:
    def interceptor(event, context):
        request_context.request_id = context.aws_request_id or None
        request_context.authorization = None
        headers = event.get("headers")
        if headers:
            token = headers.get("Authorization")
            if token:
                try:
                    decoded_token = jwt.decode(
                        token, algorithms=["RS256"], options={"verify_signature": False}
                    )
                    request_context.authorization = decoded_token
                except jwt.PyJWTError:
                    pass
            correlation_id = headers.get("X-Correlation-Id")
            if correlation_id:
                request_context.correlation_id = correlation_id
        return lambda_func(event, context)

    return interceptor
