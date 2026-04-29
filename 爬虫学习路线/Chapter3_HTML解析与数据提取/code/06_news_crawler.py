"""
综合案例：新闻网站数据提取 - 06_news_crawler.py

实战项目：抓取新闻网站，提取标题、链接、日期、摘要

HTML样本：
- 06_sample.html  # 可在浏览器中打开查看结构

运行环境：
python 06_news_crawler.py
"""

import os
import requests
from bs4 import BeautifulSoup
import json
import time
import sys
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SAMPLE_FILE = os.path.join(os.path.dirname(__file__), '06_sample.html')


def load_html():
    """从文件加载HTML"""
    with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
        return f.read()


class NewsCrawler:
    def __init__(self):
        self.news_list = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"获取页面失败: {e}")
            return None

    def parse_news_list(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []

        for article in soup.select('.news-item'):
            news = {}

            title_elem = article.select_one('.news-title a')
            if title_elem:
                news['title'] = title_elem.text.strip()
                news['link'] = title_elem.get('href', '')

            category_elem = article.select_one('.category')
            if category_elem:
                news['category'] = category_elem.text.strip()

            author_elem = article.select_one('.author')
            if author_elem:
                news['author'] = author_elem.text.strip()

            time_elem = article.select_one('.publish-time')
            if time_elem:
                news['publish_time'] = time_elem.text.strip()

            views_elem = article.select_one('.views')
            if views_elem:
                views_text = views_elem.text.strip()
                news['views'] = int(re.search(r'\d+', views_text).group()) if re.search(r'\d+', views_text) else 0

            summary_elem = article.select_one('.news-summary')
            if summary_elem:
                news['summary'] = summary_elem.text.strip()

            tags = [tag.text for tag in article.select('.tag')]
            news['tags'] = tags

            news['id'] = article.get('data-id', '')

            news['is_top'] = article.select_one('.news-badge') is not None

            if news.get('title'):
                news_items.append(news)

        return news_items

    def save_to_json(self, data, filename='output/news.json'):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已保存到: {filename}")

    def crawl(self, html_content=None):
        if html_content is None:
            html_content = load_html()

        print("开始解析新闻...")
        self.news_list = self.parse_news_list(html_content)
        print(f"解析完成，共 {len(self.news_list)} 条新闻")

        return self.news_list

    def display_news(self):
        print("\n" + "=" * 70)
        print("新闻列表")
        print("=" * 70)

        for i, news in enumerate(self.news_list, 1):
            print(f"\n【{i}】{news.get('title', '无标题')}")
            if news.get('is_top'):
                print("  🔝 置顶")
            print(f"  分类: {news.get('category', '无')}")
            print(f"  作者: {news.get('author', '无')}")
            print(f"  时间: {news.get('publish_time', '无')}")
            print(f"  浏览: {news.get('views', 0)}")
            print(f"  摘要: {news.get('summary', '无')[:50]}...")
            if news.get('tags'):
                print(f"  标签: {', '.join(news.get('tags', []))}")


def demo():
    print("=" * 70)
    print("新闻网站数据提取 - 综合案例")
    print("=" * 70)

    print(f"\nHTML样本文件: {SAMPLE_FILE}")
    print("提示: 可在浏览器中打开该HTML文件查看结构\n")

    crawler = NewsCrawler()
    news_list = crawler.crawl()
    crawler.display_news()
    crawler.save_to_json(news_list, 'output/demo_news.json')

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    demo()