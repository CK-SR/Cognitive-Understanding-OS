# CUOS (Phase 4 Session/Audit/Review)

## 快速使用流程

```bash
python -m cuos.cli init
python -m cuos.cli ingest xxx.pdf --parser mock
python -m cuos.cli map <paper_id> --llm mock
python -m cuos.cli session <paper_id>
python -m cuos.cli audit <paper_id> --session <session_id> --llm mock
python -m cuos.cli review --llm mock
```

按论文过滤复习任务：

```bash
python -m cuos.cli review --paper <paper_id> --llm mock
```

## 真实 LLM 配置

在 `config.yaml` 中配置 OpenAI-compatible：

```yaml
llm:
  provider: openai-compatible
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini
  api_key_env: CUOS_LLM_API_KEY
```

并设置环境变量：

```bash
export CUOS_LLM_API_KEY=your_key
```

## Phase 4 输出文件

- `sessions/<session_id>.json` / `.md`
- `cognitive/audit_report.md`
- `cognitive/follow_up_questions.md`
- `cognitive/understanding_state.json`
- `cognitive/review_tasks.json`

## Prompt 列表

- `prompts/answer_audit.md`：回答审计
- `prompts/review.md`：复习提问（后续可扩展）
- `prompts/socratic_question.md`：问题生成
