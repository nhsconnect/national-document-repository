from utils.lambda_response import ApiGatewayResponse


def check_manual_error_conditions(error_type: str, http_method: str = "GET"):
    if error_type == "TIMEOUT":
        trigger_timeout_error()
    if error_type == "MEMORY":
        trigger_memory_error()
    if error_type == "400":
        return trigger_400(http_method)
    if error_type == "500":
        return trigger_500(http_method)


# no unit test as don't want to slow down test suite, tested in AWS
def trigger_memory_error():
    memory_break_string = "string_length_to_double_each_iteration"
    for _ in range(1000000000000000000000000000000000):
        memory_break_string = memory_break_string + memory_break_string


# no unit test as don't want to slow down test suite, tested in AWS
def trigger_timeout_error():
    memory_break_string = "string_to_set_each_iteration"
    for _ in range(1000000000000000000000000000000000):
        memory_break_string = memory_break_string


def trigger_400(http_method):
    return ApiGatewayResponse(400, "", http_method).create_api_gateway_response()


def trigger_500(http_method):
    return ApiGatewayResponse(500, "", http_method).create_api_gateway_response()
