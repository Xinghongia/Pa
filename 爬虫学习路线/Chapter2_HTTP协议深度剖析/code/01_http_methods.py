"""
HTTP请求与响应结构演示

学习目标:
1. 理解HTTP请求的完整结构
2. 理解HTTP响应的完整结构
3. 掌握常见HTTP方法
4. 理解请求头和响应头的作用

运行方式:
    python code/01_http_methods.py
"""

import requests
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def demonstrate_request_structure():
    """演示HTTP请求的完整结构"""
    print("=" * 60)
    print("HTTP请求结构详解")
    print("=" * 60)

    url = "https://httpbin.org/get"

    response = requests.get(url)

    print("\n【请求URL】")
    print(f"  {url}")

    print("\n【请求方法】")
    print(f"  GET (获取资源)")

    print("\n【请求头 - 实际发送的】")
    for key, value in response.request.headers.items():
        print(f"  {key}: {value}")

    print("\n【响应状态码】")
    print(f"  {response.status_code} {response.reason}")

    print("\n【响应头 - 重要字段】")
    important_headers = [
        'Content-Type', 'Content-Length', 'Date',
        'Server', 'Connection', 'Cache-Control'
    ]
    for key in important_headers:
        value = response.headers.get(key, '(未设置)')
        print(f"  {key}: {value}")

    print("\n【响应体预览】")
    print(f"  类型: {type(response.text)}")
    print(f"  长度: {len(response.text)} 字符")
    print(f"  预览: {response.text[:200]}...")


def demonstrate_post_request():
    """演示POST请求"""
    print("\n" + "=" * 60)
    print("POST请求演示")
    print("=" * 60)

    url = "https://httpbin.org/post"

    data = {
        "username": "test_user",
        "password": "123456",
        "email": "test@example.com"
    }

    headers = {
        "Content-Type": "application/json",
        "X-Custom-Header": "custom_value"
    }

    response = requests.post(url, json=data, headers=headers)

    print("\n【POST请求数据】")
    print(f"  URL: {url}")
    print(f"  数据: {json.dumps(data, ensure_ascii=False)}")
    print(f"  Content-Type: application/json")

    print("\n【请求体 - 实际发送的】")
    print(f"  {response.request.body}")

    print("\n【响应分析】")
    result = response.json()
    print(f"  json()方法: {type(result)}")
    print(f"  是否成功: {result.get('origin', 'N/A')}")


def demonstrate_http_methods():
    """演示不同的HTTP方法"""
    print("\n" + "=" * 60)
    print("HTTP方法对比")
    print("=" * 60)

    base_url = "https://httpbin.org"

    methods = [
        ("GET", "/get"),
        ("POST", "/post"),
        ("PUT", "/put"),
        ("DELETE", "/delete"),
        ("PATCH", "/patch"),
    ]

    for method_name, path in methods:
        url = base_url + path
        print(f"\n【{method_name} {path}】")

        try:
            if method_name == "GET":
                response = requests.get(url, timeout=5)
            elif method_name == "POST":
                response = requests.post(url, data={"key": "value"}, timeout=5)
            elif method_name == "PUT":
                response = requests.put(url, data={"key": "value"}, timeout=5)
            elif method_name == "DELETE":
                response = requests.delete(url, timeout=5)
            elif method_name == "PATCH":
                response = requests.patch(url, data={"key": "value"}, timeout=5)

            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 成功")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)[:50]}")


def demonstrate_headers():
    """演示请求头的设置和作用"""
    print("\n" + "=" * 60)
    print("请求头的作用")
    print("=" * 60)

    url = "https://httpbin.org/headers"

    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com",
        "X-Custom-Header": "CustomValue"
    }

    response = requests.get(url, headers=custom_headers)

    print("\n【发送的请求头】")
    sent_headers = response.json().get('headers', {})
    for key, value in sent_headers.items():
        print(f"  {key}: {value}")

    print("\n【User-Agent的作用】")
    print("  - 告诉服务器你是哪种浏览器")
    print("  - 有些网站根据User-Agent返回不同页面")
    print("  - 爬虫常通过修改User-Agent来伪装")

    print("\n【Referer的作用】")
    print("  - 告诉服务器你从哪个页面来的")
    print("  - 用于防盗链（图片、视频常用）")
    print("  - 某些API需要正确的Referer才能访问")


def demonstrate_response_headers():
    """演示响应头的各种信息"""
    print("\n" + "=" * 60)
    print("响应头的各种信息")
    print("=" * 60)

    url = "https://httpbin.org/get"
    response = requests.get(url)

    print("\n【常见响应头】")
    headers_info = [
        ("Content-Type", "内容类型，如text/html、application/json"),
        ("Content-Length", "内容长度（字节）"),
        ("Server", "服务器类型"),
        ("Date", "响应时间"),
        ("Connection", "连接状态，keep-alive表示复用"),
        ("Cache-Control", "缓存控制，max-age=3600表示缓存1小时"),
    ]

    for header, description in headers_info:
        value = response.headers.get(header, '(无)')
        print(f"  {header}: {value}")
        print(f"      说明: {description}")

    print("\n【Cookie相关响应头】")
    print("  Set-Cookie: 服务器设置Cookie")
    print("  服务器通过这个头告诉浏览器设置Cookie")

    print("\n【重定向相关响应头】")
    print("  Location: 重定向的目标URL（配合3xx状态码）")
    print("  301: 永久重定向")
    print("  302: 临时重定向")


def demonstrate_status_codes():
    """演示常见状态码"""
    print("\n" + "=" * 60)
    print("HTTP状态码详解")
    print("=" * 60)

    status_codes = {
        200: ("OK", "请求成功，服务器返回预期内容"),
        201: ("Created", "资源创建成功"),
        204: ("No Content", "成功但无返回内容"),
        301: ("Moved Permanently", "永久重定向"),
        302: ("Found", "临时重定向"),
        304: ("Not Modified", "使用缓存"),
        400: ("Bad Request", "请求格式错误"),
        401: ("Unauthorized", "需要认证"),
        403: ("Forbidden", "禁止访问"),
        404: ("Not Found", "资源不存在"),
        429: ("Too Many Requests", "请求太频繁，被限流"),
        500: ("Internal Server Error", "服务器内部错误"),
        502: ("Bad Gateway", "网关错误"),
        503: ("Service Unavailable", "服务不可用"),
    }

    print("\n【2xx 成功】")
    for code, (text, desc) in status_codes.items():
        if 200 <= code < 300:
            print(f"  {code} {text}: {desc}")

    print("\n【3xx 重定向】")
    for code, (text, desc) in status_codes.items():
        if 300 <= code < 400:
            print(f"  {code} {text}: {desc}")

    print("\n【4xx 客户端错误】")
    for code, (text, desc) in status_codes.items():
        if 400 <= code < 500:
            print(f"  {code} {text}: {desc}")

    print("\n【5xx 服务器错误】")
    for code, (text, desc) in status_codes.items():
        if 500 <= code < 600:
            print(f"  {code} {text}: {desc}")

    print("\n【爬虫中常见的状态码处理】")
    print("  200: 成功解析数据")
    print("  301/302: 处理重定向")
    print("  404: 资源不存在，跳过")
    print("  403: 被禁止，可能需要换IP或调整请求头")
    print("  429: 被限流，增加请求间隔")
    print("  5xx: 服务器问题，等待后重试")


if __name__ == "__main__":
    demonstrate_request_structure()
    demonstrate_post_request()
    demonstrate_http_methods()
    demonstrate_headers()
    demonstrate_response_headers()
    demonstrate_status_codes()
