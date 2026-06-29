# NREQUEST-49352 代码仓库

## 关联代码仓库

> 以下为根据需求内容推断的可能关联仓库，需用户确认。

| 仓库 | 本地路径 | 涉及条目 | 推断依据 |
|------|---------|---------|---------|
| APS | D:\project\aps | 条目1（部署优化）、条目2（日常巡视BUG） | APS 系统部署优化、订单处理相关 |
| GWS-APS | D:\project\gws-aps | 条目2（API 网关相关） | API 网关/流量相关巡视问题 |

## 需要确认

1. 是否还有其他关联仓库（如 API 渠道模块）？
2. 各仓库的 Sprint 分支是什么？
3. 代码变更是否已合入主分支？

## 状态

未能通过 testmind:get-repo-code-diff 获取代码变更信息（Bash 不可用）。需在 Code Analyzer Agent 阶段通过 setup-repo → fetch-code-diff 获取。
