import os
from datetime import date, timedelta
from logger import LOG
from hacker_news_client import HackerNewsClient
from llm import LLM

class HackerNewsReportGenerator:
    def __init__(self, llm):
        self.llm = llm  # 初始化时接受一个LLM实例
        self.client = HackerNewsClient()  # 创建HackerNewsClient实例
    
    def generate_daily_report(self):
        """生成每日Hacker News趋势报告"""
        LOG.info("开始生成Hacker News每日趋势报告")
        
        # 获取今日热门文章
        top_stories = self.client.fetch_hackernews_top_stories()
        
        # 导出原始数据
        markdown_file_path = self.client.export_daily_trends()
        
        # 生成趋势洞察提示词
        template, stories_text = self.client.generate_trends_insight(top_stories)
        
        # 调用LLM生成分析报告
        prompt = f"{template}\n\n今日Hacker News热门文章:\n{stories_text}"
        report = self.llm.generate_daily_report(prompt)
        
        # 保存报告
        report_file_path = os.path.splitext(markdown_file_path)[0] + "_analysis.md"
        with open(report_file_path, 'w', encoding='utf-8') as report_file:
            report_file.write(report)
        
        LOG.info(f"Hacker News趋势分析报告已保存到 {report_file_path}")
        
        return report, report_file_path
    
    def generate_report_by_date_range(self, days):
        """生成指定日期范围的Hacker News趋势报告"""
        LOG.info(f"开始生成Hacker News {days}天趋势报告")
        
        # 获取热门文章
        top_stories = self.client.fetch_hackernews_top_stories()
        
        # 导出原始数据
        markdown_file_path = self.client.export_trends_by_date_range(days)
        
        # 生成趋势洞察提示词
        template, stories_text = self.client.generate_trends_insight(top_stories)
        
        # 调用LLM生成分析报告
        today = date.today()
        since = today - timedelta(days=days)
        prompt = f"{template}"
        report = self.llm.generate_daily_report(markdown_content=f"{since}至{today}的Hacker News热门文章:\n{stories_text}",dry_run=False,system_prompt=prompt)
        
        # 保存报告
        report_file_path = os.path.splitext(markdown_file_path)[0] + "_analysis.md"
        with open(report_file_path, 'w', encoding='utf-8') as report_file:
            report_file.write(report)
        
        LOG.info(f"Hacker News趋势分析报告已保存到 {report_file_path}")
        
        return report, report_file_path

# 测试代码
if __name__ == "__main__":
    from llm import LLM
    
    llm = LLM()  # 创建LLM实例
    report_generator = HackerNewsReportGenerator(llm)  # 创建报告生成器
    
    # 生成今日报告
    report, file_path = report_generator.generate_daily_report()
    print(f"报告已生成: {file_path}")
    
    # 生成过去7天的报告
    report, file_path = report_generator.generate_report_by_date_range(7)
    print(f"7天趋势报告已生成: {file_path}") 