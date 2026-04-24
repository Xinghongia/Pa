"""
代理与认证机制

学习目标:
1. 理解代理的工作原理
2. 掌握HTTP/HTTPS代理的使用
3. 理解Basic认证和Bearer Token
4. 理解JWT的原理

运行方式:
    python code/03_proxy_auth.py
"""

import requests
import json
import base64
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def demonstrate_proxy():
    """演示代理的工作原理"""
    print("=" * 60)
    print("代理工作原理")
    print("=" * 60)

    print("\n【直连】")
    print("  爬虫 ──────────────→ 服务器")
    print("       (暴露真实IP)")

    print("\n【使用代理】")
    print("  爬虫 ────→ 代理服务器 ────→ 服务器")
    print("            (隐藏真实IP)      (只看到代理IP)")

    print("\n【代理的常见用途】")
    print("  1. 隐藏真实IP，防止被封")
    print("  2. 突破IP访问限制")
    print("  3. 切换不同地区获取内容")
    print("  4. 负载均衡，分散请求压力")


def demonstrate_proxy_setting():
    """演示代理的设置方式"""
    print("\n" + "=" * 60)
    print("代理设置方式")
    print("=" * 60)

    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }

    print("\n【代理格式】")
    print("  http://IP:端口")
    print("  socks5://IP:端口")
    print(f"\n【示例代理】")
    print(f"  {proxies}")

    print("\n【requests中使用代理】")
    print("""
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }
    response = requests.get(url, proxies=proxies)
    """)


def demonstrate_proxy_with_url():
    """演示带用户名密码的代理"""
    print("\n" + "=" * 60)
    print("带认证的代理")
    print("=" * 60)

    proxy_url = "http://username:password@127.0.0.1:7890"

    print("\n【代理URL格式】")
    print(f"  {proxy_url}")

    proxies = {
        'http': proxy_url,
        'https': proxy_url,
    }

    print("\n【requests中使用】")
    print("  proxies = {")
    print("      'http': 'http://username:password@127.0.0.1:7890',")
    print("      'https': 'http://username:password@127.0.0.1:7890',")
    print("  }")


def demonstrate_proxy_headers():
    """演示代理相关的HTTP头"""
    print("\n" + "=" * 60)
    print("代理相关的HTTP头")
    print("=" * 60)

    print("\n【X-Forwarded-For】")
    print("  格式: X-Forwarded-For: client_ip, proxy1_ip, proxy2_ip")
    print("  作用: 告诉服务器真实客户端IP")
    print("  注意: 这是代理添加的，可被伪造")

    print("\n【X-Real-IP】")
    print("  格式: X-Real-IP: client_ip")
    print("  作用: 同上，另一种写法")

    print("\n【Via】")
    print("  格式: Via: 1.1 proxy_name")
    print("  作用: 标记请求经过的代理")


def demonstrate_basic_auth():
    """演示Basic认证"""
    print("\n" + "=" * 60)
    print("Basic认证")
    print("=" * 60)

    print("\n【原理】")
    print("  1. 服务器返回401和WWW-Authenticate头")
    print("  2. 客户端将 username:password 用Base64编码")
    print("  3. 客户端发送 Authorization: Basic <base64>")
    print("  4. 服务器验证")

    print("\n【认证流程】")
    print("  请求: GET /protected HTTP/1.1")
    print("         ")
    print("  响应: HTTP/1.1 401 Unauthorized")
    print("         WWW-Authenticate: Basic realm='Protected'")
    print("         ")
    print("  请求: GET /protected HTTP/1.1")
    print("         Authorization: Basic dXNlcjpwYXNzMTIz")
    print("                      ↑")
    print("         base64('user:pass123')")
    print("         ")
    print("  响应: HTTP/1.1 200 OK")
    print("         内容...")

    print("\n【代码实现】")
    username = "test_user"
    password = "password123"
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()

    print(f"  原始: {credentials}")
    print(f"  Base64: {encoded}")

    headers = {
        'Authorization': f'Basic {encoded}'
    }
    print(f"  请求头: {headers}")


def demonstrate_bearer_token():
    """演示Bearer Token认证"""
    print("\n" + "=" * 60)
    print("Bearer Token认证")
    print("=" * 60)

    print("\n【原理】")
    print("  1. 用户先通过其他方式获取Token（如OAuth2.0）")
    print("  2. 后续请求在 Authorization 头中携带 Token")
    print("  3. 格式: Authorization: Bearer <token>")

    print("\n【OAuth2.0流程】")
    print("  1. 用户点击授权")
    print("  2. 跳转到授权服务器")
    print("  3. 用户授权")
    print("  4. 授权服务器返回Token")
    print("  5. 客户端用Token访问API")

    print("\n【代码实现】")
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjM0NTY3ODkwfQ"

    headers = {
        'Authorization': f'Bearer {token}'
    }
    print(f"  Token: {token}...")
    print(f"  请求头: {headers}")


def demonstrate_jwt():
    """演示JWT"""
    print("\n" + "=" * 60)
    print("JWT (JSON Web Token)")
    print("=" * 60)

    print("\n【JWT结构】")
    print("  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjM0NSwiZXhwIjoxNzA3MDAwMDAwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    print("  ├─────────────────────┤├────────────────────────────┤├─────────────────┤")
    print("         Header               Payload                    Signature")

    print("\n【Header (头部)】")
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, indent=2)
    header_base64 = base64.b64encode(json.dumps(header).encode()).decode()
    print(f"  JSON: {header_json}")
    print(f"  Base64: {header_base64}")

    print("\n【Payload (载荷)】")
    payload = {
        "user_id": 12345,
        "username": "test_user",
        "exp": 1707000000,
        "iat": 1706996400
    }
    payload_json = json.dumps(payload, indent=2)
    payload_base64 = base64.b64encode(json.dumps(payload).encode()).decode().replace('=', '')
    print(f"  JSON: {payload_json}")
    print(f"  Base64: {payload_base64}")

    print("\n【Signature (签名)】")
    print("  签名 = HMAC-SHA256(Header.Base64 + '.' + Payload.Base64, secret_key)")
    print("  作用: 防止数据被篡改")

    print("\n【JWT验证流程】")
    print("  1. 收到Token: header.payload.signature")
    print("  2. 用Secret重新计算签名")
    print("  3. 对比签名是否一致")
    print("  4. 检查exp是否过期")
    print("  5. 验证通过后，从Payload获取用户信息")


def demonstrate_jwt_decode():
    """演示JWT解码"""
    print("\n" + "=" * 60)
    print("JWT解码")
    print("=" * 60)

    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjM0NSwidXNlcm5hbWUiOiJ0ZXN0IiwiZXhwIjoxNzA3MDAwMDAwfQ.abc123signature"

    print("\n【完整的JWT】")
    print(f"  {jwt_token}")

    parts = jwt_token.split('.')
    print(f"\n【分解为三部分】")
    print(f"  Header:   {parts[0]}")
    print(f"  Payload:  {parts[1]}")
    print(f"  Signature: {parts[2]}")

    print(f"\n【解码Header】")
    header_json = base64.b64decode(parts[0] + '==').decode()
    print(f"  {header_json}")

    print(f"\n【解码Payload】")
    payload_json = base64.b64decode(parts[1] + '==').decode()
    print(f"  {payload_json}")

    print("\n【注意】")
    print("  - Header和Payload只是Base64编码，可直接解码")
    print("  - Signature是签名，需要密钥验证")
    print("  - 不能在Payload中存敏感信息！")


def demonstrate_爬虫中认证实战():
    """演示爬虫中常见的认证场景"""
    print("\n" + "=" * 60)
    print("爬虫中认证实战")
    print("=" * 60)

    print("\n【场景1: 带Token的API请求】")
    token = "your_api_token_here"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    print(f"  headers = {headers}")
    print(f"  response = requests.get(url, headers=headers)")

    print("\n【场景2: 带JWT的API请求】")
    print("  # 从登录响应中获取JWT")
    print("  jwt = response.json()['token']")
    print("  # 后续请求带上JWT")
    print("  headers = {'Authorization': f'Bearer {jwt}'}")

    print("\n【场景3: 需要重新登录的情况】")
    print("  if response.status_code == 401:")
    print("      # 重新登录获取新Token")
    print("      login_response = session.post('/api/login', data=credentials)")
    print("      new_token = login_response.json()['token']")
    print("      # 重试原请求")
    print("      response = session.get(url, headers={'Authorization': f'Bearer {new_token}'})")


if __name__ == "__main__":
    demonstrate_proxy()
    demonstrate_proxy_setting()
    demonstrate_proxy_with_url()
    demonstrate_proxy_headers()
    demonstrate_basic_auth()
    demonstrate_bearer_token()
    demonstrate_jwt()
    demonstrate_jwt_decode()
    demonstrate_爬虫中认证实战()
