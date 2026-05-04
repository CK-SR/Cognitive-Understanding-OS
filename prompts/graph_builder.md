目标：基于 ProblemModel 和 DocumentBlock 生成候选理解图谱 JSON。
约束：
- 节点 type 只能使用 CognitiveNode.type 枚举。
- 边 relation 只能使用 CognitiveEdge.relation 枚举。
- 每个节点尽量绑定 source_blocks。
- 每条边必须包含 source_blocks 和 evidence_blocks。
- 模型推测时，human_verified=false 且 llm_confidence<=0.7。
- 不生成不可追溯证据的强结论。

ProblemModel:
{{problem_model_json}}

Document:
{{document_markdown}}
