from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session
import sys
import logging

from services.github_client import GitHubClient
from services.db_service import DBService
from services.analysis_service import AnalysisService
from database import create_db_and_tables, get_session
from models import Project, Commit

# 创建一个 logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 格式器
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# 1. 输出到控制台 (StreamHandler)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 2. 输出到文件 (FileHandler)
file_handler = logging.FileHandler("app.log", encoding="utf-8") # 文件名叫 app.log
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 生命周期管理器：应用是启动创建表
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# 初始化 APP
app = FastAPI(title="Project Activity Dashboard", lifespan=lifespan)

# 配置 CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],    # 允许前端的地址
    allow_credentials=True,
    allow_methods=["*"],    # 允许所有方法 (GET, POST...)
    allow_headers=["*"], 
)

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

@app.get("/api/analyze/{owner}/{repo}")
async def analyze_project(owner: str, repo: str, db: Session = Depends(get_session)):
    """
    触发一次完整的分析流程：
    1. 拉取 GitHub 数据
    2. 存入数据库
    3. 返回分析结果
    """
    # 初始化服务
    gh_client = GitHubClient()
    db_service = DBService(db)
    analysis_service = AnalysisService(db)

    try:
        # 确保 Project 存在
        project_url = f"https://github.com/{owner}/{repo}"
        project = db_service.create_or_update_project(owner, repo, project_url)

        # 拉取数据
        raw_commits = await gh_client.fetch_commits_graphql(owner, repo, limit=50)

        # 存入数据库
        db_service.add_commits(project.id, raw_commits)

        # 计算分数
        health_score = analysis_service.update_project_health(project.id)

        return {
            "staus": "success",
            "message": f"Analyzed {owner}/{repo}",
            "project_id": project.id,
            "commits_found": len(raw_commits), 
            "health_score": health_score
        }
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # 打印详细堆栈，方便调整时区
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ping")
async def ping():
    return "pong"