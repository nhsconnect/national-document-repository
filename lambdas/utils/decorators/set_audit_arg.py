from typing import Callable

import jwt

from utils.request_context import request_context


def set_request_context_for_logging(lambda_func: Callable) -> Callable:
    def interceptor(event, context):
        request_context.request_id = context.aws_request_id
        request_context.authorization = None
        if event.get("headers"):
            token = event.get("headers").get("Authorization")
            decoded_token = jwt.decode(
                token, algorithms=["RS256"], options={"verify_signature": False}
            )
            request_context.authorization = decoded_token
        return lambda_func(event, context)

    return interceptor
