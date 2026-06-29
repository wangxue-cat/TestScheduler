# generate-execution-plan 详细规则

## 1. platform_id 透传

从 match-platform-interface 的匹配结果中提取 `platform_id`，原样写入执行计划每个步骤，供 execute-plan 通过 `testmind:auto-interface-exec` 按 ID 执行。不可修改或猜测 platform_id。

## 2. io_bindings 处理

io_bindings 缺失的依赖标记为 `pending_data`，不阻塞生成。验证规则：
- 上游 method 必须在当前 case 的步骤中出现
- 依赖字段必须在 from_method 的 response 中有定义

## 3. 外部参数

外部参数（external_params）将在 assemble-params 阶段填充，此时仅标记来源未知。

## 4. Schema 验证

写入文件前验证 JSON schema 完整性，确保所有必填字段存在。
