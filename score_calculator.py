import numpy as np
import pandas as pd

def calculate_health_score(df):
    """
    根据 commit 历史计算健康度评分 (0-100)
    
    :param df: 包含 datetime 索引的 DataFrame
    :return: 整数分数，解释文本字典
    """
    score = 0
    explanations = []

    if df.empty:
        return 0, ["No data available"]

    # --- 活跃度评分 ---
    last_commit_date = df.index.max()
    now = pd.Timestamp.now(tz=last_commit_date.tz)  # 保持时区一致
    days_since_last = (now - last_commit_date).days

    if days_since_last < 30:
        activity_score = 40
        explanations.append("Very Active: Commits in last 30 days. ")
    elif days_since_last < 90:
        activity_score = 20
        explanations.append("Slowing Down: No commits in last month. ")
    else:
        activity_score = 0
        explanations.append("Inactive: No commits in last 3 months. ")

    score += activity_score

    # --- 社区评分 ---
    unique_authors = df['author'].nunique()
    
    # 计算头号贡献者的占比
    # value_counts(normalize=True) 直接返回百分比 (0.0 - 1.0)
    author_ratios = df['author'].value_counts(normalize=True)
    top_contributor_ratio = author_ratios.iloc[0] if not author_ratios.empty else 0

    if unique_authors >= 10:
        community_score = 30
        explanations.append("Healthy Community: >10 Contributors.")
    elif unique_authors >= 3:
        community_score = 15
        explanations.append("Small Team: <10 Contributors. ")
    else:
        community_score = 5
        explanations.append("Bus Factor Risk: Only 1-2 contributors. ")

    # 惩罚项：看独裁程度
    # 如果一个人干了超过 80% 的活，且团队人数 > 1 (避免把个人项目误判)，扣 10 分
    if top_contributor_ratio > 0.8 and unique_authors > 1:
        community_score = max(0, community_score - 10) # 不扣成负数
        explanations.append(f"HIGH RISK: One developer wrote {top_contributor_ratio:.1%} of code.")

    score += community_score

    # --- 稳定性评分 ---
    project_age_days = (df.index.max() - df.index.min()).days
    if project_age_days > 180:
        stability_score = 30
        explanations.append("Mature Project: >6 months history. ")
    elif project_age_days > 30:
        stability_score = 15
        explanations.append("Young Project: <6 months history.")
    else:
        stability_score = 0
        explanations.appent("Baby Project: Just started. ")

    score += stability_score

    return score, explanations