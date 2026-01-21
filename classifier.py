class CommitClassifier:
    def __init__(self):
        # 定义关键词规则
        # 这种做法在工业界叫 "Heuristic Rule-based Approach"
        self.rules = {
            "Feature": ["feat", "feature", "add", "new", "create", "implement"],
            "Bugfix": ["fix", "bug", "issue", "resolve", "correct", "patch", "hotfix"],
            "Refactor": ["refactor", "clean", "style", "format", "optimize", "improve"],
            "Docs": ["doc", "docs", "readme", "comment", "typo"],
            "Test": ["test", "tests", "coverage", "benchmark"],
            "Build": ["build", "ci", "cd", "workflow", "dep", "dependency"], 
            "Chore": ["chore", "misc", "update", "upgrade", "bump", "dep", "dependency"], 
        }

    def classify(self, message):
        """
        根据 commit message 返回分类标签
        """
        msg_lower = message.lower()
        
        # 优先匹配 Conventional Commits 格式 (例如 "feat: login")
        if ":" in msg_lower:
            prefix = msg_lower.split(":")[0].strip()
            # 检查前缀是否直接命中
            for category, keywords in self.rules.items():
                # 如果前缀就是 feat, fix 等
                if prefix in keywords or prefix == category.lower():
                    return category
        
        # 如果不是标准格式，进行关键词扫描
        for category, keywords in self.rules.items():
            for word in keywords:
                # 简单的单词匹配
                if word in msg_lower:
                    return category
                    
        return "Other" # 没匹配到