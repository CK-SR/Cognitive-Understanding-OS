from cuos.schemas.audit import AuditResult

VALID_LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5")
_LEVEL_INDEX = {level: idx for idx, level in enumerate(VALID_LEVELS)}


# NOTE: V1 heuristic mapping only; this is intentionally simple and can be refined later.
def determine_understanding_level(audit: AuditResult) -> str:
    """Map an AuditResult to a conservative understanding level.

    Prefer the structured `suggested_understanding_level` emitted by the audit
    prompt, but cap it with score-based gates so a fluent model answer cannot
    inflate the level too aggressively. This avoids the previous English-only
    string matching on issue text and works better for Chinese audit output.
    """
    heuristic = _heuristic_level(audit)
    suggested = audit.suggested_understanding_level
    if suggested not in _LEVEL_INDEX:
        return heuristic

    if audit.accuracy_score < 0.4:
        return "L0"
    if suggested == "L5" and audit.transfer_score < 0.7:
        suggested = "L4"
    if _LEVEL_INDEX[suggested] >= _LEVEL_INDEX["L4"] and audit.depth_score < 0.65:
        suggested = "L3"
    if _LEVEL_INDEX[suggested] >= _LEVEL_INDEX["L3"] and audit.completeness_score < 0.6:
        suggested = "L2"

    # Allow the LLM-suggested level to move at most one level above the score
    # heuristic in V1. This keeps scoring stable without ignoring the prompt.
    max_allowed_index = min(_LEVEL_INDEX[heuristic] + 1, _LEVEL_INDEX["L5"])
    return VALID_LEVELS[min(_LEVEL_INDEX[suggested], max_allowed_index)]


def _heuristic_level(audit: AuditResult) -> str:
    if audit.accuracy_score < 0.4:
        return "L0"
    level = "L1" if audit.completeness_score < 0.7 else "L2"
    if audit.depth_score >= 0.7:
        level = "L2"
    if audit.completeness_score >= 0.8 and audit.depth_score >= 0.75:
        level = "L3"
    if audit.depth_score >= 0.85 and (audit.issues or audit.missing_evidence):
        level = "L4"
    if audit.transfer_score >= 0.8:
        level = "L5"
    return level


def max_level(*levels: str) -> str:
    valid = [level for level in levels if level in _LEVEL_INDEX]
    if not valid:
        return "L0"
    return max(valid, key=lambda item: _LEVEL_INDEX[item])
