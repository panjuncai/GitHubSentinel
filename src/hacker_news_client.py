import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, date, timedelta
from logger import LOG

class HackerNewsClient:
    def __init__(self):
        self.base_url = "https://news.ycombinator.com"

    def fetch_hackernews_top_stories(self):
        response = requests.get(self.base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        stories = soup.find_all("tr", class_="athing")

        top_stories = []
        for story in stories:
            title_tag = story.find("span", class_="titleline")
            if title_tag:
                title=title_tag.find("a").text
                link=title_tag.find("a")['href']
                top_stories.append({
                    "title": title,
                    "link": link
                })

        return top_stories

    def export_daily_trends(self):
        LOG.debug("[准备导出Hacker News趋势]")
        today = datetime.now().date().isoformat()  # 获取今天的日期
        stories = self.fetch_hackernews_top_stories()  # 获取今天的热门文章
        
        # 确保目录存在
        reports_dir = os.path.join('daily_progress', 'hacker_news')
        os.makedirs(reports_dir, exist_ok=True)
        
        # 构建文件路径
        file_path = os.path.join(reports_dir, f'{today}.md')
        
        # 写入文件
        with open(file_path, 'w') as file:
            file.write(f"# Hacker News 热门文章 ({today})\n\n")
            file.write("\n## 今日热门文章\n")
            for idx, story in enumerate(stories[:20], start=1):  # 只保留前20条
                file.write(f"{idx}. [{story['title']}]({story['link']})\n")
        
        LOG.info(f"Hacker News趋势报告已生成: {file_path}")
        return file_path
    
    def export_trends_by_date_range(self, days):
        today = date.today()
        since = today - timedelta(days=days)
        
        stories = self.fetch_hackernews_top_stories()  # 获取当前热门文章
        
        # 确保目录存在
        reports_dir = os.path.join('daily_progress', 'hacker_news')
        os.makedirs(reports_dir, exist_ok=True)
        
        # 更新文件名以包含日期范围
        date_str = f"{since}_to_{today}"
        file_path = os.path.join(reports_dir, f'{date_str}.md')
        
        # 写入文件
        with open(file_path, 'w') as file:
            file.write(f"# Hacker News 技术洞察 ({since} 至 {today})\n\n")
            file.write(f"## 技术前沿趋势与热点话题\n\n")
            file.write("以下是最近{days}天内Hacker News上的热门文章：\n\n")
            for idx, story in enumerate(stories[:20], start=1):
                file.write(f"{idx}. [{story['title']}]({story['link']})\n")
        
        LOG.info(f"Hacker News趋势报告已生成: {file_path}")
        return file_path
    
    def generate_trends_insight(self, stories, template_path=None):
        """
        使用提供的提示词模板生成技术趋势洞察
        """
        # 默认模板路径
        if not template_path:
            template_path = os.path.join("prompts", "hackernews_prompt.txt")
        
        # 准备文章列表
        stories_text = ""
        for idx, story in enumerate(stories[:20], start=1):
            stories_text += f"{idx}. {story['title']} - {story['link']}\n"
            
        today_date = date.today().isoformat()
        
        # 如果存在模板文件，则使用模板；否则使用默认模板
        try:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
            else:
                template = """
你是一个关注 Hacker News 的技术专家，擅于洞察技术热点和发展趋势。

任务：
根据你收到的 Hacker News Top List，分析和总结当前技术圈讨论的热点，不超过5条。

格式：
# Hacker News 技术洞察

## 时间：{date}

## 技术前沿趋势与热点话题

1. **个人项目与创作**：许多用户在 "Ask HN" 讨论中分享了他们正在进行的项目，这凸显了开发者界对个人创作及创业的持续热情。

2. **网络安全思考**：有关于"防守者和攻击者思考方式"的讨论引发了对网络安全策略的深入思考。这种对比强调防守与攻击之间的心理与技术差异，表明网络安全领域对攻击者策略的关注日益增加。
"""
                
            # 替换模板中的日期
            template = template.replace("{date}", today_date)
            
            # 返回模板和文章内容
            return template, stories_text
            
        except Exception as e:
            LOG.error(f"生成趋势洞察模板时出错: {str(e)}")
            return "", stories_text

if __name__ == "__main__":
    hacker_news_client = HackerNewsClient()
    top_stories = hacker_news_client.fetch_hackernews_top_stories()
    for idx,story in enumerate(top_stories,start=1):
        print(f"{idx}. {story['title']} - {story['link']}")
    
    # 生成今日报告
    report_path = hacker_news_client.export_daily_trends()
    print(f"报告已生成: {report_path}")