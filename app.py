import altair as alt
import streamlit as st
import pandas as pd
from datetime import datetime


from github_loader import GitHubLoader
from db_manager import DBManager
from score_calculator import calculate_health_score

# === 初始化 ===
# 设置页面标题
st.title("Project Activity Dashboard")

# 安全检查
st.subheader("Security Check")
try:
    # st.secrets 就像一个字典，专门读取 secrets.toml 里的内容
    token = st.secrets["GITHUB_TOKEN"]
except:
    st.error("Please config your Token in .streamlit/secrets.toml !")
    st.stop()

# 初始化加载器
loader = GitHubLoader(token)

db = DBManager()

# === 用户输入 ===
repo_name = st.text_input("Enter Repository Name", "pandas-dev/pandas")

if st.button("Analyze Project"):
    with st.spinner(f"Fetching data from {repo_name} ..."):
        try:
            # 检查数据库里的最新时间
            last_date = db.get_latest_commit_date(repo_name)

            # 如果有时间，就只拉取那个时间之后的。
            # 如果没时间，就拉取默认数量。
            if last_date:
                st.info(f"Local data found. Last update: {last_date}. Fetching new commits...")
                new_commits_raw = loader.fetch_commits(repo_name, limit=500, since_date=last_date)
            else:
                st.info("First time analysis. Fetching history...")
                new_commits_raw = loader.fetch_commits(repo_name, limit=500)

            # 数据清洗
            cleaned_data = []
            for c in new_commits_raw:
                cleaned_data.append({
                    "sha": c['sha'],    # 保持原始长 hash
                    "author": c['commit']['author']['name'],
                    "date": c['commit']['author']['date'],
                    "message": c['commit']['message'],
                    # 注意：普通的 commits 列表接口没有 stats (additions/deletions)
                    # 要获取详细 stats 需要单条查询，这很慢
                    # MVP 阶段我们先填 0, 或者只用 commit count
                    "additions": 0, 
                    "deletions": 0
                })

            # 存入数据库
            if cleaned_data:
                db.save_commits(repo_name, cleaned_data)

            # 从数据库读取全量数据
            all_commits = db.get_all_commits(repo_name)
            df = pd.DataFrame(all_commits)

            # 转换时间格式
            df['date'] = pd.to_datetime(df['date'])

            st.success(f"Analysis Ready! Total Commits in DA: {len(df)} ")
            st.dataframe(df)

            # === 数据处理 ===

            # 确保 date 列是 datetime 类型
            df['date'] = pd.to_datetime(df['date'], utc=True)

            # 设置 date 为索引，方便后续按时间切片
            df.set_index('date', inplace=True)

            # 排序（从旧到新）
            df.sort_index(inplace=True)

            # === 绘制图表 ===

            st.divider()    # 分割线
            st.subheader("Project Overview")

            # 创建 3 列布局
            col1, col2, col3 = st.columns(3)

            # 指标 1: 总提交书
            total_commits = len(df)
            col1.metric("Total Commits", total_commits)

            # 指标 2: 活跃贡献者人数
            unique_authors = df['author'].nunique()
            col2.metric("Contributors", unique_authors)

            # 指标 3: 项目跨度（天）
            if not df.empty:
                duration = (df.index.max() - df.index.min()).days
                col3.metric("Active Days", f"{duration} days")

            st.subheader("Activity Trend (Weekly)")

            # Pandas 魔法：resample('W') = 按周聚合
            # count() = 计算这一周有多少行
            weekly_commits = df.resample('W')['sha'].count()

            # 画折线图
            st.line_chart(weekly_commits)

            # 统计周一到周日的提交分布
            st.subheader("Work Rhythm (Day of Week)")

            # 1. 提取星期几
            # df.index 是 datetime 类型，直接有 day_name() 方法
            day_counts = df.index.day_name().value_counts()

            # 【Debug 探针 1】打印原始索引看看长什么样
            st.write("Debug - Raw Index:", day_counts.index.tolist())

            # 排序
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            # reindex 会按照我们制定的列表顺序重新排列数据
            day_counts = day_counts.reindex(days_order, fill_value=0)

            chart_data = day_counts.reset_index()
            chart_data.columns = ['Day', 'Commits']

            # 构建一个绝对听话的图表
            c = alt.Chart(chart_data).mark_bar().encode(
                # sort=days_order: 强制按照我们要的顺序排 X 轴
                x=alt.X('Day', sort=days_order),
                y='Commits',
                tooltip=['Day', 'Commits']
            )

            # 3. 画图
            st.altair_chart(c, width='stretch')
            
            # 4. 自动洞察 (Bonus)
            weekend_commits = day_counts['Saturday'] + day_counts['Sunday']
            total = day_counts.sum()
            weekend_ratio = weekend_commits / total
            
            if weekend_ratio > 0.3:
                st.info(f"High Weekend Activity ({weekend_ratio:.1%}). Looks like a hobby/side project.")
            else:
                st.success(f"Professional Workflow. Most commits happen on weekdays.")
            
            # 自动解释 (简单的规则引擎)
            last_4_weeks = weekly_commits.tail(4).mean()
            if last_4_weeks > weekly_commits.mean():
                st.success(f"Trending Up! Average {last_4_weeks:.1f} commits/week recently.")
            else:
                st.info(f"Cooling Down. Average {last_4_weeks:.1f} commits/week recently.")
               
            st.subheader("Top Contributors")

            # 1. 准备数据
            author_counts = df['author'].value_counts().head(10)
            author_df = author_counts.reset_index()
            author_df.columns = ['Author', 'Commits']
            
            # 2. 使用 Altair 画图
            c = alt.Chart(author_df).mark_bar().encode(
                # x 轴：显示 Author 名字
                # sort='-y': 这是一个神奇的指令。意思是 "按 Y 轴的值倒序排列 X 轴"
                x=alt.X('Author', sort='-y'), 
                y='Commits',
                # 顺便加个颜色，让图表不那么单调
                color=alt.Color('Commits', legend=None),
                tooltip=['Author', 'Commits']
            )
            
            st.altair_chart(c, use_container_width=True)

            st.divider()

            # 计算分数
            score, reasons = calculate_health_score(df)

            # 使用 Streamlit 的列布局展示分数
            score_col, reason_col = st.columns([1, 2])

            with score_col:
                color = "green" if score >= 80 else "orange" if score >= 50 else "red"
                st.markdown(f"""
                    <div style="text-align: center;"
                        <h3 style="margin:0;">Project Health</h3>
                        <h1 style="color: {color}; font-size: 72px; margin:0;">{score}</h1>)
                    </div>
                    """, unsafe_allow_html=True)
                
            with reason_col:
                st.subheader("Analysis Report")
                for reason in reasons:
                    st.write(reason)

            st.divider()

        except Exception as e:
            st.error(f"Error: {e}")
            st.stop() # 停止后续代码执行