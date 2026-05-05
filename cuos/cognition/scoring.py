from cuos.schemas.audit import AuditResult


# NOTE: V1 heuristic mapping only; this is intentionally simple and can be refined later.
def determine_understanding_level(audit: AuditResult) -> str:
    if audit.accuracy_score < 0.4:
        return "L0"
    level = "L1" if audit.completeness_score < 0.7 else "L2"
    if audit.depth_score >= 0.7:
        level = "L2"
    if audit.completeness_score >= 0.8 and audit.depth_score >= 0.75:
        level = "L3"
    if audit.depth_score >= 0.85 and any(
        "limit" in issue.lower() for issue in audit.issues
    ):
        level = "L4"
    if audit.transfer_score >= 0.8:
        level = "L5"
    return level
