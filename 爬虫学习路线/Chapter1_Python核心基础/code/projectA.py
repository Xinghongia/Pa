"""
IT之家新闻爬虫 - 完整实现

功能说明：
1. 并发请求多个分类的新闻列表页
2. 解析每条新闻的标题、链接、发布时间
3. 保存为JSON格式文件

使用方法：
1. 确保已安装依赖：pip install aiohttp beautifulsoup4
2. 运行：python 项目AIT之家新闻爬虫.py
3. 结果保存在当前目录的 ithome_news.json 文件中

合规提醒：
- 仅用于学习目的，爬取公开数据
- 请遵守robots协议，控制请求频率
- 禁止商业用途和侵权行为
"""

import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
from datetime import datetime
import random
import os
import sys

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class NewsCrawler:
    def __init__(self):
        self.base_url = "https://www.ithome.com"
        self.results = []
        # 配置连接池参数
        self.connector_config = {
            "limit": 100,  # 总连接数
            "limit_per_host": 10,  # 单个域名最大连接数
            "ttl_dns_cache": 300,  # DNS缓存时间
            "use_dns_cache": True,  # 启用DNS缓存
        }
        # 请求头配置
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def fetch_page(self, session, url):
        """获取单个页面"""
        timeout = aiohttp.ClientTimeout(total=30)  # 30秒超时
        try:
            async with session.get(
                url,
                headers=self.headers,
                timeout=timeout,
                ssl=False  # 忽略SSL证书验证
            ) as response:
                if response.status == 200:
                    # 尝试解析JSON，否则返回文本
                    try:
                        json_data = await response.json()
                        return json_data
                    except:
                        html = await response.text()
                        return html
                else:
                    print(f"⚠️ 请求失败: {url}, 状态码: {response.status}")
                    return None
        except asyncio.TimeoutError:
            print(f"⏰ 请求超时: {url}")
            return None
        except Exception as e:
            print(f"❌ 请求异常: {url}, 错误: {str(e)}")
            return None

    async def parse_news_list(self, data, category_name):
        """解析新闻列表页 - 支持JSON、HTML和XML三种格式"""
        if not data:
            return []

        news_list = []

        # 如果是JSON数据（API返回）
        if isinstance(data, dict):
            items = data.get('data', {}).get('list', []) or data.get('list', [])
            
            for item in items:
                try:
                    title = item.get('title', '').strip()
                    if not title or len(title) < 5:
                        continue

                    link = item.get('url', '')
                    if link and not link.startswith('http'):
                        link = self.base_url + link

                    publish_time = item.get('time', '') or item.get('date', '')

                    news_list.append({
                        'title': title,
                        'link': link,
                        'publish_time': publish_time,
                        'category': category_name,
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception:
                    continue

        # 如果是HTML/XML数据（字符串）
        elif isinstance(data, str):
            # 使用lxml解析器
            soup = BeautifulSoup(data, 'lxml')
            
            # 解析RSS XML格式
            if soup.find('rss') or soup.find('feed') or soup.find('channel'):
                # 使用正则表达式提取item块
                import re
                item_pattern = r'<item>(.*?)</item>'
                items = re.findall(item_pattern, data, re.DOTALL)
                
                for item_content in items:
                    try:
                        # 提取标题
                        title_match = re.search(r'<title>(.*?)</title>', item_content, re.DOTALL)
                        if not title_match:
                            continue
                        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                        
                        if not title or len(title) < 5:
                            continue

                        # 提取链接
                        link_match = re.search(r'<link>(.*?)</link>', item_content)
                        link = link_match.group(1).strip() if link_match else ''
                        
                        # 如果link为空，尝试提取guid
                        if not link:
                            guid_match = re.search(r'<guid>(.*?)</guid>', item_content)
                            link = guid_match.group(1).strip() if guid_match else ''

                        # 提取时间
                        pubdate_match = re.search(r'<pubDate>(.*?)</pubDate>', item_content)
                        publish_time = pubdate_match.group(1).strip() if pubdate_match else ''

                        news_list.append({
                            'title': title,
                            'link': link,
                            'publish_time': publish_time,
                            'category': category_name,
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except Exception:
                        continue
            else:
                # 解析HTML格式
                news_items = soup.select('a[href*="/news/"], a[href*="/it/"], .newslist a')

                for item in news_items:
                    try:
                        title = item.get_text(strip=True)
                        if not title or len(title) < 5:
                            continue

                        link = item.get('href', '')
                        if link.startswith('/'):
                            link = self.base_url + link
                        elif link and not link.startswith('http'):
                            link = self.base_url + '/' + link

                        if not link:
                            continue

                        news_list.append({
                            'title': title,
                            'link': link,
                            'publish_time': '',
                            'category': category_name,
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except Exception:
                        continue

        return news_list

    async def crawl_category(self, session, category, semaphore):
        """爬取单个分类"""
        # 使用IT之家的RSS订阅源（更稳定，返回XML格式）
        url = f"https://www.ithome.com/rss/"

        # 使用信号量控制并发
        async with semaphore:
            print(f"📡 开始爬取: {category}")

            # 添加随机延时，避免请求过快
            await asyncio.sleep(random.uniform(0.5, 1.5))

            html = await self.fetch_page(session, url)
            if html:
                news_list = await self.parse_news_list(html, category)

                if news_list:
                    self.results.extend(news_list)
                    print(f"✅ {category}: 获取 {len(news_list)} 条新闻")
                else:
                    print(f"⚠️ {category}: 未解析到新闻数据")
            else:
                print(f"❌ {category}: 页面请求失败")

    async def crawl_all(self, categories):
        """并发爬取所有分类"""
        # 创建连接池
        connector = aiohttp.TCPConnector(**self.connector_config)

        # 创建信号量，控制最大并发数为5
        semaphore = asyncio.Semaphore(5)

        # 使用 with 语句管理 Session
        async with aiohttp.ClientSession(
            connector=connector, # 使用连接池
            headers=self.headers  # 设置请求头
               ) as session:
            # 创建所有分类的爬取任务
            tasks = [
                self.crawl_category(session, category, semaphore) # 创建任务
                for category in categories 
            ]

            # 并发执行所有任务
            await asyncio.gather(*tasks, return_exceptions=True)

    def save_results(self, filename):
        """保存结果为JSON文件"""
        if not self.results:
            print("⚠️ 没有数据可保存")
            return

        # 确保目录存在
        dir_name = os.path.dirname(filename)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"💾 数据已保存到: {filename}")
        print(f"📊 共保存 {len(self.results)} 条新闻")


async def main():
    # 分类列表（可根据需要修改）
    # 使用IT之家实际的分类URL格式
    categories = [
        "it",         # IT资讯
        "mobile",     # 手机
        "computer",   # 电脑
        "digital",    # 数码
        "car",        # 汽车
        "enterprise", # 企业
        "game",       # 游戏
        "science",    # 科学
    ]

    print("=" * 50)
    print("🚀 IT之家新闻爬虫启动")
    print("=" * 50)
    print(f"📋 待爬取分类: {len(categories)} 个")
    print("⚠️ 合规提醒: 仅用于学习，请遵守robots协议")
    print("-" * 50)

    start_time = datetime.now()

    crawler = NewsCrawler()
    await crawler.crawl_all(categories) 
		#aiait确实要等这个完成才能继续执行下面的代码，但是可以让出cpu资源执行别的函数任务

    # 保存结果
    crawler.save_results("ithome_news.json")

    elapsed = (datetime.now() - start_time).total_seconds()
    print("-" * 50)
    print(f"✅ 爬虫完成，耗时: {elapsed:.2f} 秒")
    print(f"📊 共爬取 {len(crawler.results)} 条新闻")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
