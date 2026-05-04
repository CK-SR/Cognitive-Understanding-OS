# AGENTS.md — Cognitive Understanding OS (cuos) 项目级开发指南

## 1) 项目概述

Cognitive Understanding OS（`cuos`）是一个**个人使用**的“认知机制驱动的论文理解命令行系统”。

第一版（V1）聚焦 PDF 学术材料（论文、技术报告），采用**自动流水线 + 交互式认知会话**混合工作流：

- 自动阶段：`ingest` / `map`
- 交互阶段：`session` / `audit` / `review`

系统定位不是“PDF 总结器”，而是：

- PDF 解析与结构化
- 候选理解图谱构建
- 交互式追问与反思
- 回答审计与证据回溯
- 复习任务生成与闭环

V1 优先目标：**结构清晰、接口可替换、测试可运行**。

---

## 2) 代码风格

### 2.1 Python 与工程规范

- Python 版本：`3.11+`
- 全量类型注解（公共函数/方法必须显式标注输入输出类型）。
- 统一使用 `ruff` 做 lint/format（如果项目拆分了 lint 与 format，保持 CI 一致）。
- 单个函数保持“短小、单一职责”，避免超长函数和隐式副作用。
- 优先使用组合（composition）而非继承（inheritance）。
- 严禁在 import 周围使用 try/catch 做静默降级。

### 2.2 命名约定

- 文件/模块：`snake_case`
- 类名：`PascalCase`
- 函数与变量：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- CLI 命令：短词、动词优先（如 `ingest`, `map`, `session`）。

### 2.3 日志与输出

- CLI 展示使用 `rich`，错误信息要可执行（告诉用户下一步）。
- 核心流程必须有结构化日志（至少含 `event`, `paper_id`, `stage`, `status` 字段）。
- 不在普通日志里输出敏感信息（API key、完整隐私文本）。

---

## 3) 目录结构约定

建议按如下结构组织（可迭代，但不要破坏分层边界）：

```text
cuos/
  __init__.py
  cli/
    app.py                 # Typer 入口
    commands/
      ingest.py
      map.py
      session.py
      audit.py
      review.py
  core/
    pipeline/
    services/
    policies/
  domain/
    models/                # Pydantic v2 数据模型
    graph/
  infra/
    llm/
    parser/
    storage/
    config/
  prompts/
    *.yaml | *.md | *.jinja
  tests/
    unit/
    integration/
  scripts/
  pyproject.toml
  AGENTS.md
```

硬性边界：

- `cli` 层不得直接依赖具体 LLM SDK 或具体 PDF 工具实现；必须通过 `core/infra` 抽象。
- `domain` 层不依赖 `cli`。
- `prompts/` 与业务代码分离，代码中禁止写死业务 prompt。

---

## 4) 数据模型约定

### 4.1 总原则

- 所有核心对象使用 **Pydantic v2** 定义 schema。
- LLM 输出必须“先校验后使用”：`raw -> pydantic validate -> domain object`。
- 不允许将未经 schema 校验的 LLM 文本直接写入数据库或图谱。

### 4.2 关键实体（V1 最小集）

至少应包含（可扩展）：

- `Paper`：论文元信息
- `Block`：解析后的最小证据块（段落/公式/图表说明等）
- `Claim`：候选论断
- `Concept`：概念节点
- `GraphNode` / `GraphEdge`：理解图谱节点与边
- `SessionTurn`：交互回合
- `AuditRecord`：回答审计记录
- `ReviewTask`：复习任务

### 4.3 图谱边强制字段

**所有候选图谱边必须包含以下字段：**

- `source_blocks: list[str]`：边来源块（通常是触发该边生成的块）
- `evidence_blocks: list[str]`：支撑证据块
- `human_verified: bool`：是否已被人工确认

禁止省略上述字段；空值要使用显式空列表/布尔值，不可用 `None` 混淆语义。

---

## 5) LLM 调用约定

### 5.1 供应商无关与可替换性

- 通过 `infra.llm` 下的抽象接口调用模型，默认可接 OpenAI-compatible Chat Completions。
- 业务层不得耦合具体厂商参数命名。

### 5.2 调用安全与稳定

- 每次调用必须：
  - 指定任务类型（抽取/对比/审计/出题）
  - 指定输出 schema
  - 设置超时与重试策略（有限重试）
- 输出处理流程固定：
  1) 获取原始响应
  2) JSON 解析
  3) Pydantic 校验
  4) 校验失败进入受控错误分支（记录 + 可重试/降级）

### 5.3 可观测性

记录最小调用元数据：

- `model_name`
- `temperature` / 关键参数
- `prompt_template_id`
- `token_usage`（若可得）
- `latency_ms`
- `parse_success`

---

## 6) Prompt 外置约定

- **禁止在 Python 代码中写死业务 prompt。**
- 所有业务 prompt 必须位于 `prompts/` 或配置文件中。
- 每个 prompt 必须有稳定 ID（如 `map.claim_extract.v1`）。
- Prompt 迭代采用版本后缀（`v1`, `v2`），不得静默覆盖导致行为漂移。
- Prompt 模板需声明：
  - 用途
  - 输入变量
  - 期望输出 schema 名称
  - 失败重试策略（若适用）

---

## 7) ParserAdapter 约定

V1 PDF 解析能力通过 Adapter 接入，禁止与单一解析库强耦合。

### 7.1 接口要求

定义统一 `ParserAdapter`（示例语义）：

- `parse(file_path) -> ParsedDocument`
- `extract_blocks(parsed_doc) -> list[Block]`
- `extract_assets(parsed_doc) -> list[Asset]`（公式/图/表）
- `metadata(parsed_doc) -> PaperMetadata`

### 7.2 设计要求

- 适配器实现与核心流程解耦，可替换不同 PDF 解析后端。
- 解析失败必须返回结构化错误，不得只抛裸异常字符串。
- `Block` 需可追溯页码、块序号与原文定位信息，支持审计回链。

---

## 8) 测试要求

### 8.1 测试分层

- `tests/unit`：纯单元测试（schema、服务逻辑、图算法）。
- `tests/integration`：流水线集成测试（ingest/map/session 主路径）。

### 8.2 必测项（V1）

- Pydantic schema 校验成功/失败分支。
- LLM 输出非法 JSON、字段缺失、类型错误时的受控处理。
- 图谱边字段完整性（`source_blocks/evidence_blocks/human_verified`）约束。
- Prompt 装载与版本选择逻辑。
- ParserAdapter 替换性（至少一个 mock adapter + 一个真实适配器 smoke test）。

### 8.3 工程门禁建议

- `ruff check .`
- `pytest -q`
- 如启用类型检查：`pyright` 或 `mypy`

---

## 9) 每次开发完成后的 Handoff 要求

每次任务完成后，提交说明至少包含：

1. **变更摘要**：新增/修改了哪些模块，解决什么问题。
2. **架构影响**：是否引入新抽象、是否影响分层边界。
3. **数据模型变更**：schema 字段增删改及兼容性说明。
4. **Prompt 变更**：涉及哪些 prompt ID/版本。
5. **测试结果**：执行命令与结果（通过/失败原因）。
6. **后续建议**：下一步可迭代项与风险点。

---

## 10) 明确禁止事项

- 禁止将该系统实现为“只出摘要”的一次性脚本。
- 禁止跳过用户参与的关键理解动作（闭卷复述/自我解释/迁移应用）。
- 禁止在代码中硬编码业务 prompt。
- 禁止让未经 Pydantic 校验的 LLM 输出进入核心流程。
- 禁止省略图谱边的 `source_blocks` / `evidence_blocks` / `human_verified`。
- 禁止在 V1 引入复杂 RAG、Neo4j、Web 前端、多论文跨库图谱。
- 禁止为了“跑通”牺牲可替换性（Parser/LLM/Storage 必须可替换）。

---

## 11) V1 范围再确认（防止需求漂移）

V1 只做：

- 单论文 PDF 输入
- ingest/map 自动阶段
- session/audit/review 交互阶段
- 本地存储（SQLite）
- 命令行交互（Typer + Rich）

不做：

- Web Dashboard
- 多论文统一知识库
- 重型检索基础设施

> 若新增需求超出 V1 范围，必须先在任务说明中标注“超范围变更”并给出拆分计划。
