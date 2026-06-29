---
name: story-manage-transition-requires-from-status
description: story-manage 状态流转必须传 --from-status，否则报错 data_list 缺少 status 键
metadata:
  type: feedback
---

testmind:story-manage 的 `transition` 命令执行故事状态流转时，**必须同时传入 `--from-status`（当前状态）和 `--test-type`（测试形式）**，否则会失败。

**错误示例**（缺少 --from-status）：
```bash
python story_manage.py transition --key "JYSG-149007" --change-status "冒烟测试" --real-time false
# → flag=F, msg="data_list中的Python字典数据, 必须有status键(状态)!"
```

**正确示例**：
```bash
python story_manage.py transition \
  --key "JYSG-149007" \
  --from-status "等待测试" \
  --change-status "冒烟测试" \
  --test-type "标准IT测试" \
  --real-time false
```

**Why:** 脚本内部用 `--from-status` 构建 workflow graph 查找最短流转路径，不传则 data_list 缺少 status 键导致接口报错。`--test-type` 也是某些流转路径的必要参数。

**How to apply:** 每次调用 story-manage transition 时，必须先查询故事当前状态，然后同时传入 `--from-status`、`--change-status`、`--test-type` 三个参数。
