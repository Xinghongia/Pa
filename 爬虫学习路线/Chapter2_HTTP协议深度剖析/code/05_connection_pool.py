"""
TCP连接与连接池演示

学习目标:
1. 理解TCP三次握手四次挥手
2. 理解连接池的作用和原理
3. 掌握requests中的连接池配置
4. 理解连接复用的性能优势

运行方式:
    python code/05_connection_pool.py
"""

import requests
import time
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def demonstrate_connection_pool_concept():
    """演示连接池的概念"""
    print("=" * 60)
    print("连接池概念")
    print("=" * 60)

    print("\n【不使用连接池】")
    print("  请求1: 握手 → 传输 → 挥手")
    print("  请求2: 握手 → 传输 → 挥手")
    print("  请求3: 握手 → 传输 → 挥手")
    print("  问题: 每次都要握手+挥手，很慢！")

    print("\n【使用连接池】")
    print("  握手 → [请求1: 传输] → [请求2: 传输] → [请求3: 传输] → 挥手")
    print("                    连接一直保持着")
    print("  优势: 省去多次握手+挥手，大幅提升性能")


def demonstrate_keep_alive():
    """演示HTTP Keep-Alive"""
    print("\n" + "=" * 60)
    print("HTTP Keep-Alive")
    print("=" * 60)

    print("\n【Keep-Alive原理】")
    print("  HTTP/1.0: 一次请求-响应后连接就断开")
    print("  HTTP/1.1: 默认开启Keep-Alive，一次连接可以处理多个请求")

    print("\n【响应头中的Keep-Alive】")
    print("  Connection: keep-alive")
    print("  Keep-Alive: timeout=5, max=1000")
    print("    - timeout=5: 保持连接5秒")
    print("    - max=1000: 最多处理1000个请求")


def demonstrate_session_connection_pool():
    """演示Session的连接池"""
    print("\n" + "=" * 60)
    print("Session的连接池")
    print("=" * 60)

    print("\n【创建Session】")
    session = requests.Session()

    print(f"  Session对象: {session}")
    print(f"  Session的适配器: {session.adapters}")
    print(f"  Session的连接池配置: 默认 urllib3.PoolManager")

    print("\n【查看默认连接池大小】")
    print("  每个host一个连接池")
    print("  默认大小: 10个连接")


def demonstrate_connection_pool_config():
    """演示连接池配置"""
    print("\n" + "=" * 60)
    print("连接池配置")
    print("=" * 60)

    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    print("\n【自定义连接池大小】")
    print("""
    session = requests.Session()

    # 为HTTP配置连接池
    adapter = HTTPAdapter(
        pool_connections=10,  # 最多10个连接池
        pool_maxsize=20       # 每个连接池最多20个连接
    )
    session.mount('http://', adapter)

    # 为HTTPS配置连接池
    session.mount('https://', adapter)
    """)

    session = requests.Session()

    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    print(f"  已配置连接池: pool_connections=10, pool_maxsize=20")


def demonstrate_connection_reuse():
    """演示连接复用"""
    print("\n" + "=" * 60)
    print("连接复用性能对比")
    print("=" * 60)

    url = "https://httpbin.org/get"
    iterations = 5

    print("\n【不使用Session（不复用连接）】")
    start = time.time()
    for i in range(iterations):
        requests.get(url, timeout=5)
        print(f"  请求 {i+1} 完成")
    no_session_time = time.time() - start
    print(f"  总耗时: {no_session_time:.2f}秒")

    print("\n【使用Session（复用连接）】")
    session = requests.Session()
    start = time.time()
    for i in range(iterations):
        session.get(url, timeout=5)
        print(f"  请求 {i+1} 完成")
    session_time = time.time() - start
    print(f"  总耗时: {session_time:.2f}秒")

    improvement = (no_session_time - session_time) / no_session_time * 100
    print(f"\n【性能提升】: {improvement:.1f}%")


def demonstrate_pool_manager():
    """演示PoolManager"""
    print("\n" + "=" * 60)
    print("PoolManager详解")
    print("=" * 60)

    from urllib3 import PoolManager

    print("\n【PoolManager作用】")
    print("  - 管理多个连接池")
    print("  - 按host区分连接池")
    print("  - 自动复用连接")

    print("\n【创建PoolManager】")
    pm = PoolManager(num_pools=10, maxsize=20)
    print(f"  PoolManager: {pm}")
    print(f"  pool数量: {num_pools if hasattr(pm, 'pools') else '按需创建'}")

    print("\n【使用PoolManager请求】")
    print("  response = pm.request('GET', 'https://httpbin.org/get')")


def demonstrate_connection_limit():
    """演示连接数限制"""
    print("\n" + "=" * 60)
    print("连接数限制")
    print("=" * 60)

    print("\n【浏览器对单域名连接数限制】")
    print("  - HTTP/1.1: 通常最多6个并发连接")
    print("  - HTTP/2: 只有1个连接（多路复用）")
    print("  - 超出限制的请求会排队等待")

    print("\n【爬虫中的连接数设置】")
    print("  建议:")
    print("  - 单域名并发控制在5-10个")
    print("  - 总并发控制在20-30个")
    print("  - 避免超出服务器承受范围")


def demonstrate_tcp_connection_details():
    """演示TCP连接细节"""
    print("\n" + "=" * 60)
    print("TCP连接细节")
    print("=" * 60)

    print("\n【TCP三次握手】")
    print("  1. 客户端发送SYN (seq=x)")
    print("  2. 服务器返回SYN+ACK (seq=y, ack=x+1)")
    print("  3. 客户端发送ACK (ack=y+1)")
    print("  → 连接建立成功")

    print("\n【数据传输】")
    print("  - 双方可以双向传输数据")
    print("  - 每个数据包都有序号")
    print("  - 收到数据包要回复ACK")

    print("\n【TCP四次挥手】")
    print("  1. 主动方发送FIN (我要关闭)")
    print("  2. 被动方回复ACK (收到，等我发完)")
    print("  3. 被动方发送FIN (我也发完了)")
    print("  4. 主动方回复ACK (确认关闭)")
    print("  → 连接断开")


def demonstrate_practical_connection_pool():
    """演示实际的连接池使用"""
    print("\n" + "=" * 60)
    print("实际连接池使用")
    print("=" * 60)

    from requests.adapters import HTTPAdapter

    print("\n【完整的连接池配置】")
    print("""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    def create_session():
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        # 配置适配器（连接池）
        adapter = HTTPAdapter(
            pool_connections=10,      # 连接池数量
            pool_maxsize=20,          # 每个池连接数
            max_retries=retry_strategy
        )

        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    # 使用
    session = create_session()
    response = session.get('https://example.com')
    """)

    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=retry_strategy
    )

    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    print("  ✅ 连接池配置完成")


if __name__ == "__main__":
    demonstrate_connection_pool_concept()
    demonstrate_keep_alive()
    demonstrate_session_connection_pool()
    demonstrate_connection_pool_config()
    demonstrate_connection_reuse()
    demonstrate_pool_manager()
    demonstrate_connection_limit()
    demonstrate_tcp_connection_details()
    demonstrate_practical_connection_pool()
