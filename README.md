# 无障碍设施评价系统

基于 T/CNAEC 1304—2022《民用建筑无障碍设施评价标准》的评价认证平台。

## 功能特性

- 支持4种建筑类型评价（住宅类、非住宅类居住建筑、含/不含住宿功能的公共建筑）
- 完整的评分体系（Q1-Q5 + 施工验收 + 运行维护）
- 控制项闸门检查（不达标不予评级）
- 建筑类型策略模式（不同建筑类型自动适配评价维度和公式）
- 设施实体逐项评分（支持动态增减设施）
- 建筑群综合评分（ZQ = Z1×80% + Z2×20%）
- 星级评定（一/二/三星级）

## 技术栈

- **后端**: FastAPI + SQLAlchemy 2.0 + Pydantic v2
- **数据库**: SQLite（开发）/ PostgreSQL（生产）
- **评分引擎**: 纯函数计算，幂等化设计
- **测试**: pytest + httpx

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等参数
```

### 3. 初始化数据库

```bash
python3 init_db.py
```

### 4. 运行服务

```bash
python3 -m uvicorn main:app --reload
```

服务将在 http://localhost:8001 启动，API文档访问 http://localhost:8001/docs

## 核心API

### 项目管理
- `POST /projects/` - 创建评价项目
- `GET /projects/` - 查询项目列表
- `GET /projects/{id}` - 查询项目详情

### 建筑管理
- `POST /buildings/` - 添加建筑
- `GET /buildings/project/{project_id}` - 查询项目下建筑列表

### 评分录入
- `POST /scoring/control-items/{building_id}` - 录入控制项
- `POST /scoring/system-scores/{building_id}` - 录入系统评分
- `POST /scoring/facilities/{building_id}` - 添加设施实体
- `POST /scoring/facilities/{facility_id}/scores` - 录入设施评分

### 评价计算
- `POST /scoring/evaluate/{building_id}` - 执行完整评价计算
- `GET /scoring/results/{building_id}` - 查询评价结果
- `POST /scoring/complex/{project_id}` - 建筑群综合评分

### 标准条文
- `POST /standard-clauses/` - 创建标准条文
- `GET /standard-clauses/` - 查询标准条文列表
- `GET /standard-clauses/chapter/{chapter}` - 按章节查询

## 评分计算流程

```
Step 1: 控制项闸门检查 → 任一不达标则不予评级
Step 2: 系统评分 S 计算 → 参评项归一化得分 × 100
Step 3: 设施实体逐项评分 → 各类平均 → F分
Step 4: 维度分 Q 计算 → Q = S × (F/10)
Step 5: 总体评价 Q 计算 → 根据建筑类型选择公式
Step 6: 建筑群综合计算 → ZQ = Z1×80% + Z2×20%
Step 7: 等级认定 → 对照阈值表评定星级
```

## 建筑类型适配

| 建筑类型 | 参评维度 | 总分公式 |
|---------|---------|---------|
| 住宅类居住建筑 | Q1, Q3, Q4, Q5 | (Q1+Q3+Q4)/3 + Q5 |
| 非住宅类居住建筑 | Q1, Q2, Q3, Q4, Q5 | (Q1+Q2+Q3+Q4)/4 + Q5 |
| 含住宿功能公共建筑 | Q1, Q2, Q3, Q4, Q5 | (Q1+Q2+Q3+Q4)/4 + Q5 |
| 不含住宿功能公共建筑 | Q1, Q2, Q4, Q5 | (Q1+Q2+Q4)/3 + Q5 |

## 等级划分

| 等级 | 控制项 | 各维度最低分 | 总体Q | 施工验收 | 运行维护 |
|------|--------|-------------|-------|---------|---------|
| 一星级 | 全部达标 | ≥20 | ≥40 | ≥60 | ≥60 |
| 二星级 | 全部达标 | ≥40 | ≥60 | ≥70 | ≥70 |
| 三星级 | 全部达标 | ≥60 | ≥80 | ≥80 | ≥80 |

## 测试

```bash
# 运行所有测试
python3 -m pytest tests/ -v

# 运行单元测试
python3 -m pytest tests/test_scoring_engine.py -v

# 运行集成测试
python3 -m pytest tests/test_integration.py -v
```

## 项目结构

```
.
├── app/
│   ├── api/              # API路由
│   ├── core/             # 核心配置、枚举、数据库
│   ├── models/           # SQLAlchemy数据模型
│   ├── schemas/          # Pydantic模型
│   └── services/         # 业务逻辑和评分引擎
├── tests/                # 测试文件
├── main.py               # 应用入口
├── init_db.py            # 数据库初始化
├── requirements.txt      # 依赖
└── .env.example          # 环境变量示例
```

## 数据库模型

- **Project** - 评价项目
- **Building** - 建筑
- **StandardClause** - 标准条文
- **FacilityCategory** - 设施类别
- **ControlItemCheck** - 控制项核查记录
- **SystemScoreDetail** - 系统评分明细
- **FacilityEntity** - 设施实体
- **FacilityScoreDetail** - 设施评分明细
- **DimensionScore** - 维度得分计算结果
- **ComplexBuildingScore** - 建筑群综合评分

## 许可证

MIT