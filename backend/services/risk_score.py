WEIGHTS = {
    "face_absent": 3,
    "face_away": 1,
    "multiple_faces": 5,
}


def violation_weight(violation_type: str) -> float:
    return WEIGHTS.get(violation_type, 0)


def compute_risk_score(violation_types: list[str]) -> float:
    return sum(violation_weight(v) for v in violation_types)
