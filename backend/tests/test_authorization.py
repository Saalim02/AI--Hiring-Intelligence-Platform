def token(client, email):
    response = client.post("/auth/login", data={"username": email, "password": "password123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_anonymous_access_is_rejected(client):
    assert client.get("/resume/all").status_code == 401

def test_recruiter_sees_only_owned_resumes(client, users):
    headers = {"Authorization": f"Bearer {token(client, 'recruiter@example.com')}"}
    response = client.get("/resume/all", headers=headers)
    assert response.status_code == 200
    assert [item["filename"] for item in response.json()] == ["owned.pdf"]

def test_candidate_cannot_access_recruiter_library_or_ranking(client, users):
    headers = {"Authorization": f"Bearer {token(client, 'candidate@example.com')}"}
    assert client.get("/resume/all", headers=headers).status_code == 403
    assert client.post("/resume/rank-candidates", params={"job_description": "Python backend role"}, headers=headers).status_code == 403

def test_cross_user_resume_access_is_rejected(client, users):
    headers = {"Authorization": f"Bearer {token(client, 'recruiter@example.com')}"}
    assert client.get("/resume/2", headers=headers).status_code == 404
    candidate_headers = {"Authorization": f"Bearer {token(client, 'candidate@example.com')}"}
    assert client.get("/resume/1", headers=candidate_headers).status_code == 404

def test_candidate_can_access_only_own_candidate_api(client, users):
    headers = {"Authorization": f"Bearer {token(client, 'candidate@example.com')}"}
    response = client.get("/candidate/resumes", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
