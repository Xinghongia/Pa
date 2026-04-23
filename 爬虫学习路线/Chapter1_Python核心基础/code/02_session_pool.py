"""
Session连接池详解

学习目标:
1. 理解requests.Session的连接池机制
2. 掌握HTTPAdapter配置连接池参数
3. 理解连接复用的原理

运行方式:
    python code/02_session_pool.py

关键概念:
- Session: 维护TCP连接池，复用连接
- HTTPAdapter: 精细控制不同域名的连接策略
- Retry: 重试策略配置
- pool_maxsize: 连接池大小
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import concurrent.futures


def create_session_with_pool():
    """
    创建一个配置好连接池的Session

    核心配置:
    - pool_connections: 维护多少个连接池（不同域名=不同池）
    - pool_maxsize: 每个池的最大连接数
    """
    session = requests.Session()

    # 配置重试策略
    retry_strategy = Retry(
        total=3,                   # 总重试次数
        read=3,                     # 读取重试
        connect=3,                  # 连接重试
        backoff_factor=0.5,         # 重试间隔: 0.5s, 1s, 2s（指数退避）
        status_forcelist=[500, 502, 503, 504],  # 只有这些状态码才重试
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )

    # 创建适配器（这是关键！）
    adapter = HTTPAdapter(
        pool_connections=10,   # 最多维护10个不同域名的连接池
        pool_maxsize=20,       # 每个池最多20个连接
        max_retries=retry_strategy
    )

    # 挂载到Session
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # 设置默认请求头
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",  # 保持连接
    })

    return session


def test_connection_reuse():
    """测试连接复用"""
    print("=" * 50)
    print("测试1: 连续请求同一域名（应该复用连接）")
    print("=" * 50)

    session = create_session_with_pool()
    url = "https://httpbin.org/get"

    times = []
    for i in range(5):
        start = time.time()
        response = session.get(url)
        elapsed = time.time() - start
        times.append(elapsed)

        connection = response.headers.get("connection", "N/A")
        print(f"请求{i+1}: 状态={response.status_code}, "
              f"耗时={elapsed:.3f}s, "
              f"连接={connection}")

    print(f"\n📊 第一个请求较慢（建立连接）")
    print(f"📊 后4个请求较快（复用连接）")


def test_different_domains():
    """测试不同域名的连接池"""
    print("\n" + "=" * 50)
    print("测试2: 请求不同域名（不同连接池）")
    print("=" * 50)

    session = create_session_with_pool()
    urls = [
        "https://httpbin.org/get",
        "https://api.github.com/",
        "https://httpbin.org/ip",
    ]

    for url in urls:
        start = time.time()
        response = session.get(url, timeout=5)
        elapsed = time.time() - start
        print(f"  {url}")
        print(f"    状态={response.status_code}, 耗时={elapsed:.3f}s")


def demonstrate_pool_limit():
    """
    演示连接池限制

    场景: pool_maxsize=2，但并发请求3个
    """
    print("\n" + "=" * 50)
    print("测试3: 连接池限制（pool_maxsize=2）")
    print("=" * 50)

    session = requests.Session()
    adapter = HTTPAdapter(pool_maxsize=2)
    session.mount("https://httpbin.org", adapter)

    def fetch(delay):
        start = time.time()
        r = requests.get(f"https://httpbin.org/delay/{delay}")
        return time.time() - start

    # 并发3个请求，但池只能容纳2个
    # 第3个请求需要等待池中有空闲连接
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch, 1) for _ in range(3)]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            print(f"请求{i+1} 完成，耗时: {future.result():.3f}s")


if __name__ == "__main__":
    test_connection_reuse()
    test_different_domains()
    demonstrate_pool_limit()
