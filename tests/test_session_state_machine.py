from cuos.cognition.state_machine import SessionStage, next_state, ordered_question_states


def test_state_machine_linear_flow() -> None:
    state = SessionStage.INIT
    for expected in [
        SessionStage.CENTRAL_PROBLEM,
        SessionStage.MECHANISM_EXPLANATION,
        SessionStage.EVIDENCE_LINKING,
        SessionStage.LIMITATION_CRITIQUE,
        SessionStage.TRANSFER_APPLICATION,
        SessionStage.SUMMARY,
        SessionStage.DONE,
    ]:
        state = next_state(state)
        assert state == expected


def test_ordered_question_states() -> None:
    states = ordered_question_states()
    assert len(states) == 5
    assert states[0] == SessionStage.CENTRAL_PROBLEM
