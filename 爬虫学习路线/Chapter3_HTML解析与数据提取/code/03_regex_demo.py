"""
正则表达式实战 - 03_regex_demo.py

学习内容：
1. 基础元字符和数量词
2. 字符类和分组
3. 常用爬虫正则模式
4. re模块方法详解

运行环境：
python 03_regex_demo.py
"""

import re  # 导入正则表达式模块


def basic_metachar():
    text = "Python 3.12 是2024年发布的, 最新版本号是3.12.0"

    print("=" * 60)
    print("1. 基础元字符")
    print("=" * 60)

    print("\n【1.1 .】匹配任意字符:")
    pattern = r'P.thon'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【1.2 \\d】匹配数字:")
    pattern = r'\d+'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【1.3 \\w】匹配字母数字下划线:")
    pattern = r'\w+'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【1.4 \\s】匹配空白字符:")
    pattern = r'\s+'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: [{len(matches)}个空格]")

    print("\n【1.5 ^和$】字符串边界:")
    print(f"  ^Python: {bool(re.search(r'^Python', text))}")
    print(f"  0$: {bool(re.search(r'0$', text))}")


def quantifiers():
    text = "Python 3.12.0 Java 21 Spring 5.2"

    print("\n" + "=" * 60)
    print("2. 数量词")
    print("=" * 60)

    print("\n【2.1 *】0次或多次:")
    pattern = r'\d.*'
    match = re.search(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {match.group() if match else '无'}")

    print("\n【2.2 +】1次或多次:")
    pattern = r'\d+\.\d+'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【2.3 ?】0次或1次:")
    pattern = r'Spring 5\.2?'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【2.4 {n}】精确次数:")
    pattern = r'\d{2}'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【2.5 {n,m}】范围次数:")
    pattern = r'\d{1,3}'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")


def character_classes():
    text = "Hello World! 123 abc XYZ @#$%"

    print("\n" + "=" * 60)
    print("3. 字符类 []")
    print("=" * 60)

    print("\n【3.1 [abc]】匹配a或b或c:")
    pattern = r'[aeiou]'
    matches = re.findall(pattern, text.lower())
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【3.2 [a-z]】匹配小写字母:")
    pattern = r'[a-z]+'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【3.3 [0-9]】匹配数字:")
    pattern = r'[0-9]+'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")

    print("\n【3.4 [^abc]】不包含a,b,c:")
    pattern = r'[^a-zA-Z\s]+'
    matches = re.findall(pattern, text)
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")


def groups():
    text = "2024-01-15 10:30:45"

    print("\n" + "=" * 60)
    print("4. 分组和捕获 ()")
    print("=" * 60)

    print("\n【4.1 基础分组】提取日期各部分:")
    pattern = r'(\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, text)
    if match:
        print(f"  完整匹配: {match.group()}")
        print(f"  年: {match.group(1)}")
        print(f"  月: {match.group(2)}")
        print(f"  日: {match.group(3)}")

    print("\n【4.2 命名分组】(?P<name>...):")
    pattern = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
    match = re.search(pattern, text)
    if match:
        print(f"  年: {match.group('year')}")
        print(f"  月: {match.group('month')}")
        print(f"  日: {match.group('day')}")

    print("\n【4.3 非捕获组】(?:...):")
    pattern = r'(?:\d{4})-(\d{2})-(\d{2})'
    match = re.search(pattern, text)
    if match:
        print(f"  捕获组1: {match.group(1)}")
        print(f"  捕获组2: {match.group(2)}")

    print("\n【4.4 或运算】(a|b):")
    pattern = r'(Python|Java|JavaScript)'
    matches = re.findall(pattern, "Python Java JavaScript Python")
    print(f"  模式: {pattern}")
    print(f"  结果: {matches}")


def crawler_patterns():
    html_text = '''
    <div class="news-item" data-id="1001">
        <h2><a href="/news/1001.html">Python 3.12发布</a></h2>
        <span class="date">2024-01-15</span>
        <span class="author">张三</span>
        <p>邮箱: zhangsan@example.com</p>
        <p>电话: 13812345678</p>
    </div>
    '''

    print("\n" + "=" * 60)
    print("5. 爬虫常用正则模式")
    print("=" * 60)

    print("\n【5.1 提取URL】:")
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, html_text)
    print(f"  模式: {url_pattern}")
    print(f"  结果: {urls}")

    print("\n【5.2 提取数字】:")
    id_pattern = r'data-id="(\d+)"'
    ids = re.findall(id_pattern, html_text)
    print(f"  模式: {id_pattern}")
    print(f"  结果: {ids}")

    print("\n【5.3 提取邮箱】:")
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, html_text)
    print(f"  模式: {email_pattern}")
    print(f"  结果: {emails}")

    print("\n【5.4 提取手机号】:")
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, html_text)
    print(f"  模式: {phone_pattern}")
    print(f"  结果: {phones}")

    print("\n【5.5 提取日期】:")
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    dates = re.findall(date_pattern, html_text)
    print(f"  模式: {date_pattern}")
    print(f"  结果: {dates}")

    print("\n【5.6 提取标签内容】:")
    link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
    links = re.findall(link_pattern, html_text)
    print(f"  模式: {link_pattern}")
    for href, text in links:
        print(f"  链接: {href} -> 文本: {text}")

    print("\n【5.7 贪婪 vs 非贪婪】:")
    div_html = '<div class="content"><p>段落1</p><p>段落2</p></div>'

    greedy = re.search(r'<div.*>.*</div>', div_html, re.DOTALL)
    print(f"  贪婪 .*: {greedy.group() if greedy else '无'}")

    non_greedy = re.search(r'<div.*?>.*?</div>', div_html, re.DOTALL)
    print(f"  非贪婪 .*?: {non_greedy.group() if non_greedy else '无'}")


def re_methods():
    text = "Python 3.12发布于2024年, 版本号3.12.0"

    print("\n" + "=" * 60)
    print("6. re模块主要方法")
    print("=" * 60)

    print("\n【6.1 findall】返回所有匹配:")
    result = re.findall(r'\d+\.?\d*', text)
    print(f"  结果: {result}")

    print("\n【6.2 search】返回第一个匹配:")
    result = re.search(r'\d+', text)
    print(f"  匹配: {result.group()}")
    print(f"  位置: {result.start()}-{result.end()}")

    print("\n【6.3 match】从开头匹配:")
    result1 = re.match(r'Python', text)
    result2 = re.match(r'\d+', text)
    print(f"  'Python': {result1.group() if result1 else '无'}")
    print(f"  '\\d+': {result2.group() if result2 else '无'}")

    print("\n【6.4 sub】替换:")
    result = re.sub(r'\d+\.?\d*', 'X.X', text)
    print(f"  原文本: {text}")
    print(f"  替换后: {result}")

    print("\n【6.5 split】分割:")
    result = re.split(r'[,\s]+', "Python Java, Go,Rust")
    print(f"  结果: {result}")

    print("\n【6.6 finditer】迭代器:")
    for m in re.finditer(r'\d+\.?\d*', text):
        print(f"  匹配: {m.group()}, 位置: {m.start()}")


def main():
    basic_metachar()
    quantifiers()
    character_classes()
    groups()
    crawler_patterns()
    re_methods()

    print("\n" + "=" * 60)
    print("正则表达式演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()