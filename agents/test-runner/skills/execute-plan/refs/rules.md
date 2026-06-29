# execute-plan 详细规则

## 1. 接口执行方式

接口执行**仅使用** `testmind:auto-interface-exec`（通过 `platform_id` 执行），不尝试其他方式。

## 2. 失败不降级

若 `auto-interface-exec` 执行不通，**停止并报告失败**，不探索 `dubbo-call`、HTTP 直连等其他途径。

## 3. 步骤失败隔离

一个步骤失败不终止整个 case（除非失败步骤是 io_bindings 上游步骤）。

## 4. Case 缓存隔离

每个 case 独立缓存，`_response_cache[case_idx]` 隔离。

## 5. 超时设置

- 接口调用：30s
- DB 查询：10s

## 6. 失败分析分离

执行过程中不分析失败原因（由 Result Analyst 负责）。

## 7. 小工具统一入口

所有小工具调用（随机生成、用户查询、加解密等）必须通过本项目 `execute-tool` skill，禁止绕过直接调 HTTP 或 `testmind:common_tool_execute`。

## 8. 环境确认

首次执行必须经用户确认环境（STG1/STG2），检查 testmind token 可用性，确认目标服务可达。

## 9. Apollo 配置修改验证

执行计划中涉及 Apollo 配置修改的步骤时：

1. 执行修改 → 若返回超时，**不可直接假定生效**
2. **调用 Apollo 查询接口**重新获取当前值，确认是否等于目标值
3. 查询确认修改成功 → 继续执行后续业务步骤
4. 查询显示未修改成功 → 重试修改，再次查询确认；重试仍失败则暂停并报告

> ❌ 禁止跳过查询确认直接跑业务 — 若配置实际未生效，业务验证结果不可信
> 参见 [[apollo-timeout-but-effective]]
