"""
CSS选择器基础 - 01_css_selector.py

学习内容：
1. 标签选择器、类选择器、ID选择器
2. 后代选择器、子选择器
3. 属性选择器
4. 伪类选择器

HTML样本：
- 01_sample.html  # 可在浏览器中打开查看结构

运行环境：
python 01_css_selector.py
"""

import os
from bs4 import BeautifulSoup

SAMPLE_FILE = os.path.join(os.path.dirname(__file__), '01_sample.html')

def load_html():
    """从文件加载HTML"""
    with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

html = load_html()


def basic_selectors():
    soup = BeautifulSoup(html, 'html.parser')

    print("=" * 60)
    print("1. 基础选择器")
    print("=" * 60)

    print("\n【1.1 标签选择器】选择所有<a>标签:")
    links = soup.select('a')
    for link in links[:3]:
        print(f"  - {link.text}: {link.get('href')}")

    print("\n【1.2 类选择器】选择class='news-item'的元素:")
    items = soup.select('.news-item')
    print(f"  找到 {len(items)} 个新闻项")

    print("\n【1.3 ID选择器】选择id='header'的元素:")
    header = soup.select_one('#header')
    print(f"  标签: {header.name}")

    print("\n【1.4 后代选择器】选择.news-list内的.news-item:")
    news_items = soup.select('.news-list .news-item')
    print(f"  找到 {len(news_items)} 个")

    print("\n【1.5 子选择器】选择.nav-list的直接<li>子元素:")
    nav_items = soup.select('.nav-list > li')
    for li in nav_items:
        print(f"  - {li.text.strip()}")


def attribute_selectors():
    soup = BeautifulSoup(html, 'html.parser')

    print("\n" + "=" * 60)
    print("2. 属性选择器")
    print("=" * 60)

    print("\n【2.1 属性存在】选择有target属性的链接:")
    links = soup.select('a[target]')
    for link in links:
        print(f"  - {link.text}: {link.get('href')}")

    print("\n【2.2 属性等于】选择href='/news'的链接:")
    links = soup.select('a[href="/news"]')
    for link in links:
        print(f"  - {link.text}")

    print("\n【2.3 属性包含】选择href包含'python'的标签:")
    tags = soup.select('[data-tag*="python"]')
    for tag in tags:
        print(f"  - {tag.text}")

    print("\n【2.4 属性开头】选择href以'/'开头的链接:")
    links = soup.select('a[href^="/"]')
    for link in links[:5]:
        print(f"  - {link.get('href')}")

    print("\n【2.5 属性结尾】选择href以'.html'结尾的链接:")
    links = soup.select('a[href$=".html"]')
    for link in links:
        print(f"  - {link.get('href')}")


def pseudo_selectors():
    soup = BeautifulSoup(html, 'html.parser')

    print("\n" + "=" * 60)
    print("3. 伪类选择器")
    print("=" * 60)

    print("\n【3.1 :first-child】选择第一个新闻项的标题:")
    first_title = soup.select_one('.news-item:first-child .news-title')
    print(f"  - {first_title.text.strip()}")

    print("\n【3.2 :last-child】选择最后一个新闻项:")
    last_item = soup.select_one('.news-item:last-child')
    print(f"  - 最后一条新闻ID: {last_item.get('data-id')}")

    print("\n【3.3 :nth-child(2)】选择第二个新闻项:")
    second_item = soup.select_one('.news-item:nth-child(2)')
    print(f"  - 第二条新闻ID: {second_item.get('data-id')}")

    print("\n【3.4 :nth-child(odd/even)】选择奇数行新闻项:")
    odd_items = soup.select('.news-item:nth-child(odd)')
    for item in odd_items:
        print(f"  - ID: {item.get('data-id')}")


def practical_extraction():
    soup = BeautifulSoup(html, 'html.parser')

    print("\n" + "=" * 60)
    print("4. 实际提取演练 - 新闻列表")
    print("=" * 60)

    news_list = []

    for item in soup.select('.news-item'):
        news = {
            'id': item.get('data-id'),
            'title': item.select_one('.news-title').text.strip(),
            'link': item.select_one('.news-title a').get('href'),
            'author': item.select_one('.author').text.replace('作者：', ''),
            'date': item.select_one('.date').text,
            'views': item.select_one('.views').text.replace('阅读：', ''),
            'summary': item.select_one('.news-summary').text,
            'tags': [tag.text for tag in item.select('.tag')]
        }
        news_list.append(news)

    for news in news_list:
        print(f"\n【{news['id']}】{news['title']}")
        print(f"  链接: {news['link']}")
        print(f"  作者: {news['author']} | 日期: {news['date']} | 阅读: {news['views']}")
        print(f"  摘要: {news['summary']}")
        print(f"  标签: {', '.join(news['tags'])}")


def main():
    print(f"HTML样本文件: {SAMPLE_FILE}")
    print("提示: 可在浏览器中打开该HTML文件查看结构\n")

    basic_selectors()
    attribute_selectors()
    pseudo_selectors()
    practical_extraction()

    print("\n" + "=" * 60)
    print("CSS选择器演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()