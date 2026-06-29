---
name: manage-interface
description: 新增/更新/查询渠道接口定义，同步维护渠道JSON和接口文档缓存
argument-hint: "<channel> <operation> [interface_def]"
---

# manage-interface

维护渠道接口定义：新增接口、更新已有接口、查询接口列表。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| channel | string | 是 | 渠道标识，如 TouTiao、PingAnPh |
| operation | string | 是 | CRUD 操作：add / update / query / delete |
| interface_def | object | 否 | 接口定义（add/update 时必填） |

## 执行逻辑

### query — 查询接口
1. 读取 `memory/api_channels/{channel}.json`
2. 调用 `testmind:auto-interface-list` 获取平台列表
3. 返回本地 + 平台的双视图

### add — 新增接口
1. 验证 interface_def 必填字段：method, label, params, param_fields
2. 读取渠道 JSON，追加到 interfaces 数组
3. 验证 JSON 格式正确
4. 写入文件

### update — 更新接口
1. 在渠道 JSON 中定位目标 method
2. 合并更新字段
3. 写入文件

### delete — 删除接口
1. 在渠道 JSON 中定位目标 method
2. 标记删除（软删除或物理删除，根据用户选择）

## 输出

```json
{
  "channel": "TouTiao",
  "operation": "add",
  "method": "newMethod",
  "status": "success",
  "file_updated": "memory/api_channels/TouTiao.json"
}
```

## 规则

1. JSON 写入后验证格式完整性
2. add/update/delete 操作后记录变更原因
3. params 字段必须 JSON.stringify 处理
