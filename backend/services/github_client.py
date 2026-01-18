import os
import httpx
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

class GitHubClient:
    def __init__(self):
        # 从环境变量获取token
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in .env file")
        
        self.base_url = "https://api.github.com"
        # 统一设置 Headers, 包含认证信息
        self.headers = {
            "Authorization": f"Bearer {self.token}", 
            "Accept": "application/vnd.github.v3+json", 
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def fetch_commits(self, owner: str, repo: str, limit: int = 10):
        """
        异步获取指定仓库的Commits
        
        :param owner: 仓库拥有者
        :param repo: 仓库名
        :param limit: 获取数量限制
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}

        # 使用异步上下文管理器，并开启重定向跟随
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=self.headers, params=params)

            # 如果状态码不是 200, 抛出异常
            response.raise_for_status()
            
            return response.json()
        
    async def fetch_repo_info(self, owner: str, repo: str):
        """
        获取仓库基本信息 (Star 数, Fork 数等)
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()