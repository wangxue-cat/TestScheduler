# parse-case-steps 详细规则

## 1. unknown 处理

`unknown` 类型的步骤不阻塞流程，但需在输出中标记供用户确认。

## 2. 步骤编号提取

步骤编号自动从文本中提取序号：1. / 2. / ① / ② / (1) / (2) 等格式。

## 3. 预期结果解析

预期结果解析失败的标记为 `type: "unknown"` 供后续人工处理。

## 4. Excel 结构验证

验证 14 列结构：story_id, node_path, name, summary, precondition, steps, expected, actual, priority, author, type, need_regression, app, tags。若列不匹配则报错。

## 5. 步骤文本分割

按换行符 / 分号 / 编号分隔 steps 文本为独立步骤。
