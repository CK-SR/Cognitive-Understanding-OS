# Prompt Customization

## Prompt 文件与作用
- `prompts/problem_model.md`: 抽取论文问题模型（输出 `ProblemModel`）
- `prompts/graph_builder.md`: 生成候选理解图谱（输出 `CognitiveGraph`）
- `prompts/socratic_question.md`: 生成苏格拉底问题集（输出 `QuestionSet`）
- `prompts/answer_audit.md`: 审计会话回答（输出 `AuditResult`）
- `prompts/review.md` / `prompts/transfer.md`: 复习与迁移辅助

## 输入变量
由 `PromptRegistry.load(name, variables)` 注入，如：
- `document_markdown`
- `problem_model_json`
- `candidate_graph_json`
- `question`
- `user_answer`

## 期望输出 schema
所有 LLM JSON 输出都通过 Pydantic 校验：`ProblemModel`/`CognitiveGraph`/`QuestionSet`/`AuditResult`。

## 如何替换为更强业务 prompt
1. 在 `prompts/` 中保留稳定 ID（文件名或版本后缀）。
2. 明确输入变量和 JSON 输出结构。
3. 小步替换并执行 mock + real LLM 双路径验证。

## 替换后测试建议
- mock: `pytest -q` + `scripts/smoke_test.sh`
- real llm: `cuos map/audit/review ... --llm openai-compatible` 并检查 JSON 校验与错误分支。
