# 📁 Project Activity Analytics Dashboard (Local-First Edition)
> **项目架构与开发规划书 v2.0**

## 1. 项目愿景 (Vision)
打造一款**“本地优先、开箱即用”**的 GitHub 项目健康度分析工具。它结合了桌面软件的数据隐私安全与 Web 界面的现代交互体验，旨在帮助技术管理者快速评估开源项目或内部代码库的维护风险。

## 2. 核心差异点 (Unique Selling Points)
1.  **风险量化 (Risk Quantification)**: 不止展示 commit 数量，而是通过 **Bus Factor (巴士系数)** 和 **Code Churn (代码搅动率)** 算出项目的健康评分。
2.  **本地优先架构 (Local-First Architecture)**: 数据存储于用户本地 SQLite，支持离线查看，保护企业代码隐私，且具备**增量缓存**能力。
3.  **极客级交付 (Product Delivery)**: 采用 **CLI + Local Web** 模式，一键启动，自动打开浏览器，提供类似 Jupyter Notebook 的专业工具体验。

## 3. 技术栈 (Tech Stack)
*   **语言**: Python 3.9+
*   **核心框架**: `Streamlit` (UI 层), `Pandas` (数据处理)
*   **数据层**: `SQLite` (本地数据库), `SQLAlchemy` (ORM, 可选)
*   **网络层**: `Requests` (API 调用)
*   **分发**: `Batch Script` / `Shell Script` (启动器)

## 4. 系统架构 (System Architecture)
```mermaid
graph TD
    User((用户)) -->|双击启动| Launcher[启动脚本 (Launcher)]
    Launcher -->|启动| Server[Local Streamlit Server]
    Launcher -->|自动打开| Browser[系统浏览器 (Chrome/Edge)]
    
    subgraph "Python 后台进程"
        Server -->|交互指令| Controller[业务逻辑层]
        Controller -->|读取| Cache[(SQLite 本地库)]
        Controller -->|请求 (仅增量)| GitHub[GitHub API]
    end
    
    Browser -->|渲染页面| Server
```

## 5. 开发路线图 (Roadmap)
*   **Week 1: 数据基石 (Data Foundation)**
    *   搭建 SQLite 架构，实现 GitHub API 的分页拉取与增量更新逻辑。
*   **Week 2: 交互界面 (Interactive UI)**
    *   使用 Streamlit 构建仪表盘，展示基础图表（热力图、趋势图）。
*   **Week 3: 核心算法 (Health Algorithm)**
    *   实现“健康度评分”模型（Bus Factor, Churn Rate）。
*   **Week 4: 产品化封装 (Production)**
    *   编写启动脚本，优化异常处理，编写 README。

---