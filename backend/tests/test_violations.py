import base64
import os
from backend.tests.test_tests import make_teacher_token, make_student_token, sample_test_payload
from backend.tests.conftest import auth_headers

TINY_JPEG_BASE64 = base64.b64encode(b"fake-jpeg-bytes").decode()


def start_session(client):
    teacher_token = make_teacher_token(client)
    test = client.post("/tests", json=sample_test_payload(), headers=auth_headers(teacher_token)).json()
    student_token = make_student_token(client)
    session = client.post("/sessions", json={"test_id": test["id"]}, headers=auth_headers(student_token)).json()
    return test, session, student_token, teacher_token


def test_create_violation_increases_risk_score(client):
    test, session, student_token, _ = start_session(client)

    resp = client.post("/violations", json={
        "session_id": session["id"], "type": "face_away", "elapsed_seconds": 5,
    }, headers=auth_headers(student_token))
    assert resp.status_code == 201
    assert resp.json()["weight"] == 1

    updated = client.get(f"/sessions/{session['id']}", headers=auth_headers(student_token)).json()
    assert updated["risk_score"] == 1


def test_violation_exceeding_threshold_blocks_session(client):
    test, session, student_token, _ = start_session(client)
    # risk_threshold is 10, multiple_faces weight is 5 -> need 2 to reach 10
    for _ in range(2):
        client.post("/violations", json={
            "session_id": session["id"], "type": "multiple_faces", "elapsed_seconds": 5,
        }, headers=auth_headers(student_token))

    updated = client.get(f"/sessions/{session['id']}", headers=auth_headers(student_token)).json()
    assert updated["status"] == "blocked"
    assert updated["risk_score"] >= 10


def test_violation_snapshot_saved_to_disk(client, tmp_path):
    test, session, student_token, _ = start_session(client)

    resp = client.post("/violations", json={
        "session_id": session["id"], "type": "face_absent", "elapsed_seconds": 1,
        "snapshot_base64": TINY_JPEG_BASE64,
    }, headers=auth_headers(student_token))
    assert resp.status_code == 201
    snapshot_path = resp.json()["snapshot_path"]
    assert snapshot_path is not None

    from backend.routers import violations as violations_module
    filename = os.path.basename(snapshot_path)
    saved_file = os.path.join(violations_module.SNAPSHOTS_DIR, filename)
    assert os.path.exists(saved_file)
