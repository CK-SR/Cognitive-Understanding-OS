from __future__ import annotations

from enum import Enum


class SessionStage(str, Enum):
    INIT = "INIT"
    CENTRAL_PROBLEM = "CENTRAL_PROBLEM"
    MECHANISM_EXPLANATION = "MECHANISM_EXPLANATION"
    EVIDENCE_LINKING = "EVIDENCE_LINKING"
    LIMITATION_CRITIQUE = "LIMITATION_CRITIQUE"
    TRANSFER_APPLICATION = "TRANSFER_APPLICATION"
    SUMMARY = "SUMMARY"
    DONE = "DONE"


LINEAR_FLOW: dict[SessionStage, SessionStage] = {
    SessionStage.INIT: SessionStage.CENTRAL_PROBLEM,
    SessionStage.CENTRAL_PROBLEM: SessionStage.MECHANISM_EXPLANATION,
    SessionStage.MECHANISM_EXPLANATION: SessionStage.EVIDENCE_LINKING,
    SessionStage.EVIDENCE_LINKING: SessionStage.LIMITATION_CRITIQUE,
    SessionStage.LIMITATION_CRITIQUE: SessionStage.TRANSFER_APPLICATION,
    SessionStage.TRANSFER_APPLICATION: SessionStage.SUMMARY,
    SessionStage.SUMMARY: SessionStage.DONE,
    SessionStage.DONE: SessionStage.DONE,
}


def next_state(current: SessionStage) -> SessionStage:
    return LINEAR_FLOW[current]


def ordered_question_states() -> list[SessionStage]:
    return [
        SessionStage.CENTRAL_PROBLEM,
        SessionStage.MECHANISM_EXPLANATION,
        SessionStage.EVIDENCE_LINKING,
        SessionStage.LIMITATION_CRITIQUE,
        SessionStage.TRANSFER_APPLICATION,
    ]
