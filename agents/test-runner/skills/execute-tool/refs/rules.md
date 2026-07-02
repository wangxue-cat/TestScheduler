# execute-tool 详细规则

## 1. 强制统一入口

TestScheduler 项目**所有小工具调用必须通过此 skill**，禁止绕过。

禁止方式：
- ❌ 直接裸 HTTP 请求（urllib.request / requests / curl）
- ❌ 绕过 `Skill(testmind:common-tool-execute)` 直接调底层脚本

## 2. Token 管理

Token 从 `d:\TestScheduler\memory\innovate_tools_api\token.txt` 读取。

若 token 为空或文件不存在，提示用户配置 token 后重试。

## 3. 工具匹配策略

从 `d:\TestScheduler\memory\innovate_tools_api\innovate_tools_api_catalog.md` 中按功能描述匹配：

- 按工具名精确匹配（如 "getUserInfo"）
- 按功能分类 + 描述模糊匹配（如 "随机手机号" → #20 random-mobileNo、"查询用户" → #1 getUserInfo）
- 匹配到多条 → 列出候选让用户选择
- 未匹配到 → 告知用户未找到对应工具

## 4. 参数组装

根据 catalog 中的定义组装参数：

- 工具参数：从 catalog 获取参数列表和类型
- env：默认 STG2，可通过参数覆盖为 STG1/STG3

## 5. 执行（QOA 追踪）

> 🚫 **禁止直接 HTTP 调用**。必须通过 `Skill(testmind:common-tool-execute)` 执行。

```
Skill(testmind:common-tool-execute, "<工具名> <参数JSON> --env <环境>")
```

Skill 内部自动处理 token 注入、HTTP 请求和响应解析，QOA 平台通过 `testmind:schedule` 追踪执行次数。

## 6. 默认环境

默认环境 STG2，可通过参数覆盖为 STG1/STG3。
