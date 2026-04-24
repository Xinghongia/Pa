"""
WebSocket与HTTPS详解

学习目标:
1. 理解HTTPS的加密原理
2. 理解WebSocket与HTTP的区别
3. 掌握WebSocket的工作原理
4. 了解如何在爬虫中处理WebSocket

运行方式:
    python code/04_websocket_https.py
"""

import requests
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def demonstrate_http_vs_https():
    """演示HTTP vs HTTPS"""
    print("=" * 60)
    print("HTTP vs HTTPS")
    print("=" * 60)

    print("\n【HTTP的问题】")
    print("  数据明文传输，谁都能偷看")
    print("  - 账号密码暴露")
    print("  - Cookie暴露（可被劫持）")
    print("  - 数据可被篡改")

    print("\n【HTTPS的解决方案】")
    print("  数据加密传输，只有客户端和服务器能解密")
    print("  - 数据加密，第三方看不到")
    print("  - 数字签名，数据不可篡改")
    print("  - 证书验证，确认服务器身份")


def demonstrate_tls_handshake():
    """演示TLS握手过程"""
    print("\n" + "=" * 60)
    print("TLS握手过程")
    print("=" * 60)

    print("\n【TLS握手流程】")
    print("  客户端                                    服务器")
    print("    │                                          │")
    print("    │ 1. Client Hello                          │")
    print("    │    (支持的加密套件列表)                   │")
    print("    │ ──────────────────────────────────────→ │")
    print("    │                                          │")
    print("    │ 2. Server Hello + Certificate            │")
    print("    │    (选择的加密套件 + 服务器证书)          │")
    print("    │ ←────────────────────────────────────── │")
    print("    │                                          │")
    print("    │ 3. 验证证书                             │")
    print("    │    (检查证书是否有效、域名是否匹配)       │")
    print("    │                                          │")
    print("    │ 4. Pre-Master Secret                     │")
    print("    │    (用公钥加密的会话密钥)                │")
    print("    │ ──────────────────────────────────────→ │")
    print("    │                                          │")
    print("    │ 5. 生成会话密钥                         │")
    print("    │    (双方用算法计算出相同的密钥)           │")
    print("    │                                          │")
    print("    │ 6. 切换到对称加密                       │")
    print("    │    (后续通信都用会话密钥加密)             │")


def demonstrate_ssl_verification():
    """演示SSL证书验证"""
    print("\n" + "=" * 60)
    print("SSL证书验证")
    print("=" * 60)

    print("\n【证书包含的信息】")
    print("  - 域名 (example.com)")
    print("  - 公钥")
    print("  - 颁发机构 (CA)")
    print("  - 有效期")
    print("  - 数字签名")

    print("\n【证书验证步骤】")
    print("  1. 检查证书是否在有效期内")
    print("  2. 检查域名是否匹配")
    print("  3. 检查颁发CA是否可信")
    print("  4. 验证数字签名是否正确")

    print("\n【证书链】")
    print("  根证书 → 中间证书 → 服务器证书")
    print("    ↑")
    print("  操作系统/浏览器内置的可信根证书")

    print("\n【爬虫中忽略证书验证】")
    print("  # 正常情况（验证证书）")
    print("  response = requests.get('https://example.com')")
    print("  ")
    print("  # 测试环境（忽略证书验证）")
    print("  response = requests.get('https://example.com', verify=False)")
    print("  # 注意：生产环境不要用这个！")


def demonstrate_http_vs_websocket():
    """演示HTTP vs WebSocket"""
    print("\n" + "=" * 60)
    print("HTTP vs WebSocket")
    print("=" * 60)

    print("\n【HTTP的请求-响应模式】")
    print("  客户端 ────→ 请求 ────→ 服务器")
    print("  客户端 ←─── ← 响应 ←─── ← 服务器")
    print("  ")
    print("  问题：服务器不能主动推送，只能客户端轮询")

    print("\n【WebSocket的双向长连接】")
    print("  客户端 ↔═══════════════↔ 服务器")
    print("       (建立连接后双向通信)")
    print("  ")
    print("  优势：")
    print("  - 服务器可以主动推送")
    print("  - 建立一次连接，一直用")
    print("  - 延迟低，实时性好")


def demonstrate_websocket_handshake():
    """演示WebSocket握手"""
    print("\n" + "=" * 60)
    print("WebSocket握手过程")
    print("=" * 60)

    print("\n【握手请求】")
    request_headers = {
        'Upgrade': 'websocket',
        'Connection': 'Upgrade',
        'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ==',
        'Sec-WebSocket-Version': '13'
    }
    print("  GET /ws HTTP/1.1")
    print("  Host: example.com")
    print("  Upgrade: websocket")
    print("  Connection: Upgrade")
    print("  Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==")
    print("  Sec-WebSocket-Version: 13")

    print("\n【握手响应】")
    print("  HTTP/1.1 101 Switching Protocols")
    print("  Upgrade: websocket")
    print("  Connection: Upgrade")
    print("  Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=")

    print("\n【关键点】")
    print("  1. 请求头带 Upgrade: websocket")
    print("  2. 服务器返回 101 Switching Protocols")
    print("  3. Sec-WebSocket-Key 是浏览器生成的随机key")
    print("  4. Sec-WebSocket-Accept 是服务器用key计算出的验证")
    print("  5. 握手后协议切换为WebSocket")


def demonstrate_websocket_frame():
    """演示WebSocket数据帧"""
    print("\n" + "=" * 60)
    print("WebSocket数据帧结构")
    print("=" * 60)

    print("\n【帧结构】")
    print("  ┌─────────────┬─────────────┬─────────────┐")
    print("  │  FIN(1bit)  │ Opcode(4bit)│ RSV(3bit)   │")
    print("  ├─────────────┴─────────────┴─────────────┤")
    print("  │ Mask(1bit)     │ Payload len(7bit)      │")
    print("  ├─────────────┴───────────────────────────┤")
    print("  │          Extended payload length       │")
    print("  ├───────────────────────────────────────┤")
    print("  │              Masking key              │")
    print("  ├───────────────────────────────────────┤")
    print("  │               Payload                 │")
    print("  └───────────────────────────────────────┘")

    print("\n【Opcode类型】")
    print("  0x0: Continuation frame (延续帧)")
    print("  0x1: Text frame (文本帧)")
    print("  0x2: Binary frame (二进制帧)")
    print("  0x8: Close frame (关闭帧)")
    print("  0x9: Ping frame (心跳帧)")
    print("  0xA: Pong frame (心跳响应帧)")


def demonstrate_websocket_in_crawler():
    """演示爬虫中处理WebSocket"""
    print("\n" + "=" * 60)
    print("爬虫中处理WebSocket")
    print("=" * 60)

    print("\n【使用websocket-client库】")
    print("""
    import websocket

    def on_message(ws, message):
        print(f'收到消息: {message}')

    def on_error(ws, error):
        print(f'错误: {error}')

    def on_close(ws):
        print('连接关闭')

    ws = websocket.WebSocketApp(
        'wss://example.com/ws',
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
    """)

    print("\n【常见场景】")
    print("  - 实时行情（股票、加密货币）")
    print("  - 在线聊天")
    print("  - 游戏对战")
    print("  - 实时通知")


def demonstrate_https_in_requests():
    """演示requests中的HTTPS处理"""
    print("\n" + "=" * 60)
    print("requests中的HTTPS处理")
    print("=" * 60)

    print("\n【验证HTTPS证书】")
    print("  # 默认验证证书")
    print("  response = requests.get('https://example.com')")
    print("  print(response.status_code)")

    print("\n【忽略证书验证（测试用）】")
    print("  response = requests.get('https://example.com', verify=False)")
    print("  # 会警告，但不报错")

    print("\n【指定证书文件】")
    print("  response = requests.get('https://example.com',")
    print("      cert=('/path/to/client.cert', '/path/to/client.key'))")

    print("\n【使用代理（支持HTTPS）】")
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }
    print(f"  proxies = {proxies}")
    print("  response = requests.get(url, proxies=proxies)")


def demonstrate_real_https_request():
    """演示实际的HTTPS请求"""
    print("\n" + "=" * 60)
    print("实际HTTPS请求演示")
    print("=" * 60)

    print("\n【请求https://httpbin.org/get】")
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)

        print(f"  状态码: {response.status_code}")
        print(f"  协议: HTTPS (TLS加密)")

        if response.url.startswith('https'):
            print(f"  URL: {response.url}")
            print(f"  ✅ 使用了HTTPS加密连接")
        else:
            print(f"  URL: {response.url}")
            print(f"  ⚠️ 未使用HTTPS")

        print(f"\n  响应头中的关键信息:")
        print(f"    Server: {response.headers.get('Server', 'N/A')}")
        print(f"    Content-Type: {response.headers.get('Content-Type', 'N/A')}")

    except Exception as e:
        print(f"  请求失败: {str(e)}")


if __name__ == "__main__":
    demonstrate_http_vs_https()
    demonstrate_tls_handshake()
    demonstrate_ssl_verification()
    demonstrate_http_vs_websocket()
    demonstrate_websocket_handshake()
    demonstrate_websocket_frame()
    demonstrate_websocket_in_crawler()
    demonstrate_https_in_requests()
    demonstrate_real_https_request()
