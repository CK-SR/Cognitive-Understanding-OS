# HANDOFF PHASE 2

## 已完成

- 实现 `ParserAdapter` 抽象与 parser factory。
- 新增 `docling` / `marker` / `mineru` 适配器骨架，具备缺依赖与命令缺失时的清晰错误。
- ingest 支持通过配置与 CLI 参数选择 parser，并将 `ParsedDocument` 元数据写入 SQLite。
- CLI 增加 parser 错误的人类可读输出（`--debug` 可抛 traceback）。
- 补充测试：factory、依赖错误、mock ingest 落库。

## ParserAdapter 设计

- 统一接口：`parse(source_path, output_dir) -> ParsedDocument`
- 统一产物：`full.md` / `structure.json` / `assets/` / `parse_report.json`
- 统一异常：
  - `ParserError`
  - `ParserDependencyError`
  - `ParserExecutionError`
  - `ParserOutputError`

## 各 parser 当前成熟度

- `mock_parser`：可用于稳定单测与流水线 smoke。
- `docling_parser`：已实现依赖探测与降级输出；细粒度 block 提取待接真实 Docling 结果对象。
- `marker_parser`：已实现 CLI 调用、输出扫描、降级逻辑；命令参数细节待按实际安装版本微调。
- `mineru_parser`：已实现 CLI 调用、目录扫描归一化、资产拷贝与解析报告；结构化 JSON 映射待增强。

## 下一阶段

1. 实现可替换 `LLMClient`（超时、重试、schema 校验闭环）。
2. 构建候选理解图谱（claim/concept/edge）与审计可回链证据。
3. 强化真实 parser 的 block/page/bbox/table/figure/formula 映射精度。
