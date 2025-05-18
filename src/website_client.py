import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import re
from logger import LOG

class WebsiteClient:
    def __init__(self):
        """初始化网站客户端"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 确保输出目录存在
        self.output_dir = "daily_progress/website_articles"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_article(self, url):
        """爬取指定URL的文章内容"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = soup.title.string if soup.title else "未知标题"
            # 清理标题中的特殊字符，防止文件名出错
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
            
            # 提取正文内容 (这里使用简单方法，实际可能需要针对不同网站定制)
            article_text = ""
            
            # 尝试查找文章主体
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
            else:
                # 退化方案：获取所有段落
                paragraphs = soup.find_all('p')
            
            for p in paragraphs:
                article_text += p.get_text() + "\n\n"
            
            # 生成一个包含原始URL的markdown文件
            article_content = f"# {title}\n\n原始链接: {url}\n\n{article_text}"
            
            # 保存原始文章
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            original_file_path = os.path.join(self.output_dir, f"{safe_title}_原文.md")
            with open(original_file_path, "w", encoding="utf-8") as f:
                f.write(article_content)
            
            LOG.info(f"成功爬取文章: {title}")
            return original_file_path, title
            
        except Exception as e:
            LOG.error(f"爬取文章失败: {str(e)}")
            raise
