# HANDOFF FINAL MVP

## 1. 当前 MVP 能做什么
可完成单论文 ingest/map/session/audit/review 闭环，支持 mock 无外部依赖运行。

## 2. 怎么运行
1) `pip install -e .[dev]`
2) `scripts/smoke_test.sh`

## 3. 核心目录说明
- `cuos/cli.py` 命令入口
- `cuos/pipeline/` 主流程
- `cuos/parsers/` parser adapter
- `cuos/llm/` llm adapter
- `cuos/schemas/` pydantic 模型
- `prompts/` 业务 prompt

## 4. 核心数据模型
`ParsedDocument`, `CognitiveGraph`, `SessionState`, `AuditResult`, `ReviewTask`, `UnderstandingState`。

## 5. 如何接真实 MinerU/Docling/Marker
安装对应可选依赖并在 config 中切换 `parser.default` 与 `parser.adapters`。

## 6. 如何接真实 OpenAI-compatible LLM
配置 `llm.provider=openai-compatible`、`base_url`、`model` 与 API key 环境变量。

## 7. 如何替换业务 prompt
编辑 `prompts/*.md`，保持输入变量与输出 schema 契约，再跑 mock + real 验证。

## 8. 当前已知限制
V1 单论文、CLI 交互为主、图谱策略仍偏启发式。

## 9. 推荐下一步路线
强化证据回链、改进审计鲁棒性、补全 integration 回归样例矩阵。
