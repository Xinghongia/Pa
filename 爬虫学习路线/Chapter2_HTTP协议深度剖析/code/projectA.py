"""
HTTP请求头构造器 - 项目A

功能说明：
1. 分析任意URL并生成完整的浏览器请求头
2. 支持多种浏览器UA切换（Chrome/Firefox/Safari/Edge）
3. 查看每个请求头的作用说明
4. 发送请求并验证请求头是否生效
5. 保存常用网站的请求头配置到文件

使用方法：
1. 运行：python projectA.py
2. 输入要分析的URL
3. 选择使用的浏览器UA
4. 查看生成的请求头和响应结果

核心原理：
- 请求头是HTTP协议的一部分，告诉服务器客户端的信息
- 完整的请求头能伪装成真实浏览器，避免被识别为爬虫
- 不同网站的请求头要求不同，需要针对性构造

合规提醒：
- 本项目为学习用途，用于理解HTTP协议
- 实际爬虫应用请遵守robots协议和相关法律法规
"""

import requests
import json
import os
import sys
from urllib.parse import urlparse
from typing import Dict, Optional, List

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class HeaderBuilder:
    """HTTP请求头构造器"""

    # 常见浏览器User-Agent列表
    USER_AGENTS = {
        'chrome': {
            'name': 'Chrome (Windows)',
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'chrome_mac': {
            'name': 'Chrome (macOS)',
            'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'firefox': {
            'name': 'Firefox (Windows)',
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        },
        'firefox_mac': {
            'name': 'Firefox (macOS)',
            'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        },
        'safari': {
            'name': 'Safari (macOS)',
            'ua': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        },
        'edge': {
            'name': 'Edge (Windows)',
            'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        },
        'mobile_chrome': {
            'name': 'Chrome (Android)',
            'ua': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        },
        'mobile_safari': {
            'name': 'Safari (iPhone)',
            'ua': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
        }
    }

    # 请求头说明文档
    HEADER_DESCRIPTIONS = {
        'User-Agent': '浏览器标识，告诉服务器是什么浏览器和操作系统。不同的UA会返回不同版本的页面。',
        'Accept': '告诉服务器客户端能处理的内容类型（MIME类型），q值表示优先级。',
        'Accept-Language': '声明客户端偏好的语言，zh-CN表示中文简体，en表示英语。',
        'Accept-Encoding': '声明支持的压缩算法，gzip/deflate/br可以大幅减少传输数据量。',
        'Connection': 'keep-alive表示保持连接不复用，close表示每次请求后关闭连接。',
        'Upgrade-Insecure-Requests': '告诉服务器客户端支持升级不安全的请求到HTTPS。',
        'Host': '目标服务器的主机名和端口号，必不可少，用于区分同一IP上的多个网站。',
        'Referer': '当前请求的来源页面URL，用于防盗链和统计来源分析。',
        'Cookie': '服务器设置的Cookie，每次请求时会自动携带，用于会话跟踪。',
        'Authorization': '认证信息，用于API接口的权限验证，如Bearer Token、Basic Auth。',
        'Origin': '请求的来源域名，用于CORS跨域请求限制。',
        'Sec-Fetch-Dest': 'Fetch API的安全特性，表示请求的目标资源类型。',
        'Sec-Fetch-Mode': 'Fetch API的安全特性，表示请求模式。',
        'Sec-Fetch-Site': 'Fetch API的安全特性，表示请求来源与目标站点的关系。',
        'Sec-Fetch-User': 'Fetch API的安全特性，?1表示由用户触发的请求。',
        'Cache-Control': '缓存控制指令，no-cache表示不使用缓存，max-age表示缓存有效期。',
        'If-Modified-Since': '条件请求，如果资源未修改则返回304，节省带宽。',
        'If-None-Match': '条件请求，基于ETag判断资源是否修改。',
        'X-Requested-With': '通常设置为XMLHttpRequest，表示AJAX异步请求。',
        'X-Forwarded-For': '代理转发时添加的真实IP头，用于突破简单IP限制。'
    }

    def __init__(self):
        self.config_dir = 'header_configs'
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def get_ua_list(self) -> List[str]:
        """获取支持的UA列表"""
        return list(self.USER_AGENTS.keys())

    def get_ua_info(self, ua_key: str) -> Dict:
        """获取指定UA的详细信息"""
        return self.USER_AGENTS.get(ua_key, {})

    def build_headers(self, url: str, referer: Optional[str] = None,
                     cookies: Optional[str] = None, ua_key: str = 'chrome',
                     custom_headers: Optional[Dict] = None) -> Dict[str, str]:
        """
        构造完整请求头

        Args:
            url: 目标URL
            referer: 来源页面URL（可选）
            cookies: Cookie字符串（可选）
            ua_key: User-Agent类型键名
            custom_headers: 自定义请求头（可选）

        Returns:
            Dict: 构造好的请求头字典
        """
        # 获取User-Agent
        ua_info = self.USER_AGENTS.get(ua_key, self.USER_AGENTS['chrome'])
        headers = {
            'User-Agent': ua_info['ua']
        }

        # 解析URL获取域名
        parsed = urlparse(url)

        # 添加基础请求头
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        headers['Connection'] = 'keep-alive'
        headers['Upgrade-Insecure-Requests'] = '1'

        # 设置Host
        headers['Host'] = parsed.netloc

        # 设置Referer
        if referer:
            headers['Referer'] = referer
        else:
            headers['Referer'] = f'{parsed.scheme}://{parsed.netloc}/'

        # 设置Cookie
        if cookies:
            headers['Cookie'] = cookies

        # 添加安全请求头（现代浏览器常见）
        headers['Sec-Fetch-Dest'] = 'document'
        headers['Sec-Fetch-Mode'] = 'navigate'
        headers['Sec-Fetch-Site'] = 'none'
        headers['Sec-Fetch-User'] = '?1'

        # 添加移动端特有的请求头
        if 'mobile' in ua_key:
            headers['X-Requested-With'] = 'com.android.browser'

        # 合并自定义请求头
        if custom_headers:
            headers.update(custom_headers)

        return headers

    def explain_headers(self, headers: Dict[str, str]) -> None:
        """
        打印请求头的详细说明

        Args:
            headers: 请求头字典
        """
        print("\n" + "=" * 60)
        print("请求头说明")
        print("=" * 60)

        for key, value in headers.items():
            description = self.HEADER_DESCRIPTIONS.get(key, '无说明')
            print(f"\n【{key}】")
            print(f"  值: {value[:80]}{'...' if len(value) > 80 else ''}")
            print(f"  说明: {description}")

        print("\n" + "=" * 60)

    def analyze_response(self, response: requests.Response, show_content: bool = True) -> None:
        """
        分析响应内容

        Args:
            response: requests响应对象
            show_content: 是否显示响应内容
        """
        print("\n" + "-" * 50)
        print("响应分析")
        print("-" * 50)

        # 状态码
        status_info = {
            200: 'OK - 请求成功',
            301: 'Moved Permanently - 永久重定向',
            302: 'Found - 临时重定向',
            304: 'Not Modified - 未修改，使用缓存',
            400: 'Bad Request - 请求错误',
            401: 'Unauthorized - 未授权，需要登录',
            403: 'Forbidden - 禁止访问',
            404: 'Not Found - 页面不存在',
            429: 'Too Many Requests - 请求过于频繁',
            500: 'Internal Server Error - 服务器内部错误',
            502: 'Bad Gateway - 网关错误',
            503: 'Service Unavailable - 服务不可用'
        }
        status_desc = status_info.get(response.status_code, '未知状态')
        print(f"状态码: {response.status_code} - {status_desc}")

        # 响应头
        print(f"\n响应头 (共 {len(response.headers)} 项):")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'content-length', 'date', 'server', 'set-cookie']:
                print(f"  {key}: {value}")

        # 内容信息
        if show_content:
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                print(f"\n内容类型: HTML页面")
                print(f"内容长度: {len(response.text)} 字符")
                # 提取title
                if '<title>' in response.text:
                    start = response.text.find('<title>') + 7
                    end = response.text.find('</title>')
                    title = response.text[start:end]
                    print(f"页面标题: {title}")
            elif 'application/json' in content_type:
                print(f"\n内容类型: JSON数据")
                try:
                    data = response.json()
                    print(f"JSON数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                except:
                    print(f"内容长度: {len(response.text)} 字符")
            else:
                print(f"\n内容类型: {content_type}")
                print(f"内容长度: {len(response.content)} 字节")

    def save_config(self, name: str, url: str, ua_key: str, headers: Dict[str, str]) -> None:
        """
        保存请求头配置到文件

        Args:
            name: 配置名称
            url: 目标URL
            ua_key: UA类型
            headers: 请求头字典
        """
        config_file = os.path.join(self.config_dir, f'{name}.json')
        config = {
            'name': name,
            'url': url,
            'ua_key': ua_key,
            'headers': headers
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ 配置已保存到: {config_file}")

    def load_config(self, name: str) -> Optional[Dict]:
        """
        从文件加载请求头配置

        Args:
            name: 配置名称

        Returns:
            Dict: 配置字典，不存在则返回None
        """
        config_file = os.path.join(self.config_dir, f'{name}.json')
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def list_configs(self) -> List[str]:
        """
        列出所有保存的配置

        Returns:
            List: 配置名称列表
        """
        if not os.path.exists(self.config_dir):
            return []
        return [f.replace('.json', '') for f in os.listdir(self.config_dir) if f.endswith('.json')]

    def send_request(self, url: str, ua_key: str = 'chrome',
                    referer: Optional[str] = None,
                    cookies: Optional[str] = None,
                    show_headers: bool = True,
                    show_response: bool = True) -> requests.Response:
        """
        发送请求并显示结果

        Args:
            url: 目标URL
            ua_key: UA类型
            referer: 来源页面
            cookies: Cookie
            show_headers: 是否显示请求头
            show_response: 是否显示响应

        Returns:
            Response: requests响应对象
        """
        headers = self.build_headers(url, referer, cookies, ua_key)

        if show_headers:
            print("\n" + "=" * 50)
            print("发送的请求头")
            print("=" * 50)
            for key, value in headers.items():
                print(f"{key}: {value}")

        print("\n" + "=" * 50)
        print(f"正在请求: {url}")
        print("=" * 50)

        try:
            response = requests.get(url, headers=headers, timeout=15, verify=True)

            if show_response:
                self.analyze_response(response)

            return response

        except requests.exceptions.Timeout:
            print("❌ 请求超时（15秒）")
            return None
        except requests.exceptions.SSLError as e:
            print(f"⚠️ SSL错误: {str(e)[:50]}...")
            print("尝试忽略SSL验证...")
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            if show_response:
                self.analyze_response(response)
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {str(e)[:80]}...")
            return None

    def interactive_mode(self) -> None:
        """交互式模式"""
        print("=" * 60)
        print("HTTP请求头构造器 - 交互模式")
        print("=" * 60)
        print("\n支持的浏览器UA:")
        for key, info in self.USER_AGENTS.items():
            print(f"  {key}: {info['name']}")

        # 检查是否有保存的配置
        configs = self.list_configs()
        if configs:
            print(f"\n保存的配置: {', '.join(configs)}")

        while True:
            print("\n" + "-" * 50)
            print("请选择操作:")
            print("  1. 发送请求（输入URL）")
            print("  2. 查看保存的配置")
            print("  3. 加载配置发送请求")
            print("  4. 测试 httpbin.org")
            print("  5. 退出")
            print("-" * 50)

            choice = input("请输入选项 (1-5): ").strip()

            if choice == '1':
                url = input("请输入URL: ").strip()
                if not url:
                    print("URL不能为空")
                    continue

                # 选择UA
                print("\n选择浏览器UA:")
                for i, key in enumerate(self.USER_AGENTS.keys(), 1):
                    print(f"  {i}. {self.USER_AGENTS[key]['name']}")
                ua_choice = input(f"请输入选项 (1-{len(self.USER_AGENTS)}, 默认1): ").strip()
                ua_key = list(self.USER_AGENTS.keys())[int(ua_choice) - 1 if ua_choice.isdigit() and 1 <= int(ua_choice) <= len(self.USER_AGENTS) else 0]

                # 可选参数
                referer = input("输入Referer (可选，直接回车跳过): ").strip() or None
                cookies = input("输入Cookie (可选，直接回车跳过): ").strip() or None

                # 发送请求
                response = self.send_request(url, ua_key, referer, cookies)

                # 询问是否保存配置
                if response:
                    save = input("\n是否保存此配置？(y/n): ").strip().lower()
                    if save == 'y':
                        name = input("输入配置名称: ").strip()
                        headers = self.build_headers(url, referer, cookies, ua_key)
                        self.save_config(name, url, ua_key, headers)

            elif choice == '2':
                configs = self.list_configs()
                if configs:
                    print(f"\n保存的配置 ({len(configs)}个):")
                    for name in configs:
                        config = self.load_config(name)
                        print(f"  - {name}: {config['url']} ({config['ua_key']})")
                else:
                    print("\n暂无保存的配置")

            elif choice == '3':
                configs = self.list_configs()
                if not configs:
                    print("\n暂无保存的配置")
                    continue
                print(f"\n保存的配置: {', '.join(configs)}")
                name = input("输入配置名称: ").strip()
                config = self.load_config(name)
                if config:
                    response = self.send_request(
                        config['url'],
                        config['ua_key'],
                        show_headers=True
                    )
                else:
                    print(f"配置 {name} 不存在")

            elif choice == '4':
                print("\n--- 测试 httpbin.org ---")
                print("\n1. 测试请求头 (httpbin.org/headers)")
                self.send_request("https://httpbin.org/headers", show_response=True)

                print("\n2. 测试IP (httpbin.org/ip)")
                self.send_request("https://httpbin.org/ip", show_response=True)

                print("\n3. 测试Cookie (httpbin.org/cookies)")
                self.send_request("https://httpbin.org/cookies", show_response=True)

            elif choice == '5':
                print("\n感谢使用！")
                break

            else:
                print("无效选项，请重新输入")

    def explain_all_headers(self) -> None:
        """显示所有请求头的说明"""
        print("\n" + "=" * 60)
        print("HTTP请求头完全指南")
        print("=" * 60)

        for header, description in self.HEADER_DESCRIPTIONS.items():
            print(f"\n【{header}】")
            print(f"  {description}")


def main():
    """主函数"""
    builder = HeaderBuilder()

    if len(sys.argv) > 1:
        # 命令行模式
        url = sys.argv[1]
        ua_key = sys.argv[2] if len(sys.argv) > 2 else 'chrome'
        builder.send_request(url, ua_key)
    else:
        # 交互式模式
        builder.interactive_mode()


if __name__ == "__main__":
    main()
