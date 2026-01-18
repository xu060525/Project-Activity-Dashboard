from fastapi import FastAPI

# 初始化 APP
app = FastAPI(
    title="Project Activity Dashboard API",
    description="API service for analyzing GitHub project health",
    version="0.1.0",
)

@app.get('/')
async def root():
    """
    根路由，用于健康检查
    """
    return {"message": "Service is running", "status": "healthy"}

@app.get("/ping")
async def ping():
    return "pong"