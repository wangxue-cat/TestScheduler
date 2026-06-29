import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

result = subprocess.run([
    'curl', '-s', '-H',
    'token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMDYsInVzZXJuYW1lIjoid2FuZ3h1ZS1qayIsImV4cCI6MTgxMDc5NDQxMywiZW1haWwiOiJ3YW5neHVlLWprQHFpZnUuY29tIn0.Aq6J10omCPErhkViGdTx4LPk0geSu51IxzDvriFUphQ',
    'http://lingxi-qoa-app.daikuan.qihoo.net/pipeline/api/testFlowAnalyze/?sprint_name=20260618%20%E8%BF%AD%E4%BB%A3%E7%89%88%E6%9C%AC'
], capture_output=True, timeout=30)

data = json.loads(result.stdout.decode('utf-8'))

if data.get('flag') == 'S':
    results = data['results']
    no_case = data.get('no_case_request', [])

    print('## 测试流程及时性诊断 — 20260618 迭代版本\n')

    # Extract the actual keys from first result
    key_map = {}
    for raw_k in results[0].keys():
        print(f'  Raw key: {repr(raw_k)}')
    print()

    for r in results:
        # Try to extract meaningful data
        vals = list(r.values())
        keys = list(r.keys())
        # The structure seems to be: group_name, leader, total, exec_rate, ...
        print(f'组: {vals[0] if len(vals)>0 else "?"} | 负责人: {vals[1] if len(vals)>1 else "?"}')
        for i, (k, v) in enumerate(zip(keys, vals)):
            if i < 2: continue
            print(f'  {i}: {v}')
        print()

    if no_case:
        print(f'### 无用例需求 ({len(no_case)}个)')
        for nc in no_case[:15]:
            print(f'- {nc.get("key","?")}: {str(nc.get("summary","?"))[:80]}')
else:
    print(f'API Error: {data.get("msg","?")}')
