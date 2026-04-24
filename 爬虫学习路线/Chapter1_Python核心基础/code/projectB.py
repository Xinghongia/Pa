"""
数据处理流水线 - 完整实现

功能说明：
1. 使用生成器模式处理数据，内存占用极小
2. 多阶段处理：URL生成 → 数据爬取 → 数据清洗 → 数据统计
3. 实时监控内存占用和处理速度
4. 可随时中断和恢复

使用方法：
1. 确保已安装依赖：pip install psutil
2. 运行：python projectB.py
3. 观察控制台输出的进度和统计信息

核心原理：
- 生成器（yield）：惰性求值，不预先计算所有数据
- 流水线模式：每个阶段独立，数据逐个传递
- 内存监控：使用 psutil 实时跟踪内存占用

合规提醒：
- 本项目为学习用途，模拟数据处理流程
- 实际应用中请遵守相关法律法规
"""

import time
import random
import hashlib
import sys
from typing import Generator, List, Dict, Optional
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class DataPipeline:
    """数据处理流水线"""

    def __init__(self):
        self.stats = {
            "generated": 0,
            "fetched": 0,
            "cleaned": 0,
            "saved": 0
        }
        # 模拟商品分类
        self.categories = ["electronics", "clothing", "books", "home", "sports"]
        # 模拟数据状态
        self.status_options = ["active", "inactive", "pending"]

    def url_generator(self, total: int) -> Generator[str, None, None]:
        """
        URL生成器 - 惰性生成URL

        每次 yield 一个URL，不一次性生成所有URL
        这样即使total=1000000，内存也只占用很少

        Args:
            total: 需要生成的URL总数

        Yields:
            str: 商品API的URL
        """
        for i in range(total):
            # 模拟商品API的URL格式
            category = self.categories[i % len(self.categories)]
            url = f"https://api.example.com/items/{category}/{i}"
            yield url
            self.stats["generated"] += 1

    def data_fetcher(self, urls: Generator) -> Generator[Dict, None, None]:
        """
        数据获取器 - 模拟从URL获取数据

        实际项目中，这里会用 requests 或 aiohttp 请求真实URL
        本项目模拟返回商品数据

        Args:
            urls: URL生成器

        Yields:
            Dict: 商品原始数据
        """
        for url in urls:
            # 模拟网络请求延迟（实际项目中这里是 requests.get(url)）
            # time.sleep(random.uniform(0.001, 0.005))  # 模拟延迟，测试时可注释

            # 从URL中提取信息
            parts = url.split('/')
            category = parts[-2]
            item_id = int(parts[-1])
 
            # 模拟返回商品数据
            data = {
                "id": item_id,
                "url": url,
                "category": category,
                "name": f"商品_{item_id}",
                "price": round(random.uniform(10, 1000), 2),
                "rating": round(random.uniform(1, 5), 1),
                "sales": random.randint(0, 10000),
                "status": random.choice(self.status_options),
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "raw_data": True  # 标记为原始数据
            }

            yield data
            self.stats["fetched"] += 1

    def data_cleaner(self, raw_data: Generator) -> Generator[Dict, None, None]:
        """
        数据清洗器 - 清洗和格式化数据

        清洗任务：
        1. 过滤无效数据（状态为inactive的商品）
        2. 格式化字段（价格保留2位小数、添加数据哈希）
        3. 补充元数据（清洗时间、数据质量评分）

        Args:
            raw_data: 原始数据生成器

        Yields:
            Dict: 清洗后的商品数据
        """
        for item in raw_data:
            # 1. 过滤无效数据
            if item.get("status") == "inactive":
                continue  # 跳过无效数据

            # 2. 格式化字段
            item["price"] = round(item["price"], 2)  # 价格保留2位小数
            item["rating"] = min(5.0, max(1.0, item["rating"]))  # 评分限制在1-5

            # 3. 补充元数据
            item["cleaned_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item["data_hash"] = hashlib.md5(
                f"{item['id']}_{item['price']}_{item['name']}".encode()
            ).hexdigest()[:8]

            # 计算数据质量评分（模拟）
            quality_score = 0
            if item["price"] > 0:
                quality_score += 0.3
            if item["rating"] >= 3:
                quality_score += 0.3
            if item["sales"] > 100:
                quality_score += 0.4
            item["quality_score"] = round(quality_score, 2)

            # 移除原始数据标记
            item.pop("raw_data", None)

            yield item
            self.stats["cleaned"] += 1

    def stats_collector(self, data: Generator) -> Generator[Dict, None, None]:
        """
        统计收集器 - 收集数据并添加统计信息

        Args:
            data: 清洗后的数据生成器

        Yields:
            Dict: 带统计信息的商品数据
        """
        # 分类统计
        category_stats = {}
        price_total = 0
        price_count = 0

        for item in data:
            # 分类统计
            category = item["category"]
            if category not in category_stats:
                category_stats[category] = {"count": 0, "total_sales": 0}
            category_stats[category]["count"] += 1
            category_stats[category]["total_sales"] += item.get("sales", 0)

            # 价格统计
            price_total += item["price"]
            price_count += 1

            # 添加统计信息到数据项
            item["category_rank"] = category_stats[category]["count"]
            item["avg_price"] = round(price_total / price_count, 2) if price_count > 0 else 0

            yield item
            self.stats["saved"] += 1

    def run(self, total: int):
        """
        运行流水线

        Args:
            total: 需要处理的数据总量
        """
        print(f"🚀 启动数据处理流水线，处理 {total:,} 条数据")
        print("-" * 50)

        start_time = time.time()

        # 启动流水线 - 各阶段串联
        urls = self.url_generator(total)
        raw_data = self.data_fetcher(urls)
        cleaned_data = self.data_cleaner(raw_data)
        final_data = self.stats_collector(cleaned_data)

        # 消费数据
        processed = 0
        last_item = None

        for item in final_data:
            processed += 1
            last_item = item

            # 每处理10000条打印一次进度
            if processed % 10000 == 0:
                elapsed = time.time() - start_time
                speed = processed / elapsed if elapsed > 0 else 0
                print(f"  已处理: {processed:,} | 速度: {speed:,.0f}/s | "
                      f"内存: {self.get_memory():.1f}MB")

            # 演示用，只处理前100000条（避免测试时间过长）
            if processed >= 100000:
                break

        # 输出最终统计
        elapsed = time.time() - start_time
        print("-" * 50)
        print(f"✅ 处理完成: {processed:,} 条数据")
        print(f"⏱️  总耗时: {elapsed:.2f} 秒")
        print(f"📊 平均速度: {processed/elapsed:,.0f} 条/秒")
        print()

        # 输出各阶段统计
        print("📈 各阶段处理统计:")
        print(f"  URL生成: {self.stats['generated']:,}")
        print(f"  数据获取: {self.stats['fetched']:,}")
        print(f"  数据清洗: {self.stats['cleaned']:,}")
        print(f"  统计收集: {self.stats['saved']:,}")
        print()

        # 输出内存信息
        print(f"💾 当前内存占用: {self.get_memory():.1f}MB")

        # 输出最后一条数据示例
        if last_item:
            print()
            print("📦 最后一条数据示例:")
            print(f"  ID: {last_item['id']}")
            print(f"  名称: {last_item['name']}")
            print(f"  价格: ¥{last_item['price']}")
            print(f"  评分: {last_item['rating']}")
            print(f"  销量: {last_item['sales']}")
            print(f"  分类: {last_item['category']}")
            print(f"  质量评分: {last_item['quality_score']}")

    def get_memory(self) -> float:
        """
        获取当前进程内存占用（MB）

        Returns:
            float: 内存占用（MB）
        """
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # 如果psutil未安装，返回估算值
            return 0.0


if __name__ == "__main__":
    # 模拟处理100万个数据
    pipeline = DataPipeline()
    pipeline.run(1_000_000)
