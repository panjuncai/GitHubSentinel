import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def add_subscription(repo_name):
    """添加新项目到订阅列表"""
    if not repo_name or len(repo_name.strip()) == 0:
        return "请输入有效的项目名称", format_subscriptions(subscription_manager.list_subscriptions()), gr.Dropdown(choices=subscription_manager.list_subscriptions())
    
    try:
        # 验证格式是否为 owner/repo
        if '/' not in repo_name:
            return f"❌ 错误：项目名称格式应为 'owner/repo'", format_subscriptions(subscription_manager.list_subscriptions()), gr.Dropdown(choices=subscription_manager.list_subscriptions())
        
        subscription_manager.add_subscription(repo_name)
        subscriptions = subscription_manager.list_subscriptions()
        LOG.info(f"Added subscription: {repo_name}")
        return f"✅ 成功添加项目：{repo_name}", format_subscriptions(subscriptions), gr.Dropdown(choices=subscriptions, value=repo_name)
    except Exception as e:
        LOG.error(f"Failed to add subscription: {repo_name}. Error: {e}")
        return f"❌ 添加失败：{str(e)}", format_subscriptions(subscription_manager.list_subscriptions()), gr.Dropdown(choices=subscription_manager.list_subscriptions())

def format_subscriptions(subscriptions):
    """将订阅列表格式化为Markdown列表"""
    if not subscriptions or len(subscriptions) == 0:
        return "目前没有订阅的项目"
    
    formatted_text = "### 已订阅项目列表\n\n"
    for idx, sub in enumerate(subscriptions, 1):
        formatted_text += f"{idx}. **{sub}**\n"
    
    return formatted_text

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    try:
        raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
        report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径
        return report, report_file_path  # 返回报告内容和报告文件路径
    except Exception as e:
        LOG.error(f"Failed to export progress: {e}")
        return f"❌ 生成报告失败：{str(e)}", None

# 创建Gradio界面
with gr.Blocks(title="GitHubSentinel") as demo:
    gr.Markdown("# GitHub Sentinel")
    
    # 创建初始订阅列表
    current_subscriptions = subscription_manager.list_subscriptions()
    
    with gr.Tab("订阅管理"):
        with gr.Row():
            with gr.Column(scale=3):
                new_repo_input = gr.Textbox(label="新增项目名称", placeholder="格式：owner/repo，例如：tensorflow/tensorflow", info="输入要添加的GitHub项目")
            with gr.Column(scale=1):
                add_button = gr.Button("添加到订阅列表", variant="primary")
        
        add_result = gr.Markdown()
        subscription_list = gr.Markdown(format_subscriptions(current_subscriptions), label="已订阅列表")
    
    with gr.Tab("生成报告"):
        with gr.Row():
            report_repo = gr.Dropdown(choices=current_subscriptions, label="选择项目", info="选择要生成报告的GitHub项目")
            report_days = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天")
        
        generate_button = gr.Button("生成报告", variant="primary")
        
        with gr.Row():
            report_output = gr.Markdown(label="报告内容")
            report_file = gr.File(label="下载报告")
    
    # 设置添加按钮的点击事件，更新两个标签页的数据    
    add_button.click(
        fn=add_subscription,
        inputs=[new_repo_input],
        outputs=[add_result, subscription_list, report_repo]
    )
    
    # 设置生成报告按钮的点击事件
    generate_button.click(
        fn=export_progress_by_date_range,
        inputs=[report_repo, report_days],
        outputs=[report_output, report_file]
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="127.0.0.1")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))