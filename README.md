# CUOS (Phase 3 LLM + Map)

## 配置 OpenAI-compatible LLM

在 `config.yaml` 中配置：

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

## 使用 Mock LLM

```yaml
llm:
  provider: mock
```

可离线跑通 `map` 阶段。

## map 阶段输出

- `problem_model.json`：问题骨架。
- `candidate_graph.json`：候选理解图谱（nodes/edges）。
- `key_questions.json` / `key_questions.md`：第一轮苏格拉底追问。
- `reading_map.md`：阅读路径建议。

## candidate_graph.json 字段说明

- `nodes[].source_blocks`：节点来源证据块。
- `edges[].source_blocks`：边生成来源块。
- `edges[].evidence_blocks`：边支撑证据块。
- `edges[].human_verified`：是否人工确认。
- `edges[].llm_confidence`：模型置信度。

## 为什么业务 prompt 外置

- 避免把业务策略硬编码在 Python 中。
- 便于版本化迭代 prompt。
- 降低代码变更频率，提升可审计性。
