"""
国家统计局数据爬虫 - stats_crawler.py

功能：爬取国家统计局官方公开数据（GDP、CPI、人口、收入等指标）

数据来源：https://www.stats.gov.cn （国家统计局主站）

数据页面：
- 数据发布：https://www.stats.gov.cn/sj/
- 最新发布：https://www.stats.gov.cn/sj/zxfb/

⚠️ 合规提醒：
1. 本代码仅用于学习研究，爬取国家统计局公开数据
2. 请遵守网站robots协议和使用条款
3. 禁止将数据用于商业盈利目的
4. 请控制请求频率，不要对服务器造成压力
5. 数据版权归属国家统计局，仅授权个人学习使用

运行环境：
pip install requests beautifulsoup4 pandas lxml
python stats_crawler.py
"""

import os
import sys
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://www.stats.gov.cn"
DATA_URL = f"{BASE_URL}/sj/"
ZXFZ_URL = f"{BASE_URL}/sj/zxfb/"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/2010 Firefox/121.0',
]

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

REQUEST_DELAY = 1.5


class StatsCrawler:
    """国家统计局数据爬虫类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._init_session()

    def _init_session(self):
        """初始化会话，获取Cookie"""
        try:
            self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
            response = self.session.get(BASE_URL, timeout=15)
            response.raise_for_status()
            print("会话初始化成功")
        except requests.RequestException as e:
            print(f"会话初始化失败: {e}")

    def _make_request(self, url: str) -> Optional[str]:
        """
        发送HTTP请求获取HTML

        参数：
            url: 请求URL

        返回：
            HTML文本，失败返回None
        """
        try:
            time.sleep(REQUEST_DELAY + random.uniform(0, 0.5))
            self.session.headers['User-Agent'] = random.choice(USER_AGENTS)
            self.session.headers['Referer'] = BASE_URL

            response = self.session.get(url, timeout=20)

            if response.status_code == 403:
                print(f"被反爬拦截，状态码: 403")
                return None

            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text

        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def parse_news_list(self, html: str) -> List[Dict]:
        """
        解析数据发布列表页

        参数：
            html: 页面HTML

        返回：
            新闻列表，每项包含 title、link、date
        """
        soup = BeautifulSoup(html, 'lxml')
        news_list = []

        for item in soup.select('.list-content ul li'):
            title_elem = item.select_one('a.fl, a:first-of-type')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')

            if link and not link.startswith('http'):
                if link.startswith('./'):
                    link = ZXFZ_URL + link[2:]
                elif link.startswith('/'):
                    link = BASE_URL + link
                else:
                    link = ZXFZ_URL + link

            date_elem = item.select_one('span')
            date = date_elem.get_text(strip=True) if date_elem else ''

            if title:
                news_list.append({
                    'title': title,
                    'link': link,
                    'date': date
                })

        return news_list

    def parse_detail_page(self, html: str) -> Dict:
        """
        解析数据详情页

        参数：
            html: 页面HTML

        返回：
            包含标题、内容、发布时间的字典
        """
        soup = BeautifulSoup(html, 'lxml')

        title = ''
        title_elem = soup.select_one('h1')
        if title_elem:
            title = title_elem.get_text(strip=True)

        if not title or len(title) < 5:
            title_elem = soup.select_one('meta[name="ArticleTitle"]')
            if title_elem:
                title = title_elem.get('content', '')

        if not title or len(title) < 5:
            title_elem = soup.select_one('title')
            if title_elem:
                title_text = title_elem.get_text(strip=True)
                title = title_text.split(' - ')[0] if ' - ' in title_text else title_text

        content_elem = soup.select_one('.txt-content')
        if not content_elem:
            content_elem = soup.select_one('.detail-text-content')

        content = content_elem.get_text(strip=True) if content_elem else ''

        date = ''
        date_elem = soup.select_one('meta[name="PubDate"]')
        if date_elem:
            date = date_elem.get('content', '')

        if not date:
            date_elem = soup.select_one('.detail-title-des h2 p')
            if date_elem:
                date = date_elem.get_text(strip=True)

        content = ' '.join(content.split())[:1000] + '...' if len(content) > 1000 else content

        return {
            'title': title,
            'content': content,
            'date': date
        }

    def crawl_latest_news(self, url: str = None) -> List[Dict]:
        """
        爬取最新发布数据

        参数：
            url: 列表页URL，默认使用最新发布页

        返回：
            新闻列表
        """
        target_url = url or ZXFZ_URL
        print(f"正在爬取: {target_url}")

        html = self._make_request(target_url)
        if not html:
            return []

        news_list = self.parse_news_list(html)
        print(f"获取到 {len(news_list)} 条数据")
        return news_list

    def crawl_detail(self, url: str) -> Optional[Dict]:
        """
        爬取数据详情页

        参数：
            url: 详情页URL

        返回：
            详情数据
        """
        print(f"正在爬取详情: {url}")

        html = self._make_request(url)
        if not html:
            return None

        return self.parse_detail_page(html)

    def save_to_json(self, data: List[Dict], filename: str = 'output/stats_news.json'):
        """保存为JSON"""
        import json
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filename}")

    def save_to_csv(self, data: List[Dict], filename: str = 'output/stats_news.csv'):
        """保存为CSV"""
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {filename}")

    def parse_local_html(self, filepath: str) -> List[Dict]:
        """从本地HTML文件解析列表页数据（用于测试）"""
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        return self.parse_news_list(html)

    def parse_local_detail(self, filepath: str) -> Dict:
        """从本地HTML文件解析详情页数据（用于测试）"""
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        return self.parse_detail_page(html)


def demo_crawl_list():
    """演示：爬取列表页"""
    crawler = StatsCrawler()

    print("\n" + "="*50)
    print("演示1: 从网络爬取最新数据")
    print("="*50)

    news_list = crawler.crawl_latest_news()

    if news_list:
        print("\n数据预览:")
        for i, news in enumerate(news_list[:5]):
            print(f"\n{i+1}. {news['title']}")
            print(f"   链接: {news['link']}")
            print(f"   日期: {news['date']}")

        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)

        crawler.save_to_json(news_list, os.path.join(output_dir, 'stats_news.json'))
        crawler.save_to_csv(news_list, os.path.join(output_dir, 'stats_news.csv'))
    else:
        print("未能获取到数据")


def demo_crawl_detail():
    """演示：爬取详情页"""
    crawler = StatsCrawler()

    print("\n" + "="*50)
    print("演示: 爬取数据详情页")
    print("="*50)

    print("\n--- 从网络获取列表 ---")
    news_list = crawler.crawl_latest_news()

    if news_list and len(news_list) > 0:
        first_news = news_list[0]
        print(f"\n第一条数据: {first_news['title']}")
        print(f"链接: {first_news['link']}")

        detail = crawler.crawl_detail(first_news['link'])

        if detail:
            print(f"\n标题: {detail['title']}")
            print(f"日期: {detail['date']}")
            print(f"\n内容预览:")
            print(detail['content'][:500])
        else:
            print("未能从网络获取详情，尝试从本地文件解析...")

            local_detail = os.path.join(os.path.dirname(__file__), '..', 't20260429_1963439.html')
            if os.path.exists(local_detail):
                detail = crawler.parse_local_detail(local_detail)
                print(f"\n从本地文件解析成功!")
                print(f"标题: {detail['title']}")
                print(f"日期: {detail['date']}")
                print(f"\n内容预览:")
                print(detail['content'][:500])
    else:
        print("列表为空，尝试从本地文件解析...")

        local_detail = os.path.join(os.path.dirname(__file__), '..', 't20260429_1963439.html')
        if os.path.exists(local_detail):
            detail = crawler.parse_local_detail(local_detail)
            print(f"\n从本地文件解析成功!")
            print(f"标题: {detail['title']}")
            print(f"日期: {detail['date']}")
            print(f"\n内容预览:")
            print(detail['content'][:500])


def main():
    """主函数"""
    print("="*50)
    print("国家统计局数据爬虫")
    print("="*50)
    print("\n本程序演示如何爬取国家统计局的公开数据")
    print("包括：最新发布数据列表、数据详情页")

    demo_crawl_list()

    demo_crawl_detail()

    print("\n" + "="*50)
    print("演示完成！")
    print("="*50)
    print("\n提示：")
    print("- 爬取列表页可获取最新发布的数据标题和链接")
    print("- 爬取详情页可获取完整的数据内容")
    print("- 数据已保存到 output 目录")
    print("\n⚠️ 请遵守使用规定，控制请求频率")


if __name__ == '__main__':
    main()
