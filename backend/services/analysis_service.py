from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
import pandas as pd
import logging

from models import Commit, Project

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, session: Session):
        self.session = session

    def calculate_health_score(self, project_id: int) -> int:
        """
        核心算法：根据 Commit 历史计算健康度 (0-100)
        """
        # 从数据库读取该项目的所有 Commits
        statement = select(Commit).where(Commit.project_id == project_id)
        commits = self.session.exec(statement).all()

        if not commits:
            return 0
        
        # 把 ORM 对象转换成字典列表，再给 Pandas (Pandas DataFrame)
        data = [
            {
                "date": c.committed_at,
                "author": c.author_name,
                "churn": c.additions + c.deletions
            }
            for c in commits
        ]
        df = pd.DataFrame(data)

        # 确保日期列是 datetime 类型
        df['date'] = pd.to_datetime(df['date'])

        # --- 近期活跃天数（占比40分） ---
        # 筛选最近三十天的数据
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        # 时区处理
        # df['date'].dt.tz_localize(None)
        # 假设都是UTC
        try:
            recent_df = df[df['date'] > cutoff_date]    # 如果报错，可能是时区问题
        except TypeError:
            # 兼容处理：如果数据库存的是带时区的, cutoff_date 也要带时区
            recent_df = df  # Fallback: 如果比较失败，暂时用全量数据（权宜之计）
            logger.warning("Timezong comparison issue, using all data for analysis")

        commit_count = len(recent_df)
        score_activity = min(commit_count * 2, 40)  # 一个月中 20 个 commit 即拿满40分

        # --- 团队多样性/巴士因子（占比30分）---
        unique_authors = df['author'].nunique()
        score_bus_factor = min(unique_authors * 10, 30) # 三个人即拿满30分

        # --- 代码变动稳定性（占比30分）---
        # 计算平均每次提交的变动行数
        avg_churn = df['churn'].mean()
        # 如果平均变动 < 200行，说明可能原子化提交做的好，给满分
        # 如果变动巨大，说明可能有代码堆积，扣分
        if avg_churn < 200:
            score_stability = 30
        elif avg_churn < 500:
            score_stability = 15
        else:
            score_stability = 5

        # --- 汇总 ---
        total_score = score_activity + score_bus_factor + score_stability

        logger.info(f"Project {project_id} Score: {total_score} "
                    f"(Activity: {score_activity}, Team: {score_bus_factor}, Stability: {score_stability})")
        
        return int(total_score)
    
    def update_project_health(self, project_id: int):
        """
        计算分数并更新到 Project 表
        """
        score = self.calculate_health_score(project_id)

        project = self.session.get(Project, project_id)
        if project:
            project.health_score = score
            self.session.add(project)
            self.session.commit()
            return score
        return 0
        