def test_register(client, unique_email):
    r = client.post("/auth/register", json={"email": unique_email, "password": "Secret1234!"})
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == unique_email
    assert body["is_active"] is True

def test_login(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "Secret1234!"})
    r = client.post("/auth/login", json={"email": unique_email, "password": "Secret1234!"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data and "refresh_token" in data

def test_me(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "Secret1234!"})
    tokens = client.post("/auth/login", json={"email": unique_email, "password": "Secret1234!"}).json()
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r.status_code == 200
    assert r.json()["email"] == unique_email

def test_refresh_rotates_token(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "Secret1234!"})
    data = client.post("/auth/login", json={"email": unique_email, "password": "Secret1234!"}).json()
    r = client.post("/auth/refresh", json={"refresh_token": data["refresh_token"]})
    assert r.status_code == 200
    new_tokens = r.json()
    assert "access_token" in new_tokens and "refresh_token" in new_tokens
    assert new_tokens["refresh_token"] != data["refresh_token"]  # ротация refresh-токена

def test_logout(client, unique_email):
    client.post("/auth/register", json={"email": unique_email, "password": "Secret1234!"})
    data = client.post("/auth/login", json={"email": unique_email, "password": "Secret1234!"}).json()
    r = client.post("/auth/logout", json={"refresh_token": data["refresh_token"]})
    assert r.status_code == 200

def test_delete_account(client, unique_email):
    password = "Secret1234!"

    r = client.post("/auth/register", json={"email": unique_email, "password": password})
    assert r.status_code == 201

    r = client.post("/auth/login", json={"email": unique_email, "password": password})
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    auth = {"Authorization": f"Bearer {tokens['access_token']}"}

    r = client.delete("/auth/delete-account", headers=auth)
    assert r.status_code in (200, 204)

    r = client.get("/auth/me", headers=auth)
    assert r.status_code == 401
