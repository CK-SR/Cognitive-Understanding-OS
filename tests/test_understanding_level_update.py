from cuos.cognition.scoring import determine_understanding_level
from cuos.schemas.audit import AuditResult


def test_understanding_level_update() -> None:
    result = AuditResult(
        accuracy_score=0.9,
        completeness_score=0.9,
        depth_score=0.9,
        transfer_score=0.85,
        issues=["limitation boundary not explicit"],
        missing_evidence=[],
        corrected_understanding="x",
        follow_up_question=None,
        suggested_understanding_level="L5",
    )
    assert determine_understanding_level(result) == "L5"
