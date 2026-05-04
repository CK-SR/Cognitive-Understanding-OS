# HANDOFF PHASE 3

## 已完成
- 新增 LLMClient 抽象与 OpenAI-compatible 实现。
- 新增 LLMFactory，支持 `mock` 与 `openai-compatible`。
- PromptRegistry 支持从 `prompts/` 加载并做变量替换。
- map 流程输出 `problem_model.json`、`candidate_graph.json`、`key_questions.md/json`、`reading_map.md`。

## LLM 接口说明
- `chat_text(messages, **kwargs) -> str`
- `chat_json(messages, schema_model, **kwargs) -> BaseModel`

## Prompt 外置方式
- 业务 prompt 放在 `prompts/*.md`。
- 通过 `PromptRegistry.load(name, variables)` 统一读取和替换变量。

## 当前 map 流程限制
- 当前仅做简单字符截断压缩，无复杂 RAG。
- `reading_map` 仍为规则化生成，后续可改为 LLM 输出。

## 下一阶段
- 交互式 `session / audit / review` 流程强化与审计链路完善。
