# CUOS Architecture

## 系统分层
- `cuos/cli.py`: Typer + Rich 命令入口
- `cuos/pipeline/`: ingest/map/session/audit/review 编排
- `cuos/parsers/`: ParserAdapter 与具体实现
- `cuos/llm/`: LLMClient 抽象、OpenAI-compatible、Mock
- `cuos/schemas/`: Pydantic v2 核心数据模型
- `cuos/storage/`: SQLite + workspace 文件组织

## 数据流
输入文档 -> ParserAdapter -> ParsedDocument/Block -> map(LLM+prompt) -> CognitiveGraph/QuestionSet -> session -> audit -> review。

## ParserAdapter
统一通过 `get_parser(...)` 进入，支持 mock/docling/marker/mineru，避免 pipeline 耦合具体工具。

## LLMClient
统一通过 `get_llm_client(...)` 获取，`chat_json(..., schema)` 固定为“调用 + 解析 + Pydantic 校验”。

## PromptRegistry
所有业务 prompt 外置到 `prompts/`，运行时按模板加载与变量渲染。

## CognitiveGraph
由 `GraphNode` + `GraphEdge` 构成，边包含 `source_blocks` / `evidence_blocks` / `human_verified`。

## Session/Audit/Review 状态流
`session` 采集回答 -> `audit` 生成审计和追问 -> `review` 消化复习任务并更新 understanding state。

## 存储策略
- 文件系统：论文与认知产物（json/md）
- SQLite：文档索引、复习任务状态
