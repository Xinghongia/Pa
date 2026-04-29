"""
多平台新闻聚合器 - projectA.py

功能：
1. 解析列表页，提取新闻链接
2. 解析详情页，提取标题/作者/日期/正文
3. 处理分页，自动翻页采集
4. 数据去重
5. 保存为JSON格式

HTML样本：
- projectA_list.html   # 列表页样本（浏览器打开查看结构）
- projectA_detail.html # 详情页样本

运行环境：
python projectA.py
"""

import requests
from bs4 import BeautifulSoup
from lxml import etree # XML解析库
import json  # JSON解析库
import re # 正则表达式
import sys # 系统模块
import time # 时间模块
import os # 操作系统模块
from datetime import datetime
from urllib.parse import urljoin

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://example.com"
LIST_URL_TEMPLATE = BASE_URL + "/news?page={page}"
DETAIL_URL_TEMPLATE = BASE_URL + "/news/{id}.html"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': BASE_URL,
}

SAMPLE_LIST_FILE = os.path.join(os.path.dirname(__file__), 'projectA_list.html')
SAMPLE_DETAIL_FILE = os.path.join(os.path.dirname(__file__), 'projectA_detail.html')


def load_list_html():
    with open(SAMPLE_LIST_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def load_detail_html():
    with open(SAMPLE_DETAIL_FILE, 'r', encoding='utf-8') as f:
        return f.read()


class NewsAggregator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.seen_ids = set()
        self.news_list = []
        self.crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def fetch_page(self, url, timeout=10):
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"获取页面失败: {url}, 错误: {e}")
            return None

    def parse_list_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = []

        for item in soup.select('.news-item'):
            news_id = item.get('data-id', '')

            if not self.is_new(news_id):
                continue

            link_elem = item.select_one('.title a')
            if not link_elem:
                continue

            title = link_elem.text.strip()
            href = link_elem.get('href', '')
            full_url = urljoin(BASE_URL, href)

            source_elem = item.select_one('.source')
            source = source_elem.text.replace('来源：', '').strip() if source_elem else ''

            author_elem = item.select_one('.author')
            author = author_elem.text.replace('作者：', '').strip() if author_elem else ''

            date_elem = item.select_one('.date')
            date = date_elem.text.strip() if date_elem else ''

            summary_elem = item.select_one('.summary')
            summary = summary_elem.text.strip() if summary_elem else ''

            tags = [tag.text.strip() for tag in item.select('.tag')]

            news_items.append({
                'id': news_id,
                'title': title,
                'source': source,
                'author': author,
                'publish_time': date,
                'summary': summary,
                'tags': tags,
                'url': full_url,
                'crawl_time': self.crawl_time,
            })

        return news_items

    def parse_detail_page(self, html, news_info):
        tree = etree.HTML(html)

        content_elem = tree.xpath('//div[@class="content"]')
        if content_elem:
            content = tree.xpath('string(//div[@class="content"])').strip()
            content = re.sub(r'\s+', ' ', content)
            news_info['content'] = content
        else:
            news_info['content'] = ''

        views_elem = tree.xpath('//span[@class="views"]/text()')
        if views_elem:
            views_text = views_elem[0]
            views_match = re.search(r'\d+', views_text)
            news_info['views'] = int(views_match.group()) if views_match else 0
        else:
            news_info['views'] = 0

        return news_info

    def has_next_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.select_one('.pagination .next-page') is not None

    def is_new(self, news_id):
        if not news_id:
            return True
        if news_id in self.seen_ids:
            return False
        self.seen_ids.add(news_id)
        return True

    def crawl_list(self, max_pages=3, use_sample=True):
        print(f"开始采集列表页，最多 {max_pages} 页...")

        for page in range(1, max_pages + 1):
            print(f"\n--- 第 {page} 页 ---")

            if use_sample:
                html = load_list_html()
            else:
                url = LIST_URL_TEMPLATE.format(page=page)
                html = self.fetch_page(url)
                if not html:
                    continue

            news_items = self.parse_list_page(html)
            print(f"解析到 {len(news_items)} 条新闻")

            for news in news_items:
                self.news_list.append(news)

            if not self.has_next_page(html):
                print("已到达最后一页")
                break

            if use_sample:
                break

            time.sleep(0.5)

        print(f"\n列表采集完成，共 {len(self.news_list)} 条新闻")

    def crawl_detail(self, use_sample=True):
        print("\n开始采集详情页...")

        for i, news in enumerate(self.news_list):
            print(f"[{i+1}/{len(self.news_list)}] 采集: {news['title'][:30]}...")

            if use_sample:
                detail_info = self.parse_detail_page(load_detail_html(), news)
            else:
                html = self.fetch_page(news['url'])
                if html:
                    detail_info = self.parse_detail_page(html, news)
                else:
                    detail_info = news
                    detail_info['content'] = ''

            self.news_list[i] = detail_info

            if not use_sample:
                time.sleep(0.3)

        print("详情采集完成")

    def save_to_json(self, filename='output/news_aggregator.json'):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.news_list, f, ensure_ascii=False, indent=2)

        print(f"\n数据已保存到: {filename}")
        print(f"共 {len(self.news_list)} 条新闻")

    def display_news(self):
        print("\n" + "=" * 70)
        print("新闻列表预览")
        print("=" * 70)

        for i, news in enumerate(self.news_list[:5], 1):
            print(f"\n【{i}】{news.get('title', '无标题')}")
            print(f"    ID: {news.get('id', '无')}")
            print(f"    来源: {news.get('source', '无')}")
            print(f"    作者: {news.get('author', '无')}")
            print(f"    时间: {news.get('publish_time', '无')}")
            print(f"    摘要: {news.get('summary', '无')[:50]}...")
            if news.get('content'):
                print(f"    正文: {news['content'][:50]}...")

        if len(self.news_list) > 5:
            print(f"\n... 还有 {len(self.news_list) - 5} 条新闻")

    def run(self, max_pages=3, crawl_detail_flag=True):
        print("=" * 70)
        print("多平台新闻聚合器")
        print("=" * 70)

        self.crawl_list(max_pages=max_pages)

        if self.news_list:
            self.display_news()

            if crawl_detail_flag:
                self.crawl_detail()

            self.save_to_json()
        else:
            print("没有采集到任何新闻")

        print("\n" + "=" * 70)
        print("爬取完成！")
        print("=" * 70)


def main():
    aggregator = NewsAggregator()
    aggregator.run(max_pages=3, crawl_detail_flag=True)


if __name__ == "__main__":
    main()