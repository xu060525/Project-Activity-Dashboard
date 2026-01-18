from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

# Project 模型（对应 project 表）
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner: str
    name: str
    url: str
    description: Optional[str] = None
    stars: int = 0
    health_score: int = 0   # 核心指标
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))

# Commit 模型（对应 commit 表）
class Commit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sha: str = Field(index=True)    # 加索引，方便查询
    project_id: int = Field(foreign_key="project.id")
    anthor_name: str
    author_email: Optional[str]
    message: str
    additions: int  # 增加行数
    additions: int  # 删除行数
    committed_at: datetime