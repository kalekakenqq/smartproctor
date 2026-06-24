from backend.tests.test_tests import make_teacher_token, make_student_token, sample_test_payload
from backend.tests.conftest import auth_headers


def create_test(client, teacher_token):
    return client.post("/tests", json=sample_test_payload(), headers=auth_headers(teacher_token)).json()


def test_student_can_start_session(client):
    teacher_token = make_teacher_token(client)
    test = create_test(client, teacher_token)
    student_token = make_student_token(client)

    resp = client.post("/sessions", json={"test_id": test["id"]}, headers=auth_headers(student_token))
    assert resp.status_code == 201
    assert resp.json()["status"] == "in_progress"


def test_teacher_cannot_start_session(client):
    teacher_token = make_teacher_token(client)
    test = create_test(client, teacher_token)

    resp = client.post("/sessions", json={"test_id": test["id"]}, headers=auth_headers(teacher_token))
    assert resp.status_code == 403


def test_starting_session_twice_returns_same_session(client):
    teacher_token = make_teacher_token(client)
    test = create_test(client, teacher_token)
    student_token = make_student_token(client)

    first = client.post("/sessions", json={"test_id": test["id"]}, headers=auth_headers(student_token)).json()
    second = client.post("/sessions", json={"test_id": test["id"]}, headers=auth_headers(student_token)).json()
    assert first["id"] == second["id"]


def test_finish_session_computes_score(client):
    teacher_token = make_teacher_token(client)
    test = create_test(client, teacher_token)
    student_token = make_student_token(client)

    session = client.post("/sessions", json={"test_id": test["id"]}, headers=auth_headers(student_token)).json()
    q1_id = test["questions"][0]["id"]
    q2_id = test["questions"][1]["id"]

    answers = {str(q1_id): 1, str(q2_id): 0}  # one correct, one wrong
    resp = client.post(f"/sessions/{session['id']}/finish", json={"answers": answers}, headers=auth_headers(student_token))
    assert resp.status_code == 200
    assert resp.json()["score"] == 50.0
    assert resp.json()["status"] == "finished"
