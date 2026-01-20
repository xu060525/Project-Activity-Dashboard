import streamlit as st
import pandas as pd
from datetime import datetime

from github_loader import GitHubLoader
from db_manager import DBManager

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

            # 画个简单的趋势图
            st.line_chart(df['date'].value_counts())
               

        except Exception as e:
            st.error(f"Error: {e}")
            st.stop() # 停止后续代码执行