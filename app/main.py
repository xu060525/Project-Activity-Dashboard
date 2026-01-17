from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI() # 创建一个 API 应用实例

# 定义输入数据格式
class Item(BaseModel):
    name: str
    description: str = None

# 接收 URL 参数
@app.get("/items/{item_id}")   # 有人访问 / 路径，用GET方法时
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q} # FastAPI 自动变成 JSON 响应

# 使用 POST 接收 JSON 数据
@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "description": item.description}