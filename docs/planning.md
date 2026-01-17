# Project Activity Analytics Dashboard

> **项目类型**：工程 + 数据分析 + 可视化
>
> **目标岗位适配**：Microsoft / Accenture / 外企技术实习
>
> **核心差异点**：项目健康度评分（Project Health Score） + 对比分析 + 自动解释

---

## 一、项目背景与目标

### 1.1 背景

在真实的软件团队中，管理者和工程师往往需要快速判断：
- 一个项目是否**健康、可持续**？
- 团队协作是否存在**单点依赖或风险**？
- 项目当前的活跃度变化是否**值得关注**？

然而，大多数现有工具仅展示**原始活动数据**（commit 数、contributors 数），缺乏对项目状态的**综合判断与解释能力**。

### 1.2 项目目标

本项目旨在构建一个 **项目活跃度与健康度可视化分析平台**，通过数据采集、指标建模和交互式可视化：

- 直观展示项目开发活动
- 量化评估项目健康度（Health Score）
- 支持时间趋势与多项目对比
- 提供可解释的分析结论，辅助决策

---

## 二、项目总体成果形式（成品应当是什么样）

### 2.1 最终交付物

- 一个 **Web Dashboard**（浏览器访问）
- 一个 **后端服务**（负责数据采集与分析）
- 一个 **完整 GitHub 项目仓库**，包含：
  - 清晰的 README
  - 架构说明
  - 工程取舍说明（Engineering Trade-offs）

### 2.2 成品展示效果（文字描述）

用户打开页面后可以：
- 输入或选择 GitHub 仓库
- 查看项目总体健康评分（0–100）
- 浏览 commit 活跃度热力图
- 查看代码变更趋势（add / delete）
- 分析贡献者分布与协作风险
- 对比不同时间段或不同项目

---

## 三、系统整体架构设计

```
GitHub API
    ↓
Data Collector（Python）
    ↓
Data Processor & Metrics Engine
    ↓
Database（SQLite / PostgreSQL）
    ↓
FastAPI Backend
    ↓
Web Dashboard（ECharts / Chart.js）
```

---

## 四、阶段化开发规划（从 0 到 1）

> 每个阶段都应 **可运行、可展示、可写进简历**

---

### 阶段 0：项目定义与准备（Day 1–2）

**目标**：明确边界，避免一开始做大做散

#### 本阶段目标
- 明确 MVP 功能范围
- 确定技术栈
- 搭建项目目录结构

#### 关键产出
- 项目 README 初稿
- 技术选型说明
- 空跑通的 FastAPI 项目

---

### 阶段 1：数据采集模块（Week 1）

**目标**：稳定、可复用地获取 GitHub 数据

#### 功能目标
- 拉取指定仓库的 commit 数据
- 支持分页与基础限流处理
- 将原始数据存入数据库

#### 技术点
- GitHub REST API
- API rate limit 处理
- 数据缓存策略

#### 阶段完成标准
- 能成功拉取一个中型仓库的 commit 历史
- 数据结构清晰，可复用

---

### 阶段 2：指标建模与数据处理（Week 2）

**目标**：从“数据”走向“信息”

#### 核心指标（MVP）
- Daily / Weekly commit count
- Lines added / deleted（Code Churn）
- Active contributors 数量

#### 数据建模
- Commit
- Author
- TimeSeries

#### 阶段完成标准
- 可输出结构化指标数据（JSON）
- 能支撑后续可视化

---

### 阶段 3：基础可视化 Dashboard（Week 3）

**目标**：让数据“看得懂”

#### 可视化模块
- Commit 活跃度热力图
- 代码变更趋势折线图
- 贡献者分布图

#### 产品要求
- 清晰布局
- 时间范围可选择
- 基本交互（hover / tooltip）

#### 阶段完成标准
- 一个可完整展示项目活动的 Dashboard 页面

---

### 阶段 4：项目健康度评分系统（Week 4）【核心差异点】

**目标**：从展示数据 → 给出判断

#### Health Score 设计（示例）
- Commit frequency（近期活跃度）
- Contributor diversity（Bus factor）
- Code churn stability（波动性）

#### 展示形式
- 健康度评分仪表盘
- 子指标拆解视图

#### 阶段完成标准
- 每个项目生成 0–100 的健康评分
- 能解释评分来源

---

### 阶段 5：对比分析与自动解释（Week 5）【进阶加分】

**目标**：体现分析与决策能力

#### 功能
- 不同时间段对比（近 30 天 vs 90 天）
- 不同项目横向对比
- 自动生成分析文本（规则驱动）

#### 示例解释文本
> “Project activity decreased by 28% in the last 30 days, while code churn increased, indicating potential instability.”

#### 阶段完成标准
- Dashboard 不再只是“图”，而是“结论 + 证据”

---

## 五、非功能性设计（外企非常看重）

### 5.1 工程取舍说明
- 为什么选择非实时数据
- 如何应对大仓库性能问题
- API 限流的处理策略

### 5.2 可扩展性设计
- 抽象数据源接口（GitHub / GitLab / Azure DevOps）
- 支持私有仓库的可能方案

---

## 六、项目完成标准（Definition of Done）

- 项目可在本地一键运行
- 有可演示的 Dashboard 页面
- README 清晰描述设计思路与亮点
- 项目差异点明确、可讲故事

---

## 七、预期简历价值

> 能完整体现：
- 工程能力
- 数据分析能力
- 可视化表达
- 产品与业务理解

**适合用于**：
- 技术实习
- 咨询技术岗
- 外企工程岗

---

## 八、后续可扩展方向（非必须）

- PR / Issue 分析
- 团队协作网络图
- 项目风险预警

---

> 本项目强调：**清晰思路 > 技术堆叠**，每个阶段都可独立展示与讲解。

