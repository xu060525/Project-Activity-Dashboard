import streamlit as st
import pandas as pd

# 设置页面标题
st.title("Project Activity Dashboard")
st.write("Day 0 Check: Enviroment is ready!")

# 安全检查
st.subheader("Security Check")
try:
    # st.secrets 就像一个字典，专门读取 secrets.toml 里的内容
    token = st.secrets["GITHUB_TOKEN"]

    # 只显示前四位，后面用星号代替
    masked_token = token[:4] + "*" * (len(token) - 4)

    st.success(f"GitHub Token loaded successfully: {masked_token[:10]} ...")
    st.info("The app can now safely access GitHub API on your behalf.")

except FileNotFoundError:
    st.error("secrets.toml not found!")

except KeyError:
    st.error("GITHUB_TOKEN not defined in secrets.toml")

# 模拟一个简单的数据表
st.subheader("UI Test")
df = pd.DataFrame({
    'Committer': ['Alice', 'Bob', 'Charlie'], 
    'Commits': [10, 20, 30], 
})

st.bar_chart(df.set_index('Committer'))
