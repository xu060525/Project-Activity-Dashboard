from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from sqlmodel import Session
import logging

from services.github_client import GitHubClient
from database import create_db_and_tables, get_session
from models import Project, Commit

# 配置日志格式
logging.basicConfig(
    level=logging.INFO, # 默认级别：只显示INFO及以上
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("api")   # 给你的应用起个名字

# 生命周期管理器：应用是启动创建表
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# 初始化 APP
app = FastAPI(title="Project Activity Dashboard", lifespan=lifespan)

@app.get('/')
async def root():
    """
    根路由，用于健康检查
    """
    return {"message": "Service is running"}

@app.get("/api/commits/{owner}/{repo}")
async def get_commits(owner: str, repo: str):
    """
    获取指定仓库的提交历史
    """
    client = GitHubClient()
    try:
        # 使用 GraphQL 获取数据
        # await 是关键，因为 fetch_commits 是异步函数
        raw_commits = await client.fetch_commits_graphql(owner, repo, limit=10)
        
        # 数据清洗：只返回我们需要展示的字段 (Data Transfer Object 思想)
        # 我们暂时只取前 5 条看看效果
        #  (模拟) 保存到数据库的逻辑演示
        # 暂时我们只返回数据，明天再做真正的入库
        
        # 格式化一下返回给前端
        result = []
        for c in raw_commits:
            result.append({
                "sha": c["oid"],
                "message": c["message"],
                "author": c["author"]["name"],
                "additions": c["additions"], # 看！拿到这个字段了
                "deletions": c["deletions"]  # 还有这个
            })
            
        return result

    
    except Exception as e:
        import traceback
        traceback.print_exc()   # 打印报错详情到后台
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ping")
async def ping():
    return "pong"