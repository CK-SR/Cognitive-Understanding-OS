# CUOS (Cognitive Understanding OS)

## 1) 项目定位
CUOS 是一个认知机制驱动的论文理解 CLI（命令行）系统，面向个人深度学习与复盘。

## 2) 不是普通 PDF 总结器
CUOS 关注“可追溯理解闭环”：解析 -> 图谱 -> 追问 -> 审计 -> 复习，而不是一次性摘要。

## 3) 第一版功能
- ingest：解析单论文并结构化存储
- map：生成 problem model / candidate graph / key questions
- session：结构化自我解释会话
- audit：基于证据的回答审计
- review：复习任务调度与更新理解状态

## 4) 安装方式
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
# 可选
pip install -e .[dev]
```

## 5) 快速开始（mock demo）
```bash
cuos --config examples/sample_config.yaml init
cuos --config examples/sample_config.yaml ingest examples/sample_paper.md --parser mock
cuos --config examples/sample_config.yaml map <paper_id> --llm mock
cuos --config examples/sample_config.yaml session <paper_id> --non-interactive-demo
cuos --config examples/sample_config.yaml audit <paper_id> --session <session_id> --llm mock
cuos --config examples/sample_config.yaml review --llm mock --non-interactive-demo
```

## 6) 真实 PDF parser 配置
在配置文件中切换 `parser.default` 为 `docling/marker/mineru`，并在 `parser.adapters` 中填写依赖参数。

## 7) OpenAI-compatible LLM 配置
```yaml
llm:
  provider: openai-compatible
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini
  api_key_env: CUOS_LLM_API_KEY
```

## 8) CLI 命令说明
- `cuos init`
- `cuos ingest <path> --parser <name>`
- `cuos map <paper_id> --llm <provider>`
- `cuos session <paper_id> [--non-interactive-demo]`
- `cuos audit <paper_id> --session <session_id> --llm <provider>`
- `cuos review [--paper <paper_id>] [--non-interactive-demo] --llm <provider>`

全部命令支持全局参数：`--config`、`--debug`。

## 9) 输出目录说明
见 `examples/sample_outputs/README.md`。

## 10) 数据模型说明
核心 Pydantic 模型位于 `cuos/schemas/`：
- document：Paper / Block / ParsedDocument
- graph：GraphNode / GraphEdge / CognitiveGraph
- cognition：SessionState / UnderstandingState / ReviewTask
- audit：AuditResult

## 11) Prompt 外置说明
业务 prompt 全部位于 `prompts/`，由 `PromptRegistry` 按文件名加载并注入变量。

## 12) 当前限制
- V1 仅单论文流程
- 默认 mock 为主，真实 parser/llm 需要额外依赖与配置
- session/review 默认交互输入（可用 demo 参数跳过）

## 13) 后续路线图
- 更细粒度证据对齐
- 更强审计策略与评分稳定性
- parser/llm 适配器扩展与回归测试矩阵
