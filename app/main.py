from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI() # 创建一个 API 应用实例

# 定义输入数据格式
class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)  # name 必须有值，并且长度限制
    description: str = Field(None, max_length=500)  # description 可选，最大长度 500
    price: float = Field(..., gt=0)  # price 必须大于 0
    tax: float = None

# 接收 URL 参数
@app.get("/items/{item_id}")   # 有人访问 / 路径，用GET方法时
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q} # FastAPI 自动变成 JSON 响应

# 使用 POST 接收 JSON 数据
@app.post("/items/")
def create_item(item: Item):
    return {"name": item.name, "description": item.description}