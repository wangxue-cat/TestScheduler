# 5 阶段执行协议

所有 testmind 技能调用必须遵循此协议。

## Phase 1: LOAD — 加载经验

```
检查 experience/{skill-name}.md 是否存在
  ├─ 存在 → 读取，将策略/踩坑加载到上下文
  └─ 不存在 → 从 refs/experience-template.md 创建 stub
```

**关键**：经验文件中的「核心原则」和「执行策略」在当前调用开始前必须已进入上下文。

## Phase 2: RESOLVE — 解析路由

查 `refs/skill-registry.md`：

```
testmind:{skill-name}
  ├─ 有本地 wrapper（delegated）？
  │   └─ 是 → 委托给本地 wrapper（如 sql-execute → agents/test-runner/skills/sql-execute/）
  └─ 无本地 wrapper（direct）？
      └─ 直接调用 Skill(testmind:{skill-name})，但带着经验上下文
```

## Phase 3: EXECUTE — 执行

带着 Phase 1 加载的经验规则执行：

- 优先采用「执行策略」中匹配的策略
- 避开「核心原则」中标记的禁止路径
- 参考「已知踩坑」避免重复错误

## Phase 4: OBSERVE — 观察

执行完成后检查：

| 观察项 | 判断标准 |
|--------|---------|
| 出现意外行为？ | 返回结果与预期不符、报错、路径无效 |
| 发现新映射/模式？ | 系统→应用映射、参数取值规则、路径格式 |
| 验证了已有模式？ | 某条「已验证模式」再次被确认 |
| 踩到已知坑？ | 某条「已知踩坑」再次发生 |

> 若以上全部为"否"，跳过 Phase 5。

## Phase 5: WRITE-BACK — 写回

向 `experience/{skill-name}.md` 追加：

- **新踩坑** → 追加到 `<!-- EVOLUTION_MARKER: pitfalls -->` 下方
- **新模式** → 追加到 `<!-- EVOLUTION_MARKER: patterns -->` 下方，`确认次数=1`
- **模式确认** → 更新已存在模式的确认次数
  - 累计 ≥3 次 → 升级到「执行策略」或「核心原则」
- 更新 metadata：`evolution_count += 1`, `last_updated`

### 写回格式

```markdown
### 坑{N}: {标题}
- **日期**: {YYYY-MM-DD}
- **现象**: {实际表现}
- **原因**: {根因分析}
- **解决**: {有效方案}
- **教训**: {可复用教训}
- **来源**: {触发上下文}

### 模式{N}: {标题}
- **日期**: {YYYY-MM-DD}
- **发现**: {具体描述}
- **确认次数**: {N}
- **来源**: {触发上下文}
```
