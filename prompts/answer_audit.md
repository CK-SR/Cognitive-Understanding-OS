# Prompt ID: audit.answer_audit.v1
用途: 审计用户对论文问题的回答质量并输出结构化评分。
输入变量:
- question
- user_answer
- related_source_blocks
- candidate_graph_context
输出schema: AuditResult

规则:
- 不要安慰用户，不要使用泛泛鼓励语。
- 优先指出误读、证据不足、因果链断裂、无法迁移问题。
- 若回答仅摘要复述，depth_score不得过高。
- 若没有连接证据，completeness_score不得过高。
- transfer_score仅在明确迁移到项目时可高。

Question:
{{question}}

User Answer:
{{user_answer}}

Related Source Blocks:
{{related_source_blocks}}

Candidate Graph Context:
{{candidate_graph_context}}

只返回 JSON，字段必须完整：
{
  "accuracy_score": 0.0,
  "completeness_score": 0.0,
  "depth_score": 0.0,
  "transfer_score": 0.0,
  "issues": [""],
  "missing_evidence": [""],
  "corrected_understanding": "",
  "follow_up_question": null,
  "suggested_understanding_level": "L0"
}
