"""
Cookie与Session管理

学习目标:
1. 理解Cookie的工作原理
2. 掌握Session的使用方法
3. 理解Cookie和Session的区别
4. 学会在爬虫中处理Cookie

运行方式:
    python code/02_cookie_session.py
"""

import requests
import http.cookiejar
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def demonstrate_cookie_storage():
    """演示Cookie的存储方式"""
    print("=" * 60)
    print("Cookie存储方式")
    print("=" * 60)

    url = "https://httpbin.org/cookies/set/test_cookie/hello_world"

    print("\n【访问设置Cookie的URL】")
    print(f"  URL: {url}")

    response = requests.get(url)

    print("\n【响应头中的Set-Cookie】")
    for key, value in response.headers.items():
        if 'cookie' in key.lower() or 'set-cookie' in key.lower():
            print(f"  {key}: {value}")

    print("\n【响应中的Cookie数据】")
    cookies = response.cookies
    print(f"  cookies对象: {cookies}")
    print(f"  获取指定Cookie: {cookies.get('test_cookie')}")

    print("\n【Cookie转字典】")
    cookie_dict = requests.utils.dict_from_cookiejar(cookies)
    print(f"  {cookie_dict}")


def demonstrate_session_cookie_persistence():
    """演示Session保持Cookie"""
    print("\n" + "=" * 60)
    print("Session自动保持Cookie")
    print("=" * 60)

    url = "https://httpbin.org/cookies/set/session_id/abc123xyz"

    print("\n【创建Session】")
    session = requests.Session()
    print(f"  Session对象: {session}")
    print(f"  Session的cookies（初始）: {session.cookies}")

    print("\n【第一次请求 - 设置Cookie】")
    response1 = session.get(url)
    print(f"  请求URL: {url}")
    print(f"  Session的cookies（请求后）: {dict(session.cookies)}")

    print("\n【第二次请求 - 自动带上Cookie】")
    response2 = session.get("https://httpbin.org/cookies")
    print(f"  请求URL: https://httpbin.org/cookies")
    print(f"  响应内容: {response2.json()}")


def demonstrate_cookie_attributes():
    """演示Cookie的各种属性"""
    print("\n" + "=" * 60)
    print("Cookie属性详解")
    print("=" * 60)

    url = "https://httpbin.org/headers"

    session = requests.Session()

    custom_cookies = {
        'user': 'test_user',
        'token': 'abc123',
        'preference': 'dark_mode'
    }

    print("\n【设置自定义Cookie】")
    print(f"  cookies: {custom_cookies}")

    response = requests.get(url, cookies=custom_cookies)

    print("\n【验证Cookie是否发送】")
    headers = response.json().get('headers', {})
    print(f"  请求头中的Cookie或User-Agent包含Cookie信息")


def demonstrate_cookiejar():
    """演示CookieJar的更多操作"""
    print("\n" + "=" * 60)
    print("CookieJar操作")
    print("=" * 60)

    url = "https://httpbin.org/cookies"

    session = requests.Session()

    response = session.get(url)
    cookies = session.cookies

    print("\n【CookieJar基本操作】")
    print(f"  获取所有Cookie: {dict(cookies)}")
    print(f"  获取指定Cookie: {cookies.get('session_id')}")
    print(f"  Cookie数量: {len(cookies)}")

    print("\n【遍历Cookie】")
    for cookie in cookies:
        print(f"  名称: {cookie.name}, 值: {cookie.value}")
        print(f"    域名: {cookie.domain}, 路径: {cookie.path}")
        print(f"    过期: {cookie.expires}, 安全: {cookie.secure}")


def demonstrate_cookie_persistence_to_file():
    """演示Cookie持久化到文件"""
    print("\n" + "=" * 60)
    print("Cookie持久化")
    print("=" * 60)

    session = requests.Session()

    url = "https://httpbin.org/cookies/set/persistent/yes"
    session.get(url)

    print("\n【内存中的Cookie】")
    print(f"  {dict(session.cookies)}")

    cookie_file = "cookies.txt"

    print(f"\n【保存Cookie到文件】")
    import os
    with open(cookie_file, 'w', encoding='utf-8') as f:
        for cookie in session.cookies:
            f.write(f"{cookie.name}\t{cookie.value}\t{cookie.domain}\t{cookie.path}\n")
    print(f"  已保存到: {cookie_file}")

    print(f"\n【读取Cookie文件内容】")
    with open(cookie_file, 'r', encoding='utf-8') as f:
        print(f"  {f.read()}")


def demonstrate_cookie_vs_session():
    """演示Cookie和Session的区别"""
    print("\n" + "=" * 60)
    print("Cookie vs Session")
    print("=" * 60)

    print("\n【Cookie的工作方式】")
    print("  1. 服务器在响应头设置Cookie")
    print("  2. 浏览器自动保存Cookie")
    print("  3. 后续请求自动带上Cookie")
    print("  4. 所有数据存在客户端")

    print("\n【Session的工作方式】")
    print("  1. 服务器创建Session，存储用户数据")
    print("  2. 只把SessionID通过Cookie发给客户端")
    print("  3. 后续请求通过SessionID找到对应数据")
    print("  4. 用户数据存在服务器端")

    print("\n【对比】")
    print("  +----------------+----------------------------+")
    print("  |     属性       |          说明              |")
    print("  +----------------+----------------------------+")
    print("  | 存储位置       | Cookie在客户端，Session在服务器端 |")
    print("  | 安全性         | Session更安全              |")
    print("  | 存储容量       | Session容量更大            |")
    print("  | 传输           | Cookie随请求发送，Session不传输 |")
    print("  | 依赖           | Cookie依赖浏览器，Session依赖服务器 |")
    print("  +----------------+----------------------------+")


def demonstrate_login_flow():
    """演示登录流程中的Cookie"""
    print("\n" + "=" * 60)
    print("登录流程中的Cookie")
    print("=" * 60)

    session = requests.Session()

    print("\n【步骤1: 查看登录前的Cookie】")
    response = session.get("https://httpbin.org/cookies")
    print(f"  登录前Cookie: {dict(session.cookies)}")

    print("\n【步骤2: 模拟登录（设置Cookie）】")
    login_url = "https://httpbin.org/cookies/set/token/abc123 session/user001"
    session.get(login_url)
    print(f"  登录后Cookie: {dict(session.cookies)}")

    print("\n【步骤3: 访问受保护的页面】")
    protected_url = "https://httpbin.org/cookies"
    response = session.get(protected_url)
    print(f"  Cookie自动带上: {response.json()}")

    print("\n【步骤4: 登出（清除Cookie）】")
    session.cookies.clear()
    print(f"  登出后Cookie: {dict(session.cookies)}")


def demonstrate_common_problems():
    """演示爬虫中常见的Cookie问题"""
    print("\n" + "=" * 60)
    print("爬虫中Cookie常见问题")
    print("=" * 60)

    print("\n【问题1: Cookie过期】")
    print("  现象: 爬虫运行一段时间后无法获取数据")
    print("  原因: 服务器设置的Cookie有有效期")
    print("  解决: 检测到401/403时重新登录获取Cookie")

    print("\n【问题2: Cookie被检测】")
    print("  现象: 请求被拒绝，返回403或空数据")
    print("  原因: 网站通过Cookie中的指纹检测爬虫")
    print("  解决: 使用Session保持Cookie，添加合理的指纹信息")

    print("\n【问题3: 多账号切换】")
    print("  现象: 需要同时爬取多个账号的数据")
    print("  原因: 每个账号有独立的Cookie")
    print("  解决: 为每个账号创建独立的Session")

    print("\n【问题4: Cookie跨域】")
    print("  现象: 某些请求Cookie带不上")
    print("  原因: Cookie有Domain和Path限制")
    print("  解决: 确保请求URL在Cookie允许的范围内")


if __name__ == "__main__":
    demonstrate_cookie_storage()
    demonstrate_session_cookie_persistence()
    demonstrate_cookie_attributes()
    demonstrate_cookiejar()
    demonstrate_cookie_persistence_to_file()
    demonstrate_cookie_vs_session()
    demonstrate_login_flow()
    demonstrate_common_problems()

    import os
    try:
        os.remove("cookies.txt")
    except:
        pass
