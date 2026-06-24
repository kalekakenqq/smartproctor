from backend.tests.test_tests import make_teacher_token, make_student_token, sample_test_payload
from backend.tests.conftest import auth_headers


def setup_finished_session(client):
    teacher_token = make_teacher_token(client)
    test = client.post("/tests", json=sample_test_payload(), headers=auth_headers(teacher_token)).json()
    student_token = make_student_token(client)
    session = client.post("/sessions", json={"test_id": test["id"]}, headers=auth_headers(student_token)).json()

    client.post("/violations", json={
        "session_id": session["id"], "type": "face_away", "elapsed_seconds": 65,
    }, headers=auth_headers(student_token))

    q1_id = test["questions"][0]["id"]
    client.post(f"/sessions/{session['id']}/finish", json={"answers": {str(q1_id): 1}}, headers=auth_headers(student_token))

    return test, session, teacher_token, student_token


def test_score_distribution_visible_to_teacher(client):
    test, session, teacher_token, _ = setup_finished_session(client)
    resp = client.get(f"/reports/test/{test['id']}/scores", headers=auth_headers(teacher_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["student_name"] == "Test User"


def test_score_distribution_forbidden_for_student(client):
    test, session, teacher_token, student_token = setup_finished_session(client)
    resp = client.get(f"/reports/test/{test['id']}/scores", headers=auth_headers(student_token))
    assert resp.status_code == 403


def test_violation_heatmap_groups_by_minute(client):
    test, session, teacher_token, _ = setup_finished_session(client)
    resp = client.get(f"/reports/test/{test['id']}/heatmap", headers=auth_headers(teacher_token))
    assert resp.status_code == 200
    assert resp.json() == {"1": 1}
