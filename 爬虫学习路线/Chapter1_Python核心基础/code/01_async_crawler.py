"""
异步爬虫基础 - 最小可行示例

学习目标:
1. 理解 async/await 语法
2. 理解 aiohttp 基本用法
3. 看到异步带来的效率提升

运行方式:
    python code/01_async_crawler.py

关键概念:
- async def: 定义协程函数
- await: 等待IO操作时让出CPU
- asyncio.gather: 并发执行多个协程
- aiohttp.ClientSession: 异步HTTP会话
"""

import asyncio
import aiohttp
import time


async def fetch(session, url):
    """
    单个URL的异步请求

    协程函数：可以暂停和恢复的函数
    当执行到 await 时，CPU会去执行其他协程
    """
    async with session.get(url) as response:
        await response.read()
        return url, response.status


async def main():
    """
    主协程 - 所有协程的入口
    """
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    start = time.time()

    # 创建ClientSession（相当于requests.Session，但支持异步）
    async with aiohttp.ClientSession() as session:
        # 创建任务列表（注意：这里还没有执行！）
        tasks = [fetch(session, url) for url in urls]

        # asyncio.gather 并发执行所有任务
        # 所有请求同时发起，谁先完成谁先返回
        results = await asyncio.gather(*tasks)

    elapsed = time.time() - start

    print(f"\n✅ 完成 {len(results)} 个请求")
    print(f"⏱️  总耗时: {elapsed:.2f} 秒")
    print(f"📊 平均每个请求: {elapsed/len(results):.2f} 秒")

    for url, status in results:
        print(f"  {'✅' if status == 200 else '❌'} {url} -> {status}")


if __name__ == "__main__":
    # asyncio.run 是Python 3.7+的标准写法
    # 相当于旧的: loop = asyncio.get_event_loop(); loop.run_until_complete(main())
    asyncio.run(main())
