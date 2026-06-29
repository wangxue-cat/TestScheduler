# execute-tool 详细规则

## 1. 强制统一入口

TestScheduler 项目**所有小工具调用必须通过此 skill**，禁止绕过。

禁止方式：
- ❌ 直接使用 `testmind:common_tool_execute`
- ❌ 裸 HTTP 请求

## 2. Token 管理

Token 从 `d:\TestScheduler\memory\innovate_tools_api\token.txt` 读取。

若 token 为空或文件不存在，提示用户配置 token 后重试。

## 3. 工具匹配策略

从 `d:\TestScheduler\memory\innovate_tools_api\innovate_tools_api_catalog.md` 中按功能描述匹配：

- 按工具名精确匹配（如 "getUserInfo"）
- 按功能分类 + 描述模糊匹配（如 "随机手机号" → #20 random-mobileNo、"查询用户" → #1 getUserInfo）
- 匹配到多条 → 列出候选让用户选择
- 未匹配到 → 告知用户未找到对应工具

## 4. HTTP 请求组装

根据 catalog 中的定义组装请求：

- **URL**: 从 catalog 中获取完整 URL
- **Method**: POST 或 GET
- **Headers**: `Content-Type: application/json`、`token: <Step 1 的 token>`
- **Body**: 工具参数 + `env`（必填）

## 5. 执行与超时

通过 Python HTTP 请求发送，超时 30s：

```bash
python -c "
import urllib.request, json
url = '<工具URL>'
headers = {'Content-Type': 'application/json', 'token': '<token>'}
data = json.dumps({...}).encode()
req = urllib.request.Request(url, data=data, headers=headers, method='POST')
resp = urllib.request.urlopen(req, timeout=30)
print(resp.read().decode())
"
```

## 6. 默认环境

默认环境 STG2，可通过参数覆盖为 STG1/STG3。
