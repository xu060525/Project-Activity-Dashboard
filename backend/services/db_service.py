from sqlmodel import Session, select
import logging

from models import Project, Commit
from datetime import datetime

logger = logging.getLogger(__name__)

class DBService:
    def __init__(self, session: Session):
        self.session = session

    def create_or_update_project(self, owner: str, repo: str, url: str) -> Project:
        """
        如果项目存在就更新，不存在就创建 (Upsert 逻辑)
        """
        statement = select(Project).where(Project.owner == owner, Project.name == repo)
        project = self.session.exec(statement).first()

        if not project:
            logger.info(f"Creating new project: {owner}/{repo}")
            project= Project(owner=owner, name=repo, url=url)
            self.session.add(project)
        else:
            # 可以在这里更新 last_updated 字段
            pass

        self.session.commit()
        self.session.refresh(project)
        return project

    def add_commits(self, project_id: int, commits_data: list):
        """
        批量插入 Commits, 自动跳过已存在的 (根据 SHA)
        """
        added_count = 0
        for data in commits_data:
            sha = data['oid']

            # 检查是否已经存在
            # 性能优化点：如果数据量大，这里应该用 Set 集合在内存比对，或者用 SQL 的 WHERE IN
            # MVP 阶段我们先用简单查询
            existing = self.session.exec(
                select(Commit).where(Commit.sha == sha)
            ).first()

            if not existing:
                # 转化成 GraphQL 的格式 -> 数据库模型
                commit = Commit(
                    sha=sha, 
                    project_id=project_id,
                    author_name=data["author"]["name"] or "Unkown", 
                    author_email=data["author"]["email"],
                    message=data["message"], 
                    additions=data["additions"],
                    deletions=data["deletions"], 

                    committed_at=datetime.fromisoformat(data["committedDate"].replace("Z", "+00:00"))
                )
                self.session.add(commit)
                added_count += 1

        self.session.commit()
        logger.info(f"Imported {added_count} new commits for project_id {project_id}")
