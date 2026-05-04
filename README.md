# CUOS (Phase 2 ParserAdapter)

本版本已实现可替换 PDF ParserAdapter 层，支持 mock/docling/marker/mineru 四类适配器。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Parser Adapter 设计

- 统一抽象：`cuos.parsers.base.ParserAdapter`
- 统一返回：`ParsedDocument`
- 工厂选择：`cuos.parsers.factory.get_parser(name, config)`
- 当前支持：`mock` / `docling` / `marker` / `mineru`

真实解析器与主流程解耦：CLI/ingest 仅依赖工厂与抽象接口，不直接依赖具体 SDK 或 CLI。

## 配置示例

```yaml
workspace_dir: ./.cuos_workspace
parser:
  default: mock
  adapters:
    mock: {}
    docling:
      python_module: docling
    marker:
      command: marker_single
      extra_args: []
    mineru:
      command: magic-pdf
      extra_args: []
```

## 真实 Parser 说明

- `docling_parser`：优先 Python API；若未安装依赖，抛清晰依赖错误。
- `marker_parser`：通过 CLI/subprocess 调用；若命令不存在，抛清晰依赖错误。
- `mineru_parser`：通过 CLI/subprocess 调用；若命令不存在，抛清晰依赖错误。

> 当前真实 parser 依赖需要用户自行安装。

## 推荐使用顺序

1. 先用 `mock` 跑通 ingest/map 全流程。
2. 再在配置中切换到 `docling` / `marker` / `mineru`。
3. 按 `parse_report.json` 观察是否降级（`degraded=true`）并逐步完善环境。

## Mock Demo

```bash
python -m cuos.cli init
python -m cuos.cli ingest examples/sample_paper.md --parser mock
python -m cuos.cli map <paper_id>
python -m cuos.cli session <paper_id>
python -m cuos.cli audit <paper_id>
python -m cuos.cli review
```

## 测试

```bash
pytest -q
```
