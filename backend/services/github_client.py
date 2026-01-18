import os
import httpx
import logging
from dotenv import load_dotenv

# 获取一个专属 logger
logger = logging.getLogger(__name__)

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
        
    async def fetch_commits_graphql(self, owner: str, repo: str, limit: int=10):
        """
        使用 GraphQL 获取 Commit 及其详细统计数据（解决 N+1 问题）
        """
        url = "https://api.github.com/graphql"

        # GraphQL 查询语句
        # 意思：在 repository(owner, name) 里，找 defaultBranchRef
        # target(Commit) -> history(first: limil) -> edges -> node
        # 拿到: oid (sha), message, committedDate, author, 
        # 以及最重要的 -> additions, deletions
        query = """
        query($owner: String!, $repo: String!, $limit: Int!) {
          repository(owner: $owner, name: $repo) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: $limit) {
                    edges {
                      node {
                        oid
                        message
                        committedDate
                        additions
                        deletions
                        author {
                          name
                          email
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            "owner": owner,
            "repo": repo, 
            "limit": limit,
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:

            # 使用 logger 记录
            logger.info(f"Fetching commits for {owner}/{repo} via GraphQL")

            response = await client.post(
                url, 
                headers=self.headers,
                json={"query": query, "variables": variables}
            )

            if response.status_code != 200:
                # 记录错误，这对排查问题至关重要
                logger.error(f"GirHub API Error: {response.text}")
                response.raise_for_status()
                
            data = response.json()

            # 调试信息可以使用 debug 级别
            # 只有当 logging level 设置为 DEBUG 时才会显示，平时不烦你
            logger.debug(f"GraphQL Response keys: {data.keys()}") 
        
            # 解析嵌套的 JSON 结构 (GraphQL 的数据层及很深)
            try: 
                history = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]["edges"]
                commits = [item["node"] for item in history]
                return commits
            except (KeyError, TypeError):
                # 如果仓库是空的或者没有默认分支，可能报错
                return []