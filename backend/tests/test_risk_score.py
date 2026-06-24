from backend.services.risk_score import compute_risk_score, violation_weight


def test_violation_weight_face_absent():
    assert violation_weight("face_absent") == 3


def test_violation_weight_face_away():
    assert violation_weight("face_away") == 1


def test_violation_weight_multiple_faces():
    assert violation_weight("multiple_faces") == 5


def test_violation_weight_unknown_type_is_zero():
    assert violation_weight("unknown") == 0


def test_compute_risk_score_sums_weights():
    score = compute_risk_score(["face_absent", "face_away", "multiple_faces"])
    assert score == 3 + 1 + 5


def test_compute_risk_score_empty_list():
    assert compute_risk_score([]) == 0
