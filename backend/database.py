from sqlmodel import SQLModel, create_engine, Session

# 使用 SQLite, 文件名为 database.db
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# echo=True 会打印生成的 SQL 语句，方便调试学习
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    """初始化数据库表结构"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """依赖诸如函数，用于 FastAPI 获取数据库会话"""
    with Session(engine) as session:
        yield session