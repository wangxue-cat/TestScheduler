# NREQUEST-47453 开发文档

## Confluence 设计文档

| 来源 | 链接 |
|------|------|
| 需求关联 Confluence | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=97682910 |
| 相关需求（大前端） | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=94719575 |
| 需求背景 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=44502580 |

## 涉及应用

| 应用 | Story | 开发负责人 |
|------|-------|-----------|
| cas-batch-app | JYSG-148393 | dengbin-jk |
| cas-app | JYSG-148393 | dengbin-jk |
| gws-aps-web | JYSG-148392 | leiyueping-jk |
| aps-app | JYSG-148392 | leiyueping-jk |

## 涉及接口（来自需求描述）

- **5.1.4 授信信息变更申请** — APS → 蚂蚁
- **5.1.5 授信信息变更结果** — 蚂蚁 → APS

## 数据流

```
CAS(调额申请) → APS(发起调额) → 蚂蚁(审核)
                                    ↓
CAS(接收结果) ← APS(返回结果) ← 蚂蚁(审核通过/失败)
```

- CAS 接收结果后有 6 次重试机制
- 重试失败 → 人工介入处理
- 初期设置 24 小时等待期
