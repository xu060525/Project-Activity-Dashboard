from fastapi import FastAPI, HTTPException
from services.github_client import GitHubClient

# 初始化 APP
app = FastAPI(title="Project Activity Dashboard")

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
        # await 是关键，因为 fetch_commits 是异步函数
        commits = await client.fetch_commits(owner, repo, limit=5)
        
        # 数据清洗：只返回我们需要展示的字段 (Data Transfer Object 思想)
        # 我们暂时只取前 5 条看看效果
        cleaned_data = []
        for commit in commits:
            cleaned_data.append({
                "sha": commit["sha"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "message": commit["commit"]["message"]
            })
            
        return cleaned_data
    
    except Exception as e:
        # 如果出错，返回 400 错误
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ping")
async def ping():
    return "pong"