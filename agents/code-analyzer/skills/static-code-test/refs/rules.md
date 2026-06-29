# static-code-test 详细规则

## 严重度分级

| 等级 | 标签 | 定义 | 示例 |
|------|------|------|------|
| Blocker | 🔴 | 线上必现故障，必须立即修复 | 金额计算错误、事务不完整导致数据不一致 |
| Critical | 🟠 | 高风险，大概率触发线上问题 | 关键路径 null 解引用、资源泄漏、线程安全问题 |
| Major | 🟡 | 中等风险，特定条件触发 | 边界条件未处理、异常被吞没 |
| Minor | 🟢 | 低风险，影响可维护性 | 硬编码值、命名不规范 |
| Suggestion | ⚪ | 改进建议，不构成缺陷 | 优化写法、简化逻辑 |

## 硬编码值检测规则

检测以下应配置化但直接写在代码中的字面量：

1. **IP 地址和端口**：`192.168.x.x`, `localhost:8080`
2. **URL 路径**：`http://` 或 `https://` 开头的字符串
3. **密钥/Token**：包含 `key`, `secret`, `token`, `password` 等关键字的字符串
4. **魔法数字**：业务逻辑中的裸数字（非 0, 1, -1 的上下文相关数字）
   - ✅ `if (list.size() == 0)` — 可接受
   - ❌ `if (amount.compareTo(new BigDecimal("50000")) > 0)` — 应定义为常量 `MAX_AMOUNT`
5. **业务枚举值**：直接写 `"SUCCESS"`, `"FAILED"` 等状态字符串
6. **超时时间**：`timeout = 3000` — 应配置化
7. **Apollo 配置 Key 硬编码**：直接写配置 Key 字符串而非引用常量

## 空安全规则

1. **方法返回值未做 null check 直接使用** → **高风险**
   ```java
   // ❌ 危险
   Order order = orderMapper.selectById(id);
   order.getAmount(); // order 可能为 null
   ```
2. **Optional.orElse(null) 或 Optional.get() 无 isPresent** → **中风险**
3. **@Nullable 注解的方法返回值未被检查** → **中风险**
4. **Collection 返回值直接遍历无 empty check** → 通常**低风险**（空集合一般不会返回 null）

## 边界条件规则

1. **数值计算无除零检查** → **高风险**
2. **金额计算使用浮点类型** → **高风险**（应用 BigDecimal）
3. **分页参数无上限** → **中风险**（可导致 OOM）
4. **日期范围无边界校验** → **中风险**
5. **字符串截取无长度检查** → **低风险**

## 逻辑错误模式

1. **条件判断反转**：`if (success)` 内的逻辑看起来像失败处理
2. **死代码**：`if (true)` / `if (false)` / `return` 后的代码
3. **Switch 穿透**：缺少 `break` 的 case
4. **条件恒真/恒假**：`if (a != null && a == null)` 等矛盾条件
5. **赋值替代比较**：`if (a = b)` (Java 中不常见但 C-style 遗留)
6. **异常吞噬**：catch 块为空或只打日志不处理
7. **事务中的 try-catch**：catch 后不抛异常导致事务不回滚

## 资源管理规则

1. **IO 流未在 finally/try-with-resources 中关闭** → **高风险**
2. **数据库连接未归还连接池** → **高风险**
3. **HTTP 客户端 response body 未关闭** → **中风险**

## 事务边界规则

1. **@Transactional 方法中 catch 了 RuntimeException 且未重新抛出** → **高风险**
   ```java
   // ❌ 事务不会回滚
   @Transactional
   public void process() {
       try { ... }
       catch (Exception e) { log.error(e); } // 吞掉异常，事务提交
   }
   ```
2. **非 public 方法上的 @Transactional** → **中风险**（Spring 代理限制）
3. **同类方法调用 @Transactional** → **中风险**（自调用不走代理）
4. **事务范围过大** → **低风险**（包含不必要的 RPC/HTTP 调用）

## 线程安全规则

1. **共享可变状态无同步** → **高风险**
2. **双重检查锁实现有误** → **高风险**（应使用 volatile + synchronized）
3. **ConcurrentHashMap 的复合操作无原子性保证** → **中风险**
   ```java
   // ❌ putIfAbsent + get 不是原子的，可能拿到过期值
   map.putIfAbsent(key, value);
   return map.get(key);
   ```

## 覆盖缺口分析规则

1. **核心业务方法变更 + 无任何测试用例覆盖** → **Critical**
2. **新增 public 方法 + 无测试用例调用** → **Major**
3. **新增 if 分支 + 仅一侧有测试覆盖** → **Major**
4. **异常处理逻辑变更 + 无异常场景测试** → **Major**
5. **配置项新增 + 无"配置关闭/开启"两侧测试** → **Minor**

## 用例过时检测规则

1. 测试步骤中引用的方法/类**在 diff 中被删除** → 用例过时
2. 测试步骤中引用的接口参数**在 diff 中被移除** → 用例过时
3. 测试步骤中引用的 DB 表/字段**在 diff 中被删除** → 用例过时
