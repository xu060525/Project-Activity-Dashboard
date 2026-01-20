import sqlite3
import os

class DBManager:
    def __init__(self, db_path="data/project_data.db"):
        # 确保 data 文件夹存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 连接数据库
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """初始化表结构"""
        cursor = self.conn.cursor()

        # 创建 commits 表
        # UNIQUE(sha) 保证同一个 commit 不会被重复存储
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commits (
                sha TEXT PRIMATY KEY, 
                repo_name TEXT, 
                author TEXT, 
                date TEXT, 
                message TEXT, 
                additions INTEGER, 
                deletions INTEGER
            )
        ''')
        self.conn.commit()

    def save_commits(self, repo_name, commits_data):
        """
        批量保存 commits
        
        :param commits_data: 兴起后的字典列表
        """
        cursor = self.conn.cursor()
        count = 0
        for c in commits_data:
            try:
                # INSERT OR IGNORE: 如果 sha 已存在，就跳过，不报错
                cursor.execute('''
                    INSERT OR IGNORE INTO commits
                    (sha, repo_name, author, date, message, additions, deletions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    c['sha'], repo_name, c['author'], c['date'], 
                    c['message'], c.get('additions', 0), c.get('deletions', 0)
                ))
                if cursor.rowcount > 0:
                    count += 1
                
            except Exception as e:
                print(f"Error saving commit {c['sha']}: {e}")

        self.conn.commit()
        print(f"Saved {count} new commits to DB.")

    def get_latest_commit_date(self, repo_name):
        """获取该仓库在数据库里最新一条 commit 的时间"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date FROM commits
            WHERE repo_name = ?
            ORDER BY date DESC
            LIMIT 1
        ''', (repo_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_all_commits(self, repo_name):
        """读取该仓库所有本地数据"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT sha, author, date, message, additions, deletions
            FROM commits
            WHERE repo_name = ?
            ORDER BY date DESC
        ''', (repo_name,))

        # 转成字典列表返回
        cols = ['sha', 'author', 'date', 'message', 'additions', 'deletions']
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    
    def close(self):
        self.conn.close()