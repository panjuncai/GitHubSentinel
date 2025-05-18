import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器
from hacker_news_report_generator import HackerNewsReportGenerator  # 导入Hacker News报告生成器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)
hacker_news_report_generator = HackerNewsReportGenerator(llm)  # 创建Hacker News报告生成器实例

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内GitHub项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def generate_hackernews_report(days):
    # 定义一个函数，用于生成指定时间范围内的Hacker News趋势报告
    LOG.info(f"通过Gradio界面生成Hacker News {days}天趋势报告")
    report, report_file_path = hacker_news_report_generator.generate_report_by_date_range(days)
    return report, report_file_path

# 创建Gradio界面
with gr.Blocks(title="GitHubSentinel") as demo:
    gr.Markdown("# GitHub Sentinel")
    
    with gr.Tab("GitHub项目报告"):
        with gr.Row():
            with gr.Column():
                # GitHub报告生成表单
                repo_dropdown = gr.Dropdown(
                    subscription_manager.list_subscriptions(), 
                    label="订阅列表", 
                    info="已订阅GitHub项目"
                )
                github_days_slider = gr.Slider(
                    value=2, 
                    minimum=1, 
                    maximum=7, 
                    step=1, 
                    label="报告周期", 
                    info="生成项目过去一段时间进展，单位：天"
                )
                github_submit_btn = gr.Button("生成GitHub项目报告")
            
            with gr.Column():
                # 输出区域
                github_report_md = gr.Markdown()
                github_report_file = gr.File(label="下载GitHub报告")
    
    with gr.Tab("Hacker News趋势"):
        with gr.Row():
            with gr.Column():
                # Hacker News报告生成表单
                hn_days_slider = gr.Slider(
                    value=1, 
                    minimum=1, 
                    maximum=7, 
                    step=1, 
                    label="报告周期", 
                    info="生成过去一段时间的Hacker News趋势，单位：天"
                )
                hn_submit_btn = gr.Button("生成Hacker News趋势报告")
            
            with gr.Column():
                # 输出区域
                hn_report_md = gr.Markdown()
                hn_report_file = gr.File(label="下载Hacker News报告")
    
    # 设置按钮点击事件
    github_submit_btn.click(
        export_progress_by_date_range,
        inputs=[repo_dropdown, github_days_slider],
        outputs=[github_report_md, github_report_file]
    )
    
    hn_submit_btn.click(
        generate_hackernews_report,
        inputs=[hn_days_slider],
        outputs=[hn_report_md, hn_report_file]
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="127.0.0.1")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))