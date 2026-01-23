import openai
import streamlit as st

class AIAnalyst:
    def __init__(self, api_key):
        # 初始化客户端
        self.client = openai.Client(
            api_key=api_key, 
            base_url="https://api.siliconflow.cn/v1"
        )

    def generate_assessment(self, repo_name, health_score, bus_factor_risk, intent_dist, activity_trend):
        """
        生成项目诊断报告

        :param repo_name: 仓库名
        :param health_score: 健康分
        :param bus_factor_risk: 是否有单点风险
        :param intent_dist: 分类字典
        """

        # 构建 Prompt
        system_prompt = """
        你是一位经验丰富的技术CTO和开源项目评估专家。
        你的任务是根据提供的数据，对 GitHub 项目的健康度进行犀利、简练的诊断。
        请用 Markdown 格式输出，包含以下部分：
        1. **总体评价**：一句话定性。
        2. **风险分析**：指出潜在隐患。
        3. **行动建议**：如果是维护者或使用者，该怎么做。
        风格要求：专业、客观、直击痛点。不要说废话。
        """

        user_prompt = f"""
        请评估项目：{repo_name}
        
        【核心数据】
        - 健康度评分：{health_score}/100
        - 活跃度趋势：{activity_trend}
        - Bus Factor 风险：{"高危 (High Risk)" if bus_factor_risk else "安全 (Safe)"}
        - 工作重心分布：{intent_dist}
        """

        try:
            # 调用 API
            response = self.client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3", # 确认这个模型名是对的，硅基流动可能是 "deepseek-ai/deepseek-v3"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=True
            )
            
            # 直接返回这个 response 对象
            return response
            
        except Exception as e:
            # 如果出错，为了不让前端崩掉，我们返回一个假的生成器，抛出错误文本
            # 这是一个高级技巧：Yield 一个包含错误信息的对象
            print(f"DEBUG: AI Error: {e}") # 在终端打印详细错误
            raise e