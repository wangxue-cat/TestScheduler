# verify-field-compare 详细规则

## 1. 字段扩展查询

当计划中的 `compare_fields` 少于实际表字段时，查询全部列做完整比对。计划中的 compare_fields 是**最小集合**。

## 2. 字符串规范化

字符串字段比对前去除首尾空格。

## 3. 数值类型统一

数值字段统一转为字符串比对（DB 可能返回字符串类型）。

## 4. NULL 处理

NULL 与空字符串视为等价（除非计划另有说明）。

## 5. 时间戳容差

`date_updated` 类时间戳允许 ±2 秒偏差（异步写入延迟）。见 [[ob-async-write-lag]]。

## 6. 严重等级分类

| 等级 | 条件 | 示例 |
|------|------|------|
| `critical` | id 不一致 | 旧表 id=202, 热表 id=203 |
| `major` | 业务字段不一致 | amount, state, withhold_state 不同 |
| `minor` | 时间戳微小偏差 | date_updated 差 1 秒 |
