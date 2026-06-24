from backend.tests.conftest import register_user, auth_headers


def make_teacher_token(client):
    resp = register_user(client, email="teacher@test.com", role="teacher")
    return resp.json()["access_token"]


def make_student_token(client):
    resp = register_user(client, email="student@test.com", role="student")
    return resp.json()["access_token"]


def sample_test_payload():
    return {
        "title": "Test Math",
        "description": "Basic math",
        "duration_minutes": 20,
        "risk_threshold": 10,
        "questions": [
            {"text": "2+2=?", "options": ["3", "4", "5"], "correct_index": 1},
            {"text": "3+3=?", "options": ["5", "6", "7"], "correct_index": 1},
        ],
    }


def test_teacher_can_create_test(client):
    token = make_teacher_token(client)
    resp = client.post("/tests", json=sample_test_payload(), headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test Math"
    assert len(resp.json()["questions"]) == 2


def test_student_cannot_create_test(client):
    token = make_student_token(client)
    resp = client.post("/tests", json=sample_test_payload(), headers=auth_headers(token))
    assert resp.status_code == 403


def test_list_tests_returns_created_test(client):
    token = make_teacher_token(client)
    client.post("/tests", json=sample_test_payload(), headers=auth_headers(token))
    resp = client.get("/tests", headers=auth_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_test_detail_hides_correct_answers(client):
    teacher_token = make_teacher_token(client)
    created = client.post("/tests", json=sample_test_payload(), headers=auth_headers(teacher_token)).json()

    student_token = make_student_token(client)
    resp = client.get(f"/tests/{created['id']}", headers=auth_headers(student_token))
    assert resp.status_code == 200
    assert "correct_index" not in resp.json()["questions"][0]
