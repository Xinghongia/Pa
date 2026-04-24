"""
HTTP头分析与网络工具

学习目标:
1. 掌握常见HTTP请求头的作用
2. 掌握常见HTTP响应头的作用
3. 学会分析和构造请求头
4. 了解网络抓包工具的使用

运行方式:
    python code/06_headers_analysis.py
"""

import requests
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def demonstrate_request_headers():
    """演示请求头的详细作用"""
    print("=" * 60)
    print("HTTP请求头详解")
    print("=" * 60)

    url = "https://httpbin.org/headers"

    response = requests.get(url)
    headers = response.json()['headers']

    print("\n【请求头分类】")

    print("\n【1. 标识类请求头】")
    print("  Host: example.com")
    print("    - 目标主机地址（必填）")
    print("    - 同一服务器可能有多个网站")
    print(f"    - 当前值: {headers.get('Host', 'N/A')}")

    print("\n  User-Agent: Mozilla/5.0...")
    print("    - 浏览器标识")
    print("    - 服务器根据它返回不同内容")
    print(f"    - 当前值: {headers.get('User-Agent', 'N/A')[:50]}...")

    print("\n【2. 内容协商类请求头】")
    print("  Accept: text/html,application/json")
    print("    - 告诉服务器我能接受什么类型")
    print(f"    - 当前值: {headers.get('Accept', 'N/A')}")

    print("\n  Accept-Language: zh-CN,zh;q=0.9")
    print("    - 能接受的语言")
    print("    - q表示优先级")
    print(f"    - 当前值: {headers.get('Accept-Language', 'N/A')}")

    print("\n  Accept-Encoding: gzip, deflate, br")
    print("    - 能接受的压缩方式")
    print("    - gzip压缩最常用")
    print(f"    - 当前值: {headers.get('Accept-Encoding', 'N/A')}")

    print("\n【3. 认证类请求头】")
    print("  Authorization: Bearer xxx")
    print("    - 携带认证信息")
    print("    - Bearer Token、JWT等")

    print("\n  Cookie: session=abc123")
    print("    - 携带Cookie")
    print("    - 维持登录态")
    print(f"    - 当前值: {headers.get('Cookie', 'N/A')}")

    print("\n【4. 来源类请求头】")
    print("  Referer: https://www.google.com")
    print("    - 从哪个页面来的")
    print("    - 用于防盗链")
    print(f"    - 当前值: {headers.get('Referer', 'N/A')}")

    print("\n  Origin: https://www.google.com")
    print("    - 请求来源（用于CORS）")
    print("    - 与Referer类似，但更简洁")

    print("\n【5. 缓存类请求头】")
    print("  Cache-Control: no-cache")
    print("    - 控制缓存行为")
    print("    - no-cache: 不使用缓存")
    print("    - max-age: 缓存时间")

    print("\n  If-None-Match: \"abc123\"")
    print("    - 条件请求")
    print("    - 如果资源没变，返回304")


def demonstrate_response_headers():
    """演示响应头的详细作用"""
    print("\n" + "=" * 60)
    print("HTTP响应头详解")
    print("=" * 60)

    url = "https://httpbin.org/get"
    response = requests.get(url)

    print("\n【响应头分类】")

    print("\n【1. 内容类响应头】")
    print("  Content-Type: text/html; charset=utf-8")
    print("    - 内容的类型和编码")
    print("    - 常见值:")
    print("      - text/html")
    print("      - application/json")
    print("      - image/png")
    print("      - application/octet-stream")
    print(f"    - 当前值: {response.headers.get('Content-Type', 'N/A')}")

    print("\n  Content-Length: 1234")
    print("    - 内容长度（字节）")
    print("    - 方便接收时判断是否完整")
    print(f"    - 当前值: {response.headers.get('Content-Length', 'N/A')}")

    print("\n  Content-Encoding: gzip")
    print("    - 压缩方式")
    print("    - 收到后要解压")
    print(f"    - 当前值: {response.headers.get('Content-Encoding', 'N/A')}")

    print("\n【2. 缓存类响应头】")
    print("  Cache-Control: max-age=3600")
    print("    - 缓存时间（秒）")
    print("    - public: 可被缓存")
    print("    - private: 只在浏览器缓存")

    print("\n  ETag: \"abc123\"")
    print("    - 资源标识")
    print("    - 变化时ETag会变")

    print("\n  Expires: Thu, 01 Jan 2025 00:00:00 GMT")
    print("    - 过期时间")
    print("    - 超过这个时间要重新请求")

    print("\n【3. Cookie类响应头】")
    print("  Set-Cookie: session=abc123; Path=/; HttpOnly; Secure")
    print("    - 让浏览器设置Cookie")
    print("    - HttpOnly: JS不能访问（防XSS）")
    print("    - Secure: 仅HTTPS传输")

    print("\n【4. 安全类响应头】")
    print("  X-Frame-Options: DENY")
    print("    - 防止iframe嵌套")

    print("\n  X-Content-Type-Options: nosniff")
    print("    - 防止MIME类型嗅探")

    print("\n  Strict-Transport-Security: max-age=31536000")
    print("    - 强制使用HTTPS")


def demonstrate_custom_headers():
    """演示自定义请求头"""
    print("\n" + "=" * 60)
    print("自定义请求头")
    print("=" * 60)

    print("\n【常见的自定义请求头】")
    custom_headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'X-Forwarded-For': '203.0.113.1',
        'X-Custom-Header': 'CustomValue',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com',
    }

    for key, value in custom_headers.items():
        print(f"  {key}: {value}")

    print("\n【爬虫中常用的请求头】")
    print("""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    """)


def demonstrate_browsing_headers():
    """演示浏览器完整的请求头"""
    print("\n" + "=" * 60)
    print("浏览器完整请求头示例")
    print("=" * 60)

    print("\n【Chrome访问百度的请求头】")
    browser_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'BID=xxx; BAIDUID=xxx',
        'Host': 'www.baidu.com',
        'Referer': 'https://www.google.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for key, value in browser_headers.items():
        print(f"  {key}: {value}")

    print("\n【每个头部的用途解析】")
    print("  Sec-Fetch-*: 浏览器安全机制，标识请求来源")
    print("  Cache-Control: no-cache 表示不用缓存")
    print("  Upgrade-Insecure-Requests: 1 表示浏览器支持HTTPS")


def demonstrate_header_priority():
    """演示请求头优先级"""
    print("\n" + "=" * 60)
    print("请求头优先级")
    print("=" * 60)

    print("\n【常见头部的优先级】")
    print("  高优先级:")
    print("    - Host（必填）")
    print("    - Content-Type（POST/PUT时必填）")
    print("    - Authorization（认证时必填）")
    print("  ")
    print("  中优先级:")
    print("    - User-Agent（影响返回内容）")
    print("    - Referer（防盗链）")
    print("    - Cookie（维持会话）")
    print("  ")
    print("  低优先级:")
    print("    - Accept-Encoding（压缩）")
    print("    - Accept-Language（语言）")
    print("    - Cache-Control（缓存策略）")


def demonstrate_network_analysis():
    """演示网络分析"""
    print("\n" + "=" * 60)
    print("网络抓包分析工具")
    print("=" * 60)

    print("\n【Chrome DevTools】")
    print("  1. F12打开开发者工具")
    print("  2. Network标签")
    print("  3. 刷新页面查看所有请求")
    print("  4. 点击请求查看详情")
    print("  5. 重点查看:")
    print("    - Headers（请求/响应头）")
    print("    - Payload（POST数据）")
    print("    - Response（响应内容）")
    print("    - Timing（时间消耗）")

    print("\n【Fiddler】")
    print("  1. 抓取所有HTTP/HTTPS请求")
    print("  2. 可以修改请求和响应")
    print("  3. 设置断点调试")
    print("  4.  Composer标签自定义发送请求")

    print("\n【mitmproxy】")
    print("  1. 命令行工具")
    print("  2. 可以写脚本拦截修改请求")
    print("  3. 适合自动化测试")

    print("\n【Charles】")
    print("  1. Mac下常用")
    print("  2. 支持断点、映射、重写")


def demonstrate_analyze_real_request():
    """演示分析真实请求"""
    print("\n" + "=" * 60)
    print("分析真实请求")
    print("=" * 60)

    url = "https://httpbin.org/get"

    print(f"\n【URL】: {url}")

    response = requests.get(url)

    print("\n【请求方法】: GET")
    print("\n【请求头】:")
    for key, value in response.request.headers.items():
        print(f"  {key}: {value}")

    print(f"\n【状态码】: {response.status_code}")
    print("\n【响应头】:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print(f"\n【响应内容预览】:")
    print(f"  {response.text[:300]}...")


if __name__ == "__main__":
    demonstrate_request_headers()
    demonstrate_response_headers()
    demonstrate_custom_headers()
    demonstrate_browsing_headers()
    demonstrate_header_priority()
    demonstrate_network_analysis()
    demonstrate_analyze_real_request()
