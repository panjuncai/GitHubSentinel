# GitHub Sentinel

<p align="center">
    <br> <a href="README-EN.md">English</a> | 中文
</p>

GitHub Sentinel 是一个开源的工具 AI 代理，专为开发人员和项目经理设计。它会定期（每日/每周）自动从订阅的 GitHub 仓库中检索和汇总更新。主要功能包括订阅管理、更新检索、通知系统和报告生成。

## 功能
- 订阅管理：添加、删除和查看订阅的仓库
- 更新检索：获取仓库的最新提交、问题和拉取请求
- 通知系统：通过邮件或Slack发送更新通知
- 报告生成：使用LLM生成结构化的项目进展报告
- Web界面：直观的订阅管理和报告生成界面

## 更新日志

### 最新更新
- **Web界面升级**：
  - 添加了项目订阅管理功能，支持直接在界面中添加监控项目
  - 改进为标签页布局，分为"订阅管理"和"生成报告"两个功能区
  - 订阅列表使用格式化列表展示，更加直观
  - 添加新项目后，生成报告标签页的项目选择会自动更新
- **LLM提示词优化**：
  - 使用System role架构提升报告质量和稳定性
  - 增强报告结构，添加"进行中的工作"部分
  - 改进了报告格式，分类更加清晰
  - 优化了温度和输出控制，提高生成内容的一致性

## 快速开始

### 1. 安装依赖

首先，安装所需的依赖项：

```sh
pip install -r requirements.txt
```

### 2. 配置应用

编辑 `config.json` 文件，以设置您的 GitHub 令牌、通知设置、订阅文件和更新间隔：

```json
{
    "github_token": "your_github_token",
    "notification_settings": {
        "email": "your_email@example.com",
        "slack_webhook_url": "your_slack_webhook_url"
    },
    "subscriptions_file": "subscriptions.json",
    "update_interval": 86400
}
```

### 3. 如何运行

GitHub Sentinel 支持以下三种运行方式：

#### A. 作为命令行工具运行

您可以从命令行交互式地运行该应用：

```sh
python src/command_tool.py
```

在此模式下，您可以手动输入命令来管理订阅、检索更新和生成报告。

#### B. 作为后台进程运行（带调度器）

要将该应用作为后台服务（守护进程）运行，它将定期检查更新：

1. 确保您已安装 `python-daemon` 包：

    ```sh
    pip install python-daemon
    ```

2. 启动后台进程：

    ```sh
    nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
    ```

   - 这将启动后台调度器，按照 `config.json` 中指定的间隔定期检查更新。
   - 日志将保存到 `logs/daemon_process.log` 文件中。

#### C. 作为 Gradio 服务器运行（推荐）

要使用 Gradio 界面运行应用，允许用户通过 Web 界面与该工具交互：

```sh
python src/gradio_server.py
```

- 这将在您的机器上启动一个 Web 服务器，允许您通过用户友好的界面管理订阅和生成报告。
- 默认情况下，Gradio 服务器将可在 `http://localhost:7860` 访问。
- **新功能**：
  - 在"订阅管理"标签页可以直接添加新的GitHub项目
  - 在"生成报告"标签页选择项目并设置时间范围生成报告

## 报告生成

系统使用OpenAI的GPT模型生成高质量的项目进展报告。报告包含：
- 新增功能：项目添加的新特性和功能
- 主要改进：对现有功能的优化和增强
- 修复问题：已解决的错误和问题
- 进行中的工作：正在进行但尚未完成的任务

生成的报告保存在`daily_progress`目录中，并可通过Web界面查看和下载。