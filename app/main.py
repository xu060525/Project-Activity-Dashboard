from fastapi import FastAPI

app = FastAPI() # 创建一个 API 应用实例

@app.get("/")   # 有人访问 / 路径，用GET方法时
def read_root():
    return {"message": "Project Activity Dashboard API is running"} # FastAPI 自动变成 JSON 响应