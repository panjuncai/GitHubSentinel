# src/llm.py

import os
from openai import OpenAI

class LLM:
    def __init__(self):
        self.client = OpenAI()

    def generate_daily_report(self, markdown_content, dry_run=False):
        system_message = """你是一位专业的技术文档编辑，擅长分析GitHub项目更新并生成结构化报告。
请分析提供的项目更新内容，生成一份简洁清晰的日报。
报告应包含以下几个部分：
1. 新增功能：按照重要性排序
2. 主要改进：包括性能优化、代码重构等
3. 修复问题：描述已解决的bug和问题
4. 进行中的工作：如果有相关信息，请包含正在进行的工作

每个部分应使用适当的Markdown格式，保持专业、简洁的技术语言风格。确保报告结构清晰，方便技术团队快速了解关键更新。"""

        user_prompt = f"以下是项目的最新进展，请帮我生成一份结构化日报：\n\n{markdown_content}"
        
        if dry_run:
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(f"System: {system_message}\n\nUser: {user_prompt}")
            return "DRY RUN"

        print("Before call GPT")
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]
        )
        print("After call GPT")
        print(response)
        return response.choices[0].message.content
