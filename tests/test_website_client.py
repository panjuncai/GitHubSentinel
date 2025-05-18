import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from website_client import WebsiteClient  # 导入要测试的 WebsiteClient 类

class TestWebsiteClient(unittest.TestCase):
    def setUp(self):
        """
        在每个测试方法之前运行，初始化测试环境。
        """
        # 创建临时目录作为测试输出目录
        self.temp_dir = tempfile.mkdtemp()
        # 保存原始输出目录路径
        self.original_output_dir = "daily_progress/website_articles"
        
        # 初始化 WebsiteClient 实例
        self.client = WebsiteClient()
        # 修改输出目录为临时目录
        self.client.output_dir = os.path.join(self.temp_dir, "website_articles")
        # 确保输出目录存在
        os.makedirs(self.client.output_dir, exist_ok=True)

    def tearDown(self):
        """
        在每个测试方法之后运行，清理测试环境。
        """
        # 删除临时目录
        shutil.rmtree(self.temp_dir)

    @patch('website_client.requests.get')
    def test_fetch_article_with_article_tag(self, mock_get):
        """
        测试 fetch_article 方法，当网页包含 article 标签时。
        """
        # 模拟 HTTP 响应
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <article>
                    <p>This is the first paragraph.</p>
                    <p>This is the second paragraph.</p>
                </article>
            </body>
        </html>
        """
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # 调用 fetch_article 方法
        article_path, title = self.client.fetch_article("https://example.com/article")
        
        # 断言文件路径和标题
        self.assertTrue(os.path.exists(article_path))
        self.assertIn("Test Article_原文.md", article_path)
        self.assertEqual(title, "Test Article")
        
        # 读取生成的文件内容并验证
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("# Test Article", content)
            self.assertIn("原始链接: https://example.com/article", content)
            self.assertIn("This is the first paragraph.", content)
            self.assertIn("This is the second paragraph.", content)

    @patch('website_client.requests.get')
    def test_fetch_article_without_article_tag(self, mock_get):
        """
        测试 fetch_article 方法，当网页不包含 article 标签时。
        """
        # 模拟 HTTP 响应
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <div>
                    <p>This is a paragraph without article tag.</p>
                    <p>This is another paragraph.</p>
                </div>
            </body>
        </html>
        """
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # 调用 fetch_article 方法
        article_path, title = self.client.fetch_article("https://example.com/page")
        
        # 断言文件路径和标题
        self.assertTrue(os.path.exists(article_path))
        self.assertIn("Test Page_原文.md", article_path)
        self.assertEqual(title, "Test Page")
        
        # 读取生成的文件内容并验证
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("# Test Page", content)
            self.assertIn("原始链接: https://example.com/page", content)
            self.assertIn("This is a paragraph without article tag.", content)
            self.assertIn("This is another paragraph.", content)

    @patch('website_client.requests.get')
    def test_fetch_article_with_special_chars_in_title(self, mock_get):
        """
        测试 fetch_article 方法处理标题中的特殊字符。
        """
        # 模拟 HTTP 响应
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <head><title>Test: Article with "special" chars?</title></head>
            <body>
                <p>Article content.</p>
            </body>
        </html>
        """
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # 调用 fetch_article 方法
        article_path, title = self.client.fetch_article("https://example.com/special")
        
        # 断言标题中的特殊字符被正确处理
        # 根据website_client.py的实现，只有 \/*?:"<>| 这些字符会被替换为_
        safe_title = "Test_ Article with _special_ chars_"
        self.assertIn(safe_title, article_path)
        self.assertEqual(title, "Test: Article with \"special\" chars?")

    @patch('website_client.requests.get')
    def test_fetch_article_http_error(self, mock_get):
        """
        测试 fetch_article 方法处理 HTTP 错误。
        """
        # 模拟 HTTP 错误
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response
        
        # 断言调用 fetch_article 方法会抛出异常
        with self.assertRaises(Exception):
            self.client.fetch_article("https://example.com/error")

if __name__ == '__main__':
    unittest.main() 