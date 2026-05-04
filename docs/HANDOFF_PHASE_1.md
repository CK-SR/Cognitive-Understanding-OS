# HANDOFF PHASE 1

## 已完成内容
- 初始化可安装 Python 包与 CLI 命令骨架。
- 实现 mock ingest/map/session/audit/review 流程。
- 建立 Pydantic v2 schemas 与基础测试。

## 未完成内容
- 真实 PDF 解析 Adapter。
- 真实 LLM provider 与重试/超时策略。
- 更完整的认知状态机与复习算法。

## 关键设计决策
- 采用最小可运行模块分层：parsers/llm/pipeline/storage/schemas。
- prompt 全部外置到 `prompts/`，业务代码仅负责加载与调度。
- 图谱边字段使用强 schema 校验，确保 evidence_blocks/human_verified 等字段语义清晰。

## 下一阶段建议
1. 增加 `ParserAdapter` 统一错误模型与定位信息。
2. 在 `llm` 层增加 schema-aware 调用封装（JSON parse + validate + retry）。
3. 扩展 integration tests 覆盖 session/audit/review 主路径。
