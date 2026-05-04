from cuos.llm.openai_compatible import extract_json_object


def test_extract_json_object() -> None:
    text = "prefix {\"a\": 1, \"b\": 2} suffix"
    assert extract_json_object(text) == {"a": 1, "b": 2}
