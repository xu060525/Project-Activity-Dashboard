import requests
import time

class GitHubLoader:
    BASE_URL = "https://api.github.com"

    def __init__(self, token):
        """
        初始化加载器
        :param token: GitHub Personal Access Token
        """
        self.headers = {
            "Authorization": f"token {token}", 
            "Accept": "application/vnd.github.v3 + json"
        }

    def fetch_commits(self, repo_name, limit=100, since_date=None):
        """
        获取指定仓库的 commit 列表，处理分页
        
        :param repo_name: 例如 'pandas-dev/pandas'
        :param limit: 限制或取得条数 （防止是 Linux 内核，把内存撑爆）
        :param since_date: ISO 8601 格式时间字符串 (e.g. '2026-01-01T00:00:00Z')
        :return: commits 列表
        """
        commits = []
        page = 1
        per_page = 100  # GitHub API 最大允许每页 100 条

        print(f"Start fetching {repo_name} (Since: {since_date})...")

        while len(commits) < limit:
            try: 
                # 构造请求参数
                params = {
                    "per_page": per_page, 
                    "page": page, 
                }
                # 如果传入了时间，加到参数里
                if since_date:
                    params['since'] = since_date
                
                url = f"{self.BASE_URL}/repos/{repo_name}/commits"

                # 发送请求
                response = requests.get(url, headers=self.headers, params=params)

                # 错误处理 (404, 403, etc)
                if response.status_code == 404:
                    # 抛出具体错误，让上层知道仓库名字写错了
                    raise ValueError(f"Repository '{repo_name}' not found. Please check spelling.")
                
                elif response.status_code == 403:
                    raise PermissionError("API Rate Limit exceeded or Token invalid.")
                
                elif response.status_code != 200:
                    raise Exception(f"Error: {response.status_code} - {response.text}")
                
                # 解析数据
                data = response.json()

                # 如果这一页是空的，说明没数据了，退出循环
                if not data:
                    break

                # 加入总列表
                commits.extend(data)
                print(f"  --> Page {page} fetched. Total: {len(commits)}")

                # 翻页
                page += 1

                # 简单的限流保护 (虽然有 Token, 但稍微礼貌一点)
                time.sleep(0.1)

            except Exception as e:
                print(f"Network Error: {e}")
                break

        # 截断到用户限制的数量
        return commits[:limit]