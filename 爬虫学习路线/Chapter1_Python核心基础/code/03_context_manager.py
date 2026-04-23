"""
上下文管理器 - 自定义实现

学习目标:
1. 理解上下文管理器的原理（__enter__ / __exit__）
2. 掌握两种实现方式：类实现 vs 装饰器实现
3. 理解爬虫中Session的正确用法

运行方式:
    python code/03_context_manager.py

关键概念:
- __enter__: with块开始时调用，返回值赋给 as 后面的变量
- __exit__: with块结束时调用，无论是否异常都会执行
- @contextmanager: 用装饰器简化上下文管理器实现
"""

from contextlib import contextmanager
import time
import requests
import aiohttp
import asyncio


# ============== 方式1: 类实现 ==============

class Timer:
    """计时器上下文管理器"""

    def __enter__(self):
        self.start = time.time()
        print(f"⏱️  开始计时...")
        return self  # 返回的对象可以在 with 块中使用

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        print(f"⏱️  耗时: {elapsed:.4f} 秒")
        return False  # 返回False表示不吞掉异常，True表示吞掉


class DatabaseConnection:
    """模拟数据库连接"""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None

    def __enter__(self):
        print(f"🔌 连接数据库 {self.host}:{self.port}...")
        self.conn = f"连接对象({self.host})"
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"🔌 关闭数据库连接...")
        self.conn = None
        return False


# ============== 方式2: 装饰器实现 ==============

@contextmanager
def timer_decorator():
    """
    用装饰器实现的计时器

    yield之前的代码相当于 __enter__
    yield之后的代码相当于 __exit__
    """
    start = time.time()
    print(f"⏱️  开始计时...")
    try:
        yield  # 相当于 __enter__ 的返回值
    finally:
        print(f"⏱️  耗时: {time.time() - start:.4f} 秒")


@contextmanager
def managed_connection(host, port):
    """用装饰器实现的连接管理"""
    print(f"🔌 连接数据库 {host}:{port}...")
    conn = f"连接对象({host})"
    try:
        yield conn
    finally:
        print(f"🔌 关闭数据库连接...")


# ============== 爬虫中的用法 ==============

def requests_session_demo():
    """requests Session 的正确用法"""
    print("\n" + "=" * 50)
    print("requests Session 上下文管理器")
    print("=" * 50)

    # ✅ 正确：用with管理，自动关闭
    with requests.Session() as session:
        session.headers.update({"User-Agent": "Mozilla/5.0"})

        response1 = session.get("https://httpbin.org/get")
        response2 = session.get("https://httpbin.org/headers")

        print(f"响应1: {response1.status_code}")
        print(f"响应2: {response2.status_code}")

    # with块结束后，session自动关闭，连接释放


async def aiohttp_session_demo():
    """aiohttp Session 的正确用法"""
    print("\n" + "=" * 50)
    print("aiohttp Session 上下文管理器")
    print("=" * 50)

    # ✅ 正确：用async with管理
    async with aiohttp.ClientSession() as session:
        async with session.get("https://httpbin.org/get") as response:
            data = await response.json()
            print(f"响应: {response.status}")

    # with块结束后，session自动关闭并清理所有连接


def demo_exception_handling():
    """异常处理示例"""
    print("\n" + "=" * 50)
    print("异常处理演示")
    print("=" * 50)

    class SafeResource:
        def __enter__(self):
            print("📦 获取资源...")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            print("📦 释放资源...")
            if exc_type is not None:
                print(f"  ⚠️  捕获到异常: {exc_val}")
                # return True 会吞掉异常，不推荐
            return False

    with SafeResource() as r:
        print("正常使用...")

    print("\n带异常的情况:")
    try:
        with SafeResource() as r:
            print("执行中...")
            raise ValueError("测试异常")
    except ValueError as e:
        print(f"异常被传播出来: {e}")


# ============== 主函数 ==============

def demo_class_style():
    """类实现的上下文管理器"""
    print("=" * 50)
    print("方式1: 类实现")
    print("=" * 50)

    with Timer() as t:
        time.sleep(0.5)
        result = 1 + 1
        print(f"计算结果: {result}")

    with DatabaseConnection("localhost", 3306) as conn:
        print(f"使用 {conn} 执行查询...")

    print()


def demo_decorator_style():
    """装饰器实现的上下文管理器"""
    print("=" * 50)
    print("方式2: 装饰器实现")
    print("=" * 50)

    with timer_decorator():
        time.sleep(0.3)
        print("执行中...")

    with managed_connection("192.168.1.100", 5432) as conn:
        print(f"使用 {conn} 执行查询...")


if __name__ == "__main__":
    demo_class_style()
    demo_decorator_style()
    demo_exception_handling()
    asyncio.run(aiohttp_session_demo())
