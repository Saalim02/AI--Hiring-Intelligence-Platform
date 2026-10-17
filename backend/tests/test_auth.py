def test_signup_validates_role_and_me_returns_jwt_user(client):
    signup = client.post(
        "/auth/signup",
        json={
            "username": "new-candidate",
            "email": "new-candidate@example.com",
            "password": "password123",
            "role": "candidate",
        },
    )
    assert signup.status_code == 200
    assert signup.json()["role"] == "candidate"

    login = client.post(
        "/auth/login",
        data={"username": "new-candidate@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    payload = login.json()
    assert payload["user"]["role"] == "candidate"

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "new-candidate@example.com"
    assert me.json()["role"] == "candidate"


def test_signup_rejects_unknown_role(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "bad-role",
            "email": "bad-role@example.com",
            "password": "password123",
            "role": "administrator",
        },
    )
    assert response.status_code == 422


def test_invalid_jwt_is_rejected(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401
