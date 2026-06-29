---
name: api-testcase-writer
description: 核心用例编写技能，7步生成流水线：解析需求ID→重复检查→加载材料→识别渠道→应用编写规则→生成Excel→输出摘要
argument-hint: "<requirement_id>"
---

# api-testcase-writer

根据需求 ID 读取本地材料目录，识别渠道，按规则生成 14 列测试用例 Excel。

## 🚫 硬性禁令（最高优先级，不可违反）

以下行为**绝对禁止**，违反即为执行错误：

| 禁止行为 | 说明 |
|---------|------|
| ❌ 访问 Confluence | 材料已由 Requirement Collector 拉取到本地，**禁止**再去 Confluence 找资料 |
| ❌ 访问灵犀/WebFetch | **禁止**自行搜索或抓取任何网页获取需求信息 |
| ❌ 自行查找接口文档 | 只允许调用 `run.py find-interface-doc`，**禁止**直接去 `D:/接口文档合集/` 翻文件、搜索文件名、或用其他方式找接口文档 |
| ❌ 接口文档找不到时自己想办法 | 找不到 → **立即停止并提示用户提供**，**禁止**绕过、猜测接口名、或用 api_channels JSON 替代 |
| ❌ 访问代码仓库 | **禁止** clone/pull/读取代码，代码分析不在本 Skill 职责范围 |

**唯一合法的信息来源**：
1. `memory/requirement_materials/{req_id}/` 下的本地文件（Read）
2. `run.py find-interface-doc` 的返回结果
3. `testcase_writing_rules.md` 规则文件
4. 用户直接提供的输入

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | string | 是 | 需求编号 |

## 7 步流水线

1. **解析需求 ID** — 从输入中提取 NREQUEST-xxxxx / JYSG-xxxxx
2. **重复检查** — 调用 `run.py check-existing-testcases` 检查是否已有用例文件
3. **加载材料** — 仅 Read `memory/requirement_materials/{req_id}/` 下的本地文件
4. **识别渠道** — 从需求文档中提取渠道名 → 调用 `run.py find-interface-doc`（**唯一合法方式**）：
   - MD 缓存命中 → 使用
   - 原始文档自动转换 → 使用
   - **都未找到 → 立即停止，提示用户提供接口文档，禁止继续**
5. **应用编写规则** — 读取 `testcase_writing_rules.md`，严格按规则生成用例
6. **生成 Excel** — 调用 `run.py generate-excel`，14 列输出
7. **输出摘要** — 用例数、按渠道/优先级分布、文件路径

## 输出

- `memory/testcases/{req_id}_testcases.xlsx`

## 规则

用例编写规则详见 `testcase_writing_rules.md`，本 Skill 执行时**必须读取该文件**并按最新规则生成用例。
