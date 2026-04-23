"""
生成器模式 - 内存优化的核心

学习目标:
1. 理解生成器的"惰性计算"特性
2. 掌握 yield 语法和生成器协议
3. 理解生成器在爬虫中的内存优化价值

运行方式:
    python code/04_generator.py

关键概念:
- yield: 暂停函数，返回值
- next(): 从暂停处恢复
- StopIteration: 迭代结束时抛出
- 惰性求值: 按需计算，不预先加载所有数据

对比:
    列表: [i for i in range(1000000)]  # 一次生成100万个元素，占内存
    生成器: (i for i in range(1000000))  # 每次只生成1个，不占内存
"""

import sys
import time


def simple_generator():
    """最简单的生成器"""
    yield 1
    yield 2
    yield 3


def number_generator(n):
    """生成1到n的数字"""
    for i in range(1, n + 1):
        yield i


def fibonacci_generator():
    """斐波那契数列生成器（无限序列）"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def demo_basic():
    """基础演示"""
    print("=" * 50)
    print("生成器基础")
    print("=" * 50)

    gen = simple_generator()
    print(f"生成器对象: {gen}")
    print(f"类型: {type(gen)}")

    print("\n使用 next() 获取值:")
    print(f"第1次 next: {next(gen)}")  # 1
    print(f"第2次 next: {next(gen)}")  # 2
    print(f"第3次 next: {next(gen)}")  # 3

    print("\n使用 for 迭代:")
    for x in simple_generator():
        print(f"  {x}")


def demo_memory_efficiency():
    """内存效率对比"""
    print("\n" + "=" * 50)
    print("内存效率对比")
    print("=" * 50)

    n = 1000000

    # 列表：一次性生成所有元素
    list_data = list[int](range(n))
    print(f"列表大小: {sys.getsizeof(list_data):,} bytes")  # ~8MB

    # 生成器：按需生成
    gen_data = number_generator(n)
    print(f"生成器大小: {sys.getsizeof(gen_data):,} bytes")  # ~200 bytes

    print(f"\n💡 生成器比列表节省: {sys.getsizeof(list_data) - sys.getsizeof(gen_data):,} bytes")
    print("💡 即使处理100万个数据，生成器也只占几百字节！")


def demo_lazy_evaluation():
    """惰性求值演示"""
    print("\n" + "=" * 50)
    print("惰性求值（按需计算）")
    print("=" * 50)

    def expensive_computation(x):
        """模拟耗时计算"""
        time.sleep(0.01)
        return x * x

    def lazy_compute(n):
        """惰性：只有真正需要时才计算"""
        for i in range(n):
            yield expensive_computation(i)

    print("使用生成器（只取前5个，只计算5次）:")
    gen = lazy_compute(100)  # 设定总数100
    for i in range(5):
        val = next(gen)
        print(f"  计算第{i+1}个: {val}")

    print("\n💡 对比：列表需要一次性计算100次，生成器只计算了5次")


def demo_fibonacci():
    """斐波那契生成器 - 无限序列"""
    print("\n" + "=" * 50)
    print("斐波那契生成器（无限序列）")
    print("=" * 50)

    fib = fibonacci_generator()

    print("前20个斐波那契数:")
    for i in range(20):
        print(f"  F({i}) = {next(fib)}")

    print("\n💡 生成器可以表示无限序列，列表不行！")


def demo_send():
    """生成器的 send() 方法"""
    print("\n" + "=" * 50)
    print("生成器 send() 方法")
    print("=" * 50)

    def counter():
        """计数器，可以接收外部信号"""
        count = 0
        while True:
            received = yield count  # yield可以接收值
            if received is not None:
                print(f"  📩 收到信号: {received}")
                count = received
            else:
                count += 1

    c = counter()
    print(f"next(c): {next(c)}")  # 0
    print(f"next(c): {next(c)}")  # 1
    print(f"next(c): {next(c)}")  # 2
    print(f"send(100): {c.send(100)}")  # 重置为100
    print(f"next(c): {next(c)}")  # 101


def demo_in_crawler():
    """
    生成器在爬虫中的应用

    场景: 爬取大量数据时，边爬边处理，不积压
    """
    print("\n" + "=" * 50)
    print("生成器在爬虫中的应用")
    print("=" * 50)

    def generate_urls(base_url, total_pages):
        """
        URL生成器：不会一次性生成所有URL
        """
        for page in range(1, total_pages + 1):
            yield f"{base_url}?page={page}&limit=20"

    def crawl_page(url):
        """
        模拟爬取单个页面
        实际项目中，这里用 requests 或 aiohttp 请求真实URL
        """
        # 模拟返回数据
        page_num = url.split("page=")[1].split("&")[0]
        return {
            "page": page_num,
            "items": [f"item_{page_num}_{i}" for i in range(20)]
        }

    def crawler_generator():
        """
        生成器爬虫：边爬边处理，不积压数据

        优势：
        1. 内存占用始终很低
        2. 可以随时停止
        3. 适合处理大数据量
        """
        base_url = "https://api.example.com/products"
        total_pages = 1000

        total_items = 0

        for url in generate_urls(base_url, total_pages):
            items = crawl_page(url)

            for item in items["items"]:
                yield item  # 每爬到一条就yield出去
                total_items += 1

                if total_items % 1000 == 0:
                    print(f"  已处理 {total_items} 条...")

    # 消费生成器
    count = 0
    total_length = 0

    print("开始处理（只处理前10000条演示）:\n")
    for item in crawler_generator():
        count += 1
        total_length += len(item)

        if count <= 10:
            print(f"  处理: {item}")
        elif count == 11:
            print("  ...")

        if count >= 10000:
            break

    print(f"\n✅ 共处理 {count:,} 条数据")
    print(f"📊 平均每条长度: {total_length/count:.1f} 字符")


if __name__ == "__main__":
    demo_basic()
    demo_memory_efficiency()
    demo_lazy_evaluation()
    demo_fibonacci()
    demo_send()
    demo_in_crawler()
