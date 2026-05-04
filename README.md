# CUOS (Phase 1 Skeleton)

可安装、可测试、可运行的 CLI 骨架，使用 MockParser 与 MockLLM 跑通 ingest/map/session/audit/review 主流程。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

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

## TODO

- 接入真实 ParserAdapter（Docling / MinerU 等）
- 接入真实 LLM 客户端与重试/超时策略
- 更丰富的 session 状态机与评分策略
- review scheduler 的记忆曲线实现
