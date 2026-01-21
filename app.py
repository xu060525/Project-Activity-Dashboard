import altair as alt
import streamlit as st
import pandas as pd
import traceback
from datetime import datetime

from github_loader import GitHubLoader
from db_manager import DBManager
from score_calculator import calculate_health_score
from classifier import CommitClassifier
from ai_analyst import AIAnalyst

# === 初始化 ===
st.set_page_config(page_title="Project Activity Dashboard", layout="wide") # 稍微优化一下布局宽屏模式
st.title("Project Activity Dashboard")

# 1. 初始化 Session State (这是解决你问题的核心！)
# 我们用这两个变量来“记住”数据，不管你点什么按钮，数据都在。
if 'data' not in st.session_state:
    st.session_state['data'] = None
if 'current_repo' not in st.session_state:
    st.session_state['current_repo'] = ""

# 安全检查
st.subheader("Security Check")
try:
    token = st.secrets["GITHUB_TOKEN"]
except:
    st.error("Please config your Token in .streamlit/secrets.toml !")
    st.stop()

# 初始化加载器
loader = GitHubLoader(token)
db = DBManager()
classifier = CommitClassifier()

# === 用户输入 ===
# 这里我们只是获取输入，不立即执行
repo_input = st.text_input("Enter Repository Name", "pandas-dev/pandas")

# === 逻辑块 A：获取数据 (Data Fetching) ===
# 只有点击这个按钮时，才去网络请求和读数据库
if st.button("Analyze Project"):
    with st.spinner(f"Fetching data from {repo_input} ..."):
        try:
            # 更新当前分析的仓库名
            st.session_state['current_repo'] = repo_input
            
            # --- 核心数据获取逻辑 (和你原来的一样) ---
            last_date = db.get_latest_commit_date(repo_input)

            if last_date:
                st.info(f"Local data found. Last update: {last_date}. Fetching new commits...")
                new_commits_raw = loader.fetch_commits(repo_input, limit=500, since_date=last_date)
            else:
                st.info("First time analysis. Fetching history...")
                new_commits_raw = loader.fetch_commits(repo_input, limit=500)

            # 数据清洗 & 分类
            cleaned_data = []
            for c in new_commits_raw:
                message = c['commit']['message']
                category = classifier.classify(message)
                cleaned_data.append({
                    "sha": c['sha'],
                    "author": c['commit']['author']['name'],
                    "date": c['commit']['author']['date'],
                    "message": c['commit']['message'],
                    "additions": 0,
                    "deletions": 0,
                    "category": category
                })

            if cleaned_data:
                db.save_commits(repo_input, cleaned_data)

            # 读取全量数据
            all_commits = db.get_all_commits(repo_input)
            df = pd.DataFrame(all_commits)
            
            # --- 【关键修改】 ---
            # 不要在这里直接画图！
            # 而是把处理好的 df 存进 Session State 里
            st.session_state['data'] = df
            
            # 成功后，强制刷新一下页面，让下面的 "逻辑块 B" 立即运行
            st.rerun()

        except Exception as e:
            st.error(f"Error during fetch: {e}")
            traceback.print_exc()


# === 逻辑块 B：展示数据 (Data Visualization) ===
# 只要 Session State 里有数据，这部分代码就会运行。
# 无论你是刚点完 "Analyze"，还是点了 "AI Report"，这里都会执行！
if st.session_state['data'] is not None:
    
    # 从缓存取出数据
    df = st.session_state['data'].copy()
    repo_name = st.session_state['current_repo'] # 使用锁定的仓库名

    try:
        # === 数据预处理 (每次渲染前做一次即可) ===
        # 确保 date 列是 datetime 类型
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], utc=True)
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)

        st.success(f"Analysis Ready for {repo_name}! Total Commits: {len(df)}")
        
        # ---------------- 下面是你原来的画图代码 (缩进调整到这里) ----------------
        
        st.divider()
        st.subheader("Project Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Commits", len(df))
        col2.metric("Contributors", df['author'].nunique())
        if not df.empty:
            duration = (df.index.max() - df.index.min()).days
            col3.metric("Active Days", f"{duration} days")

        st.subheader("Activity Trend (Weekly)")
        weekly_commits = df.resample('W')['sha'].count()
        st.line_chart(weekly_commits)

        # Work Rhythm
        st.subheader("Work Rhythm (Day of Week)")
        day_counts = df.index.day_name().value_counts()
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = day_counts.reindex(days_order, fill_value=0)
        chart_data = day_counts.reset_index()
        chart_data.columns = ['Day', 'Commits']
        
        c = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Day', sort=days_order),
            y='Commits',
            tooltip=['Day', 'Commits']
        )
        st.altair_chart(c, use_container_width=True) # width='stretch' deprecated, use this
        
        # Weekend Ratio
        weekend_commits = day_counts['Saturday'] + day_counts['Sunday']
        total = day_counts.sum()
        weekend_ratio = weekend_commits / total if total > 0 else 0
        if weekend_ratio > 0.3:
            st.info(f"High Weekend Activity ({weekend_ratio:.1%}). Hobby project?")
        else:
            st.success(f"Professional Workflow. Weekday focus.")

        # Top Contributors
        st.subheader("Top Contributors")
        author_counts = df['author'].value_counts().head(10)
        author_df = author_counts.reset_index()
        author_df.columns = ['Author', 'Commits']
        c = alt.Chart(author_df).mark_bar().encode(
            x=alt.X('Author', sort='-y'), 
            y='Commits',
            color=alt.Color('Commits', legend=None),
            tooltip=['Author', 'Commits']
        )
        st.altair_chart(c, use_container_width=True)

        st.divider()

        # Health Score
        score, reasons = calculate_health_score(df)
        score_col, reason_col = st.columns([1, 2])
        with score_col:
            color = "green" if score >= 80 else "orange" if score >= 50 else "red"
            st.markdown(f"""
                <div style="text-align: center;">
                    <h3 style="margin:0;">Project Health</h3>
                    <h1 style="color: {color}; font-size: 72px; margin:0;">{score}</h1>
                </div>
                """, unsafe_allow_html=True)
        with reason_col:
            st.subheader("Analysis Report")
            for reason in reasons:
                st.write(reason)

        st.divider()

        # === AI 部分 ===
        st.subheader("AI Intent Analysis")

        type_counts = df['category'].value_counts()
        intent_dist = type_counts.to_dict()
        is_risky = (len(reasons) > 0 and "Risk" in reasons[-1])

        # 【重点】现在这个按钮在 st.session_state['data'] 的保护下
        # 点击它，页面刷新，但上面的 if st.session_state... 依然成立
        # 所以图表不会消失！
        if st.button("Generate AI Report"):
            try:
                api_key = st.secrets["DEEPSEEK_API_KEY"]
                analyst = AIAnalyst(api_key)
                report_box = st.empty()
                full_response = ""

                
                with st.spinner("AI is thinking..."):
                    stream = analyst.generate_assessment(
                        repo_name=repo_name, 
                        health_score=score, 
                        bus_factor_risk=is_risky, 
                        intent_dist=intent_dist
                    )



                    
                    # 【调试关键】先检查 stream 是不是字符串（如果是，说明 analyst 内部报错返回了 str）
                    if isinstance(stream, str):
                        st.error(stream)
                        st.stop()


                    # 正常的流式处理
                    for chunk in stream:

                        # 增加一层保护：检查 chunk 是否有效
                        if chunk and chunk.choices:
                            delta = chunk.choices[0].delta
                            # 有些 SDK 版本 delta.content 可能是 None
                            if delta.content:
                                full_response += delta.content
                                report_box.markdown(full_response + "▌")
                                
                    report_box.markdown(full_response)

   
            except KeyError:
                st.error("Missing DEEPSEEK_API_KEY in secrets.toml")
            except Exception as e:
                st.error(f"AI Error: {e}")

        # Pie Chart
        type_df = type_counts.reset_index()
        type_df.columns = ['Category', 'Count']
        base = alt.Chart(type_df).encode(theta=alt.Theta("Count", stack=True))
        pie = base.mark_arc(outerRadius=120).encode(
            color=alt.Color("Category"),
            order=alt.Order("Count", sort="descending"), 
            tooltip=["Category", "Count"]
        )
        st.altair_chart(pie, use_container_width=True)

        # Unclassified Ratio logic...
        other_count = type_df[type_df['Category'] == 'Other']['Count'].sum()
        total_count = type_df['Count'].sum()
        ratio = other_count / total_count if total_count > 0 else 0
        if ratio > 0.3:
            st.warning(f"Unclassified Ratio: {ratio:.1%}. Messy messages.")
        else:
            st.caption(f"Data Quality is good. Unclassified: {ratio:.1%}")

    except Exception as e:
        st.error(f"Visualization Error: {e}")
        traceback.print_exc()