
# def test_prepare_redirect_response_return_303_with_correct_headers(mocker, monkeypatch):
#     monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
#     mock_dynamo_service = mocker.patch(
#         "handlers.login_redirect_handler.save_state_in_dynamo_db"
#     )
#     mock_ssm_service = mocker.patch(
#         "handlers.login_redirect_handler.get_ssm_parameters",
#         return_value=MOCK_MULTI_STRING_PARAMETERS_RESPONSE,
#     )
#
#     response = login_redirect_handler.prepare_redirect_response(FakeWebAppClient)
#     location_header = {"Location": RETURN_URL}
#
#     expected = ApiGatewayResponse(303, "", "GET").create_api_gateway_response(
#         headers=location_header
#     )
#
#     assert response == expected
#     mock_dynamo_service.assert_called_with("test1state")
#     mock_ssm_service.assert_called_once()
#
#
# def test_prepare_redirect_response_return_500_when_boto3_client_failing(
#     mocker, monkeypatch
# ):
#     monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
#     mock_dynamo_service = mocker.patch(
#         "handlers.login_redirect_handler.save_state_in_dynamo_db"
#     )
#     mock_ssm_service = mocker.patch(
#         "handlers.login_redirect_handler.get_ssm_parameters",
#         side_effect=ClientError(
#             {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
#         ),
#     )
#     response = login_redirect_handler.prepare_redirect_response(FakeWebAppClient)
#
#     expected = ApiGatewayResponse(
#         500, "Server error", "GET"
#     ).create_api_gateway_response()
#
#     assert response == expected
#     mock_dynamo_service.assert_not_called()
#     mock_ssm_service.assert_called_once()
#
#
# def test_prepare_redirect_response_return_500_when_auth_client_failing(
#     mocker, monkeypatch
# ):
# monkeypatch.setenv("OIDC_CALLBACK_URL", "https://www.testexample.com")
# mock_dynamo_service = mocker.patch(
#     "handlers.login_redirect_handler.save_state_in_dynamo_db"
# )
# mock_ssm_service = mocker.patch(
#     "handlers.login_redirect_handler.get_ssm_parameters",
#     side_effect=InsecureTransportError(),
# )
# response = login_redirect_handler.prepare_redirect_response(FakeWebAppClient)
#
# expected = ApiGatewayResponse(
#     500, "Server error", "GET"
# ).create_api_gateway_response()
#
# assert response == expected
# mock_dynamo_service.assert_not_called()
# mock_ssm_service.assert_called_once()
