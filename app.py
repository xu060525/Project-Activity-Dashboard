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
    
    # 使用副本，防止修改原始数据
    df = st.session_state['data'].copy()
    repo_name = st.session_state['current_repo']

    try:
        # === 数据预处理 ===
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], utc=True)
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)

        st.success(f"Analysis Ready for {repo_name}! Total Commits: {len(df)}")
        
        # === Day 3 新增: 使用 Tabs 组织布局 ===
        tab_overview, tab_deep_dive, tab_intent = st.tabs(["Overview", "Deep Dive", "Intent Analysis"])
        
        # 计算一些通用指标 (复用)
        total_commits = len(df)
        contributors = df['author'].nunique()
        duration = (df.index.max() - df.index.min()).days if not df.empty else 0
        score, reasons = calculate_health_score(df)
        
        # --- Tab 1: Overview (总览) ---
        with tab_overview:
            # 1. 核心指标卡片
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Commits", total_commits)
            col2.metric("Contributors", contributors)
            col3.metric("Active Days", f"{duration} days")
            
            st.divider()
            
            # 2. 健康度评分 (左) + AI 报告 (右)
            col_score, col_ai = st.columns([1, 2])
            
            with col_score:
                st.subheader("Health Score")
                color = "green" if score >= 80 else "orange" if score >= 50 else "red"
                st.markdown(f"""
                    <div style="text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h1 style="color: {color}; font-size: 80px; margin:0;">{score}</h1>
                        <p>Out of 100</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # 显示简单的扣分原因
                with st.expander("View Score Details"):
                    for reason in reasons:
                        st.write(reason)

            with col_ai:
                st.subheader("AI CTO Diagnosis")
                
                # 准备 AI 数据
                type_counts = df['category'].value_counts()
                intent_dist = type_counts.to_dict()
                is_risky = (len(reasons) > 0 and "Risk" in reasons[-1])
                
                # 计算趋势
                weekly_commits = df.resample('W')['sha'].count()
                if len(weekly_commits) >= 4:
                    recent_avg = weekly_commits.tail(4).mean()
                    total_avg = weekly_commits.mean()
                    trend = "Rising" if recent_avg > total_avg * 1.2 else "Falling" if recent_avg < total_avg * 0.5 else "Stable"
                else:
                    trend = "Unknown"

                # 缓存逻辑 (Day 2 作业成果)
                if 'ai_reports' not in st.session_state:
                    st.session_state['ai_reports'] = {}
                current_report = st.session_state['ai_reports'].get(repo_name, "")
                
                if current_report:
                    st.info(current_report)
                    if st.button("Regenerate Diagnosis", key="regen_btn"):
                        st.session_state['ai_reports'][repo_name] = ""
                        st.rerun()
                else:
                    if st.button("Generate AI Report", key="gen_btn"):
                        try:
                            api_key = st.secrets["DEEPSEEK_API_KEY"]
                            analyst = AIAnalyst(api_key)
                            with st.spinner("AI is analyzing..."):
                                stream = analyst.generate_assessment(repo_name, score, is_risky, intent_dist, trend)
                                
                                # 非流式处理 (如果 ai_analyst 改了的话) 或 流式处理
                                # 这里假设你用的是 Day 2 的流式代码
                                report_box = st.empty()
                                full_resp = ""
                                if isinstance(stream, str):
                                    st.error(stream)
                                else:
                                    for chunk in stream:
                                        if chunk.choices and chunk.choices[0].delta.content:
                                            full_resp += chunk.choices[0].delta.content
                                            report_box.markdown(full_resp + "▌")
                                    
                                    report_box.markdown(full_resp)
                                    st.session_state['ai_reports'][repo_name] = full_resp
                        except Exception as e:
                            st.error(f"AI Error: {e}")

        # --- Tab 2: Deep Dive (深度分析) ---
        with tab_deep_dive:
            st.subheader("Commit Activity")
            st.line_chart(weekly_commits)
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.subheader("Work Rhythm")
                day_counts = df.index.day_name().value_counts()
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_counts = day_counts.reindex(days_order, fill_value=0).reset_index()
                day_counts.columns = ['Day', 'Commits']
                
                c = alt.Chart(day_counts).mark_bar().encode(
                    x=alt.X('Day', sort=days_order), y='Commits', tooltip=['Day', 'Commits']
                )
                st.altair_chart(c, use_container_width=True)
                
            with col_d2:
                st.subheader("Top Contributors")
                author_counts = df['author'].value_counts().head(10).reset_index()
                author_counts.columns = ['Author', 'Commits']
                
                c2 = alt.Chart(author_counts).mark_bar().encode(
                    x=alt.X('Author', sort='-y'), y='Commits', color=alt.Color('Commits', legend=None)
                )
                st.altair_chart(c2, use_container_width=True)

        # --- Tab 3: Intent Analysis (意图分析) ---
        with tab_intent:
            col_i1, col_i2 = st.columns([2, 1])
            
            with col_i1:
                st.subheader("Category Distribution")
                type_df = type_counts.reset_index()
                type_df.columns = ['Category', 'Count']
                
                base = alt.Chart(type_df).encode(theta=alt.Theta("Count", stack=True))
                pie = base.mark_arc(outerRadius=120).encode(
                    color=alt.Color("Category"),
                    order=alt.Order("Count", sort="descending"),
                    tooltip=["Category", "Count"]
                )
                st.altair_chart(pie, use_container_width=True)
                
            with col_i2:
                st.subheader("Data Quality")
                other_count = type_df[type_df['Category'] == 'Other']['Count'].sum()
                ratio = other_count / total_commits if total_commits > 0 else 0
                st.metric("Unclassified Ratio", f"{ratio:.1%}")
                
                if ratio > 0.3:
                    st.warning("High unclassified ratio. Consider updating classification rules.")
                else:
                    st.success("Good data quality.")

    except Exception as e:
        st.error(f"Visualization Error: {e}")
        traceback.print_exc()