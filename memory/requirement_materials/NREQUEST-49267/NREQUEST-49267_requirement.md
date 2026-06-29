# NREQUEST-49267: aps库大表order_repay_withhold治理

## 需求基本信息

| 字段 | 值 |
|------|-----|
| 需求编号 | NREQUEST-49267 |
| 需求标题 | aps库大表order_repay_withhold治理 |
| 状态 | 50开发完成 |
| 迭代版本 | 20260618 迭代版本 |
| 技术领域(Story) | JYSG-148994 |
| Story状态 | 等待测试 |
| 项目 | API端外渠道合作,(227)API渠道能力扩展及赋能 |
| IT负责人 | zhanghao6-jk |
| 开发人员 | zhanghao6-jk, guiqingqing-jk |
| 测试人员 | wangxue-jk |
| 测试类型 | 标准IT测试 |
| 预计转测时间 | 2026-06-12 |
| 优先级 | 中 |
| 应用 | aps-app |
| 是否有Confluence | 否 |

## 需求内容

当前order_repay_withhol表行数及内存占用较大，且该表每日增量很大，对aps库存储压力日渐提升，为了缓解aps库压力，结合该表使用特性。本次aps接入ocean base数据源，以mysql库为主(近存储热数据)，ocean base为辅。mysql后续按创建时间分区，只保留近1个月数据，内存占用高预计降低95%。

## 开发文档概要

> 完整开发文档见：[order_repay_withhold_冷热分离改造设计文档.html](./order_repay_withhold_冷热分离改造设计文档.html)

### 1. 项目背景与问题

APS 系统的 `order_repay_withhold` 表为 MySQL 5.6 表，当前面临严重的存储和性能问题：

| 指标 | 当前值 | 影响 |
|------|--------|------|
| 存储空间 | 超过 800G | 磁盘容量告警，影响整体数据库性能 |
| 数据行数 | 2.8 亿 | 查询性能下降，定时任务扫描耗时长 |
| MySQL 版本 | 5.6 | 不支持分区表优化等新特性 |

### 2. 改造目标

1. **数据冷热分离**：最近两个月的数据为热数据，存储在 MySQL 新表中；冷数据（全量）存储在 OceanBase 中
2. **写入层面**：前期三写（旧MySQL + 新MySQL + OB），迁移完成后改为双写（新MySQL + OB）
3. **读取层面**：迁移前查旧表，迁移后先查新热表，miss 则查 OB
4. **数据迁移**：将三写开启前的历史数据迁移到 OB，迁移过程中保持数据一致

### 3. 整体架构

```
上层调用方（无需改动）
  → OrderRepayWithholdServiceImpl（内聚路由逻辑）
    ├── 旧MySQL DAO（现有）
    ├── 新MySQL热表 DAO（新增，同库同实例）
    └── OB DAO（新增，异步写入）
         ├── 旧MySQL表（同DataSource）
         ├── 新MySQL热表 order_repay_withhold_hot（同DataSource）
         └── OB表 order_repay_withhold_backup（OB DataSource）
```

### 4. 四阶段划分

| 阶段 | 写入 | 读取 | Apollo开关 |
|------|------|------|-----------|
| 三写期 | 旧MySQL + 新MySQL（本地事务）+ OB（先同步写，失败走MQ） | 只查旧MySQL | writeMode=TRIPLE, readNew=false |
| 迁移期 | 同三写期 | 只查旧MySQL | writeMode=TRIPLE, readNew=false |
| 切读期 | 同三写期 | 先查新热表，miss则查OB | writeMode=TRIPLE, readNew=true |
| 双写期 | 新MySQL + OB（先同步写，失败走MQ） | 先查新热表，miss则查OB | writeMode=DUAL, readNew=true |

### 5. Apollo开关设计（4个开关）

| 开关 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `aps.apollo.config.repayWithholdWriteMode` | String | OLD_ONLY | 写入模式：OLD_ONLY / TRIPLE / DUAL |
| `aps.apollo.function.switch.repayWithholdReadNew` | boolean | false | 读取路由开关 |
| `aps.apollo.function.switch.repayWithholdObWriteLog` | boolean | false | OB写入日志开关 |
| `aps.apollo.function.switch.repayWithholdObReadLog` | boolean | false | OB读取日志开关 |

### 6. 核心改造点

#### 写入层（OrderRepayWithholdServiceImpl）
- **insertSelective**: 根据writeMode路由到旧表/热表/OB
- **updateRepayEntityByRepayTranNoAndState**: 乐观锁更新，根据writeMode路由
- **updateRepayEntityByRepayTranNo**: 无乐观锁更新，独立处理（不能委托给上述方法）
- **saveRepayInfo**: 同时写withhold表和detail表
- OB写入为事务提交后异步（先同步写OB，异常降级MQ）

#### 读取层（OrderRepayWithholdServiceImpl）
- 单条查询：先查热表，miss则查OB
- 批量查询（queryRepayList）/ 聚合查询（selectMaxEntity等）：只查热表
- 涉及8个查询方法的路由改造

#### 数据迁移
- 新增 `OrderRepayWithholdMigrationTask` 定时任务
- 基于ID范围分批迁移（每批1万条）
- 迁移范围：三写开启前创建的数据
- 迁移后二次校验（按ID范围扫描比对关键字段）
- 迁移进度表持久化

#### 抽样数据比对监控
- 新增 `OrderRepayWithholdDataCompareTask`
- 按ID等间隔抽样（每1000条抽1条）
- 比对旧MySQL表 vs OB表关键字段
- 差异输出WAN告警日志

### 7. 涉及数据表

| 表名 | 位置 | 说明 |
|------|------|------|
| order_repay_withhold | 旧MySQL | 现有表，2.8亿行，超过800G |
| order_repay_withhold_hot | 新MySQL（同库） | 热表，按月分区，只保留近2个月数据 |
| order_repay_withhold_backup | OceanBase | 备份表，全量冷数据，按月分区 |
| order_repay_withhold_detail | 旧MySQL | 现有detail表（不变） |
| order_repay_withhold_migration_record | 新MySQL | 迁移进度记录表 |

### 8. 改造文件清单

**新增文件（13个）**:
- RepayWithholdWriteModeEnum.java - 写入模式枚举
- OrderRepayWithholdHotDao.java + Mapper.xml - 热表DAO
- OrderRepayWithholdObDao.java + Mapper.xml - OB DAO
- ObWriteProducer.java + ObWriteConsumer.java - OB MQ
- ApsObWriteMessage.java - OB消息体
- OrderRepayWithholdMigrationTask.java - 迁移任务
- OrderRepayWithholdDataCompareTask.java - 比对监控任务
- OrderRepayWithholdMigrationRecordDao.java + Mapper.xml - 迁移进度
- spring-mybatis-ob.xml - OB数据源配置

**修改文件（6个）**:
- spring-mybatis.xml - 引入OB配置
- datasource.properties - 增加OB连接参数
- ApsApolloConfiguration.java - 增加writeMode配置
- OrderRepayWithholdServiceImpl.java - 核心读写路由
- OrderRepayWithholdDao.java - 新增查询方法
- OrderRepayWithholdMapper.xml - 新增SQL

### 9. 上线步骤（12步）

1. 部署代码（所有开关默认关闭）
2. 创建新热表 order_repay_withhold_hot
3. 创建OB表
4. 配置OB数据源，重启应用
5. 开启三写 writeMode=TRIPLE
6. 启动迁移任务
7. 迁移完成，验证数据一致性
8. 切换读取路由 readNew=true（切读期）
9. 切读期观察1周左右
10. 停写旧表 writeMode=DUAL
11. 启动抽样比对监控任务
12. 后续清理（不在本次改造范围）

### 10. 已知风险

1. **旧表无date_updated索引**：二次校验和抽样比对已改为按ID扫描走主键索引
2. **分区表主键必须包含分区键**：热表主键改为(date_created, id)，id保留自增但非主键前缀

### 11. 评审建议要点

1. 先切读，持续一周左右，再停写旧MySQL表
2. 先写OB，OB写失败后才走MQ；读OB时输出日志并加开关
3. OB表建分区表
4. 新建MySQL表按月分区
5. 新分区创建监控（月初检查）
6. 分区数据清理监控（分区数>6告警）
7. 抽样比对：按起始ID等间隔抽取，比对旧MySQL表与OB表
8. 三写持续两三天后开始迁移，迁移按ID从小到大
