import os
import json
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块
from datetime import datetime, timedelta

class LLM:
    def __init__(self):
        # 创建一个OpenAI客户端实例
        self.client = OpenAI()
        # 从TXT文件加载提示信息
        with open("prompts/report_prompt.txt", "r", encoding='utf-8') as file:
            self.system_prompt = file.read()
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("logs/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False, date_range=None):
        # 处理日期范围
        if date_range is None:
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            date_range = f"{yesterday}至{today}"
        
        # 提取项目名称
        project_name = "未知项目"
        for line in markdown_content.split('\n'):
            if line.startswith('# ') or line.startswith('# Daily Progress for '):
                parts = line.replace('# Daily Progress for ', '').split(' (')
                if len(parts) > 0:
                    project_name = parts[0]
                break
        
        # 构建更详细的用户提示，包含项目名称和日期范围
        user_prompt = f"""以下是"{project_name}"项目在{date_range}期间的活动记录。请根据这些信息生成一份结构化的进展报告：

{markdown_content}"""

        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info(f"Starting report generation for {project_name} using GPT model.")
        
        try:
            # 调用OpenAI GPT模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 指定使用的模型版本
                messages=messages,
                temperature=0.3,  # 降低温度以提高输出的一致性和确定性
                max_tokens=2000   # 设置最大token数量以获得完整报告
            )
            LOG.debug("GPT response received successfully")
            # 返回模型生成的内容
            return response.choices[0].message.content
        except Exception as e:
            # 如果在请求过程中出现异常，记录错误并抛出
            LOG.error("An error occurred while generating the report: {}", e)
            raise
