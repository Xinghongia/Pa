"""
综合实战: 高性能异步爬虫框架

整合本章所有知识点:
1. 异步并发 (asyncio)
2. 连接池 (aiohttp)
3. 上下文管理器
4. 生成器
5. 错误处理和重试

运行方式:
    python code/06_complete_framework.py

学习目标:
1. 理解一个完整爬虫框架的架构设计
2. 掌握各种错误处理和重试策略
3. 理解信号量如何控制并发
"""

import asyncio
import aiohttp
from aiohttp import ClientError, ServerTimeoutError
import time
import logging
from typing import List, Dict, Generator, Optional, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CrawlerConfig:
    """爬虫配置"""
    max_concurrent: int = 10          # 最大并发数
    max_retries: int = 3              # 最大重试次数
    timeout: int = 30                 # 超时时间（秒）
    retry_delay: float = 1.0          # 重试间隔（秒）
    backoff_factor: float = 2.0       # 退避系数


class AsyncCrawler:
    """
    高性能异步爬虫框架

    特性:
    - 异步并发请求
    - 连接池管理
    - 自动重试（指数退避）
    - 错误处理和日志
    - 进度跟踪
    - 上下文管理器支持
    """

    def __init__(self, config: Optional[CrawlerConfig] = None):
        self.config = config or CrawlerConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore: Optional[asyncio.Semaphore] = None
        self.stats = {
            "success": 0,
            "failed": 0,
            "retries": 0,
        }

    @asynccontextmanager
    async def session_context(self):
        """
        Session上下文管理器

        使用 @asynccontextmanager 装饰器
        简化异步上下文管理器的实现
        """
        connector = aiohttp.TCPConnector(
            limit=self.config.max_concurrent * 2,
            limit_per_host=self.config.max_concurrent,
            ttl_dns_cache=300,
        )

        timeout = aiohttp.ClientTimeout(total=self.config.timeout)

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            self.session = session
            yield session

    async def fetch_with_retry(self, url: str) -> Dict:
        """
        带重试的请求

        指数退避策略:
        第1次失败: 等1秒后重试
        第2次失败: 等2秒后重试
        第3次失败: 等4秒后重试
        """
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                async with self.session.get(url) as response:
                    content = await response.read()

                    if response.status == 200:
                        self.stats["success"] += 1
                        return {
                            "url": url,
                            "status": response.status,
                            "content": content,
                            "success": True,
                        }
                    else:
                        self.stats["failed"] += 1
                        return {
                            "url": url,
                            "status": response.status,
                            "error": f"HTTP {response.status}",
                            "success": False,
                        }

            except ServerTimeoutError:
                last_error = "超时"
                self.stats["retries"] += 1
                logger.warning(f"⏰ 超时: {url} (第{attempt+1}次)")

            except ClientError as e:
                last_error = str(e)
                self.stats["retries"] += 1
                logger.warning(f"⚠️  请求错误: {url} - {e} (第{attempt+1}次)")

            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ 未知错误: {url} - {e}")
                break

            # 指数退避等待
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (self.config.backoff_factor ** attempt)
                await asyncio.sleep(delay)

        self.stats["failed"] += 1
        return {
            "url": url,
            "status": 0,
            "error": last_error,
            "success": False,
        }

    async def fetch_one(self, url: str) -> Dict:
        """获取单个URL（受信号量控制）"""
        async with self.semaphore:
            return await self.fetch_with_retry(url)

    async def crawl(
        self,
        urls: List[str],
        progress_callback: Optional[Callable] = None
    ) -> Generator[Dict, None, None]:
        """
        爬取多个URL

        使用 asyncio.as_completed 按完成顺序返回结果
        配合信号量控制并发数
        """
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async with self.session_context():
            tasks = [self.fetch_one(url) for url in urls]

            for i, coro in enumerate(asyncio.as_completed(tasks)):
                result = await coro

                if progress_callback:
                    progress_callback(i + 1, len(urls), result)

                yield result

    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.stats["success"] + self.stats["failed"]
        return {
            **self.stats,
            "total": total,
            "success_rate": f"{self.stats['success']/total*100:.1f}%" if total > 0 else "0%",
        }


async def main():
    """主函数 - 测试爬虫框架"""
    print("=" * 50)
    print("高性能异步爬虫框架演示")
    print("=" * 50)

    config = CrawlerConfig(
        max_concurrent=10,
        max_retries=3,
        timeout=30
    )

    crawler = AsyncCrawler(config)

    test_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/ip",
        "https://httpbin.org/headers",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/json",
    ]

    print(f"\n📋 待爬取URL数量: {len(test_urls)}")
    print(f"⚡ 最大并发数: {config.max_concurrent}")
    print(f"🔄 最大重试次数: {config.max_retries}")
    print("-" * 50)

    def progress(current, total, result):
        status = "✅" if result["success"] else "❌"
        print(f"\r  进度: {current}/{total} - {status} {result['url'][:40]}", end="")

    start_time = time.time()
    results = []

    async for result in crawler.crawl(test_urls, progress_callback=progress):
        results.append(result)

    elapsed = time.time() - start_time

    print("\n\n" + "=" * 50)
    print("📊 爬虫执行报告")
    print("=" * 50)

    stats = crawler.get_stats()
    print(f"✅ 成功: {stats['success']}")
    print(f"❌ 失败: {stats['failed']}")
    print(f"🔄 重试次数: {stats['retries']}")
    print(f"📈 成功率: {stats['success_rate']}")
    print(f"⏱️  总耗时: {elapsed:.2f} 秒")
    print(f"📊 平均每URL: {elapsed/len(test_urls):.2f} 秒")
    print(f"🚀 吞吐量: {len(test_urls)/elapsed:.2f} URL/秒")


if __name__ == "__main__":
    asyncio.run(main())
