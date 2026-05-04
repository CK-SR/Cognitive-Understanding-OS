# HANDOFF PHASE 4

## 已完成
- 实现 session 状态机与 5 类线性交互问题。
- 实现 session 持久化（json + markdown）。
- 实现 audit 流水线：逐条审计、理解等级更新、报告与追问生成。
- 实现 review scheduler（1/3/7/14 天）与 CLI review 执行。
- 增加 understanding level heuristic 规则。
- 增加 Phase 4 相关测试。

## session/audit/review 数据流
1. `session`: 读取 map 阶段产物，收集用户多行回答，保存 `sessions/<id>.json/.md`。
2. `audit`: 加载 session + candidate graph，调用 `answer_audit` prompt，生成审计结果与理解状态，并写入复习任务（json + sqlite）。
3. `review`: 读取到期任务，交互提问并审计，更新任务状态与 `understanding_state.json`。

## 当前限制
- session 仅线性状态推进，未做动态分支。
- review 复用 `answer_audit`，尚未启用专门 review 打分策略。
- understanding level 为启发式，尚未按问题类型细化。
- candidate_graph 节点 `understanding_level` 仅在全局状态体现，未逐节点写回。

## 可替换 prompt 列表
- `problem_model.md`
- `graph_builder.md`
- `socratic_question.md`
- `answer_audit.md`
- `review.md`
- `transfer.md`

## 下一阶段建议
1. 真实 PDF 解析验收：MinerU/Marker/Docling 在同一评测集对比。
2. CLI 体验优化：多行输入编辑、上下文展示、彩色评分面板。
3. 可选 dashboard：只读视图展示 session/audit/review 轨迹（保持后端与存储不变）。
