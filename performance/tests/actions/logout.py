def logout(client, auth_headers):
    client.get("/Auth/Logout", headers=auth_headers, name="Logout")
