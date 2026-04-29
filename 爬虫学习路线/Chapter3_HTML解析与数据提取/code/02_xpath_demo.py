"""
XPath表达式实战 - 02_xpath_demo.py

学习内容：
1. 基础路径表达式
2. 谓词（条件筛选）
3. 轴和函数
4. 文本和属性提取

HTML样本：
- 02_sample.html  # 可在浏览器中打开查看结构

运行环境：
python 02_xpath_demo.py
"""

import os  # 导入os模块，用于路径操作
from lxml import etree  # XPath解析库
from bs4 import BeautifulSoup # 对比用

SAMPLE_FILE = os.path.join(os.path.dirname(__file__), '02_sample.html')

def load_html():
    """从文件加载HTML"""
    with open(SAMPLE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

html = load_html()


def basic_xpath():
    tree = etree.HTML(html)

    print("=" * 60)
    print("1. 基础路径表达式")
    print("=" * 60)

    print("\n【1.1 绝对路径】/html/body/main/section/div/h1:")
    titles = tree.xpath('/html/body/main/section/div/h1')
    for t in titles:
        print(f"  - {t.text}")

    print("\n【1.2 相对路径】//h1 查找所有h1:")
    all_h1 = tree.xpath('//h1')
    for t in all_h1:
        print(f"  - {t.text}")

    print("\n【1.3 class选择】//div[@class='news-list']:")
    news_list = tree.xpath('//div[@class="news-list"]')
    print(f"  找到 {len(news_list)} 个")

    print("\n【1.4 后代选择】//div[@class='news-list']//a:")
    links = tree.xpath('//div[@class="news-list"]//a')
    for link in links:
        print(f"  - {link.text}: {link.get('href')}")


def predicate_xpath():
    tree = etree.HTML(html)

    print("\n" + "=" * 60)
    print("2. 谓词（条件筛选）")
    print("=" * 60)

    print("\n【2.1 属性等于】//article[@data-id='1001']:")
    article = tree.xpath('//article[@data-id="1001"]')
    if article:
        title = article[0].xpath('.//h2[@class="news-title"]/a/text()')[0]
        print(f"  - {title}")

    print("\n【2.2 位置[1]】//article[1]:")
    first = tree.xpath('//article[1]')
    if first:
        title = first[0].xpath('.//h2[@class="news-title"]/a/text()')[0]
        print(f"  - {title}")

    print("\n【2.3 last()】//article[last()]:")
    last = tree.xpath('//article[last()]')
    if last:
        title = last[0].xpath('.//h2[@class="news-title"]/a/text()')[0]
        print(f"  - {title}")

    print("\n【2.4 位置范围】//article[position() <= 2]:")
    articles = tree.xpath('//article[position() <= 2]')
    for a in articles:
        title = a.xpath('.//h2[@class="news-title"]/a/text()')[0]
        print(f"  - {title}")

    print("\n【2.5 文本包含】//span[contains(@class, 'author')]:")
    spans = tree.xpath('//span[contains(@class, "author")]')
    for span in spans:
        print(f"  - {span.text}")


def axis_xpath():
    tree = etree.HTML(html)

    print("\n" + "=" * 60)
    print("3. 轴（Axes）表达式")
    print("=" * 60)

    print("\n【3.1 following-sibling】h2后的span兄弟元素:")
    h2_elements = tree.xpath('//h2[@class="news-title"]')
    for h2 in h2_elements[:1]:
        spans = h2.xpath('following-sibling::span[@class]')
        for span in spans:
            print(f"  - {span.text}")

    print("\n【3.2 parent::】a标签的父元素:")
    links = tree.xpath('//div[@class="news-list"]//a')
    for link in links[:1]:
        parent_class = link.xpath('parent::*')[0].get('class')
        print(f"  - 父元素class: {parent_class}")

    print("\n【3.3 ancestor::】查找a的祖先div[@class]:")
    link = tree.xpath('//article[@data-id="1001"]//a')[0]
    ancestors = link.xpath('ancestor::div[@class]/@class')
    print(f"  - 祖先div的class: {ancestors}")


def text_attribute_xpath():
    tree = etree.HTML(html)

    print("\n" + "=" * 60)
    print("4. 文本和属性提取")
    print("=" * 60)

    print("\n【4.1 text()】提取链接文本:")
    links = tree.xpath('//div[@class="news-list"]//a/text()')
    for text in links:
        print(f"  - {text}")

    print("\n【4.2 @属性】提取链接href:")
    hrefs = tree.xpath('//div[@class="news-list"]//a/@href')
    for href in hrefs:
        print(f"  - {href}")

    print("\n【4.3 组合】提取新闻ID和标题:")
    articles = tree.xpath('//article[@data-id]')
    for article in articles:
        news_id = article.get('data-id')
        title = article.xpath('.//h2[@class="news-title"]/a/text()')[0]
        author = article.xpath('.//span[@class="author"]/text()')[0]
        print(f"  [{news_id}] {title} - {author}")

    print("\n【4.4 string(.)】提取整个article的文本:")
    article = tree.xpath('//article[@data-id="1001"]')[0]
    all_text = article.xpath('string(.)').strip()
    print(f"  - {all_text[:50]}...")


def css_vs_xpath():
    soup = BeautifulSoup(html, 'html.parser')

    print("\n" + "=" * 60)
    print("5. CSS选择器 vs XPath 对比")
    print("=" * 60)

    print("\n【场景1】获取所有新闻标题链接文本:")

    css_links = soup.select('.news-item .news-title a')
    print(f"  CSS: {[a.text for a in css_links]}")

    xpath_links = tree.xpath('//article[@class="news-item"]//h2[@class="news-title"]/a/text()')
    print(f"  XPath: {xpath_links}")

    print("\n【场景2】获取所有作者:")

    css_authors = soup.select('.news-item .author')
    print(f"  CSS: {[a.text for a in css_authors]}")

    xpath_authors = tree.xpath('//article[@class="news-item"]//span[@class="author"]/text()')
    print(f"  XPath: {xpath_authors}")


def main():
    print(f"HTML样本文件: {SAMPLE_FILE}")
    print("提示: 可在浏览器中打开该HTML文件查看结构\n")

    basic_xpath()
    predicate_xpath()
    axis_xpath()
    text_attribute_xpath()
    css_vs_xpath()

    print("\n" + "=" * 60)
    print("XPath表达式演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()