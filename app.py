import streamlit as st
import pandas as pd

from github_loader import GitHubLoader

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

# 用户输入
repo_name = st.text_input("Enter Repository Name (e.g., streamlit/streamlit)", "streamlit/streamlit")
fetch_btn = st.button("Fetch Data")

if fetch_btn:
    # 初始化加载器
    loader = GitHubLoader(token)

    with st.spinner(f"Fetching data from {repo_name} ..."):
        try:
            # 这里调用我们写的后端逻辑
            raw_commits = loader.fetch_commits(repo_name, limit=200)
        
        except Exception as e:
            st.error(f"Failed: {e}")
            st.stop() # 停止后续代码执行

    # 展示结果
    if raw_commits:
        st.success(f"Successfully fetched {len(raw_commits)} commits!")

        # 简单的数据清洗，只取我们需要的信息展示
        # 列表推导式 (List Comprehension) - Python 必会技巧
        data = []
        for c in raw_commits:
            data.append({
                "sha": c['sha'][:7],
                "author": c['commit']['author']['date'],
                "date": c['commit']['author']['date'], 
                "message": c['commit']['message'],
                "comments": c['commit']['comment_count'], 
            })

        df = pd.DataFrame(data)

        # 展示表格
        st.dataframe(df)

        # 简单统计
        st.write(f"Unique Authors: {df['author'].nunique()}")

    else:
        st.warning("No commits found or repository does noe exist.")
