"""
代理池与认证管理器 - 项目C

功能说明：
1. 代理池管理：添加代理、轮换使用、失败标记、自动重试
2. 多种认证支持：Basic Auth、Bearer Token、JWT解码和验证
3. 代理认证：支持带用户名密码的代理
4. 统计报告：成功/失败次数、响应时间、代理使用统计

使用方法：
1. 运行：python projectC.py
2. 选择测试功能
3. 观察代理轮换和认证效果

核心原理：
- 代理池：通过轮换代理IP，避免单一IP请求过于频繁被封
- Basic Auth：用户密码 Base64 编码后发送
- Bearer Token：JWT令牌放在 Authorization 头
- JWT：JSON Web Token，分为 Header、Payload、Signature 三部分

合规提醒：
- 本项目为学习用途，用于理解HTTP代理和认证机制
- 实际使用代理请确保来源合法，被用于违法违规行为
"""

import requests
import json
import base64
import time
import sys
import os
from urllib.parse import urlparse
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class ProxyInfo:
    """代理信息"""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    success_count: int = 0
    fail_count: int = 0
    avg_response_time: float = 0.0
    total_response_time: float = 0.0
    last_used: Optional[str] = None
    is_failed: bool = False

    def get_formatted_proxy(self) -> str:
        """获取格式化后的代理URL（带认证）"""
        if self.username and self.password:
            parsed = urlparse(self.url)
            return f"{parsed.scheme}://{self.username}:{self.password}@{parsed.netloc}"
        return self.url


class ProxyManager:
    """代理池管理器"""

    def __init__(self):
        self.proxies: List[ProxyInfo] = []
        self.current_index: int = 0
        self.failed_set: Set[str] = set()

    def add_proxy(self, proxy_url: str, username: Optional[str] = None,
                  password: Optional[str] = None) -> None:
        """
        添加代理到池中

        Args:
            proxy_url: 代理URL，如 http://127.0.0.1:7890
            username: 代理用户名（可选）
            password: 代理密码（可选）
        """
        proxy_info = ProxyInfo(url=proxy_url, username=username, password=password)
        self.proxies.append(proxy_info)
        print(f"  ✅ 添加代理: {proxy_url}" +
              (f" (认证用户: {username})" if username else ""))

    def get_next_proxy(self) -> Optional[ProxyInfo]:
        """
        获取下一个可用代理

        Returns:
            ProxyInfo: 可用代理信息，无可用代理返回None
        """
        if not self.proxies:
            return None

        # 尝试找到未失败的代理
        max_attempts = len(self.proxies)
        for _ in range(max_attempts):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)

            if proxy.url not in self.failed_set:
                proxy.last_used = datetime.now().strftime('%H:%M:%S')
                return proxy

        # 所有代理都失败了，清除失败记录重试
        if self.failed_set:
            print(f"  ⚠️ 所有代理都失败过，清除失败记录重试")
            self.failed_set.clear()
            return self.proxies[self.current_index]

        return None

    def mark_proxy_failed(self, proxy_url: str) -> None:
        """
        标记代理失败

        Args:
            proxy_url: 失败的代理URL
        """
        self.failed_set.add(proxy_url)
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.fail_count += 1
                proxy.is_failed = True
                break
        print(f"  ❌ 代理失败: {proxy_url} (已失败次数: {len(self.failed_set)})")

    def mark_proxy_success(self, proxy_url: str, response_time: float) -> None:
        """
        标记代理成功

        Args:
            proxy_url: 成功的代理URL
            response_time: 响应时间（秒）
        """
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                proxy.success_count += 1
                proxy.is_failed = False
                proxy.total_response_time += response_time
                proxy.avg_response_time = proxy.total_response_time / proxy.success_count
                break

    def get_stats(self) -> Dict:
        """
        获取代理池统计信息

        Returns:
            Dict: 统计信息字典
        """
        total_success = sum(p.success_count for p in self.proxies)
        total_fail = sum(p.fail_count for p in self.proxies)
        total = total_success + total_fail
        success_rate = (total_success / total * 100) if total > 0 else 0

        return {
            'total_proxies': len(self.proxies),
            'total_success': total_success,
            'total_fail': total_fail,
            'success_rate': f"{success_rate:.1f}%",
            'available': len([p for p in self.proxies if p.url not in self.failed_set])
        }

    def print_stats(self) -> None:
        """打印代理池详细统计"""
        print("\n" + "=" * 60)
        print("代理池统计")
        print("=" * 60)

        stats = self.get_stats()
        print(f"代理总数: {stats['total_proxies']}")
        print(f"成功次数: {stats['total_success']}")
        print(f"失败次数: {stats['total_fail']}")
        print(f"成功率: {stats['success_rate']}")
        print(f"可用代理: {stats['available']}")

        print("\n各代理详情:")
        print("-" * 60)
        print(f"{'代理URL':<30} {'成功':<8} {'失败':<8} {'均响应时间':<10} {'状态'}")
        print("-" * 60)
        for proxy in self.proxies:
            status = "❌失败" if proxy.is_failed else "✅正常"
            avg_time = f"{proxy.avg_response_time:.3f}s" if proxy.avg_response_time else "-"
            print(f"{proxy.url:<30} {proxy.success_count:<8} {proxy.fail_count:<8} {avg_time:<10} {status}")


class AuthManager:
    """认证管理器"""

    @staticmethod
    def create_basic_auth(username: str, password: str) -> Dict[str, str]:
        """
        创建Basic认证头

        Args:
            username: 用户名
            password: 密码

        Returns:
            Dict: 包含Authorization的请求头
        """
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        return {'Authorization': f'Basic {encoded}'}

    @staticmethod
    def create_bearer_token(token: str) -> Dict[str, str]:
        """
        创建Bearer Token认证头

        Args:
            token: JWT或其他令牌

        Returns:
            Dict: 包含Authorization的请求头
        """
        return {'Authorization': f'Bearer {token}'}

    @staticmethod
    def decode_jwt(token: str) -> Optional[Dict]:
        """
        解码JWT令牌

        JWT格式: header.payload.signature
        - Header: 算法和类型
        - Payload: 用户信息和声明
        - Signature: 签名验证

        Args:
            token: JWT字符串

        Returns:
            Dict: 包含header和payload的字典，失败返回None
        """
        parts = token.split('.')
        if len(parts) != 3:
            print(f"  ❌ JWT格式错误: 应该有3个部分，用.分隔")
            return None

        try:
            # 解码 Header
            header_bytes = AuthManager._base64url_decode(parts[0])
            header = json.loads(header_bytes.decode('utf-8'))

            # 解码 Payload
            payload_bytes = AuthManager._base64url_decode(parts[1])
            payload = json.loads(payload_bytes.decode('utf-8'))

            return {
                'header': header,
                'payload': payload,
                'signature': parts[2]
            }
        except Exception as e:
            print(f"  ❌ JWT解码失败: {str(e)}")
            return None

    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        """
        Base64URL解码

        JWT使用的是Base64URL编码，与标准Base64略有不同：
        - + 换成 -
        - / 换成 _
        - 去掉填充 =

        Args:
            data: Base64URL编码的字符串

        Returns:
            bytes: 解码后的字节
        """
        # 添加填充
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding

        # 替换 Base64URL 特殊字符
        data = data.replace('-', '+').replace('_', '/')

        return base64.b64decode(data)

    @staticmethod
    def is_token_expired(payload: Dict) -> bool:
        """
        检查Token是否过期

        Args:
            payload: JWT的payload部分

        Returns:
            bool: 是否过期
        """
        if 'exp' not in payload:
            return False

        exp_time = payload['exp']
        current_time = time.time()

        # 检查是否已过期
        if current_time > exp_time:
            return True

        # 检查是否即将过期（5分钟内）
        time_left = exp_time - current_time
        if time_left < 300:
            print(f"  ⚠️ Token即将在 {int(time_left)} 秒后过期")

        return False

    @staticmethod
    def print_jwt_info(token: str) -> None:
        """
        打印JWT详细信息

        Args:
            token: JWT字符串
        """
        print("\n" + "-" * 50)
        print("JWT解码结果")
        print("-" * 50)

        decoded = AuthManager.decode_jwt(token)
        if not decoded:
            return

        print(f"\n【Header】(算法和类型):")
        for key, value in decoded['header'].items():
            alg_name = {
                'HS256': 'HMAC using SHA-256',
                'HS384': 'HMAC using SHA-384',
                'HS512': 'HMAC using SHA-512',
                'RS256': 'RSA using SHA-256',
                'RS384': 'RSA using SHA-384',
                'RS512': 'RSA using SHA-512'
            }.get(value, value)
            print(f"  {key}: {alg_name if key == 'alg' else value}")

        print(f"\n【Payload】(数据):")
        for key, value in decoded['payload'].items():
            # 特殊字段解释
            field_desc = {
                'iss': '签发者',
                'sub': '主题/用户ID',
                'aud': '受众/接受者',
                'exp': '过期时间',
                'iat': '签发时间',
                'nbf': '生效时间',
                'jti': 'JWT唯一ID',
                'name': '用户名称',
                'username': '用户名',
                'email': '邮箱',
                'role': '角色'
            }.get(key, key)

            # 格式化值
            if key in ['exp', 'iat', 'nbf']:
                from datetime import datetime
                value_str = datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
            else:
                value_str = str(value)

            print(f"  {key} ({field_desc}): {value_str}")

        print(f"\n【Signature】(签名):")
        print(f"  {decoded['signature'][:20]}... (省略)")

        # 检查过期
        if AuthManager.is_token_expired(decoded['payload']):
            print(f"\n  🔴 Token已过期!")
        else:
            print(f"\n  🟢 Token有效")


class CrawlerWithProxy:
    """支持代理和认证的爬虫"""

    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.auth_manager = AuthManager()
        self.session = requests.Session()
        self.request_count = 0
        self.success_count = 0
        self.fail_count = 0

    def add_proxy(self, proxy_url: str, username: Optional[str] = None,
                  password: Optional[str] = None) -> None:
        """
        添加代理

        Args:
            proxy_url: 代理URL
            username: 用户名（可选）
            password: 密码（可选）
        """
        self.proxy_manager.add_proxy(proxy_url, username, password)

    def request_with_proxy(self, url: str, method: str = 'GET',
                          auth_type: Optional[str] = None,
                          token: Optional[str] = None,
                          username: Optional[str] = None,
                          password: Optional[str] = None,
                          timeout: int = 10,
                          **kwargs) -> Optional[requests.Response]:
        """
        使用代理发送请求

        Args:
            url: 目标URL
            method: 请求方法 GET/POST
            auth_type: 认证类型 'basic' 或 'bearer'
            token: 令牌（用于bearer认证）
            username: 用户名（用于basic认证）
            password: 密码（用于basic认证）
            timeout: 超时时间
            **kwargs: 其他requests参数

        Returns:
            Response: 响应对象，失败返回None
        """
        proxy = self.proxy_manager.get_next_proxy()

        if not proxy:
            print(f"  ❌ 没有可用的代理")
            return None

        # 构建代理字典
        proxies = {
            'http': proxy.get_formatted_proxy(),
            'https': proxy.get_formatted_proxy()
        }

        # 构建请求头
        headers = kwargs.get('headers', {})

        if auth_type == 'basic' and username and password:
            headers.update(self.auth_manager.create_basic_auth(username, password))
        elif auth_type == 'bearer' and token:
            headers.update(self.auth_manager.create_bearer_token(token))

        kwargs['headers'] = headers
        kwargs['timeout'] = timeout

        # 发送请求
        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, proxies=proxies, **kwargs)
            else:
                response = self.session.post(url, proxies=proxies, **kwargs)

            response_time = time.time() - start_time
            self.request_count += 1

            if response.status_code < 400:
                self.success_count += 1
                self.proxy_manager.mark_proxy_success(proxy.url, response_time)
                print(f"  ✅ 成功 ({response.status_code}) - {proxy.url} - {response_time:.3f}s")
                return response
            else:
                self.fail_count += 1
                self.proxy_manager.mark_proxy_failed(proxy.url)
                print(f"  ❌ 失败 ({response.status_code}) - {proxy.url}")
                return response

        except requests.exceptions.Timeout:
            self.fail_count += 1
            self.proxy_manager.mark_proxy_failed(proxy.url)
            print(f"  ❌ 超时 - {proxy.url}")
            return None

        except requests.exceptions.RequestException as e:
            self.fail_count += 1
            self.proxy_manager.mark_proxy_failed(proxy.url)
            print(f"  ❌ 异常: {str(e)[:50]} - {proxy.url}")
            return None

    def get_stats(self) -> Dict:
        """获取爬虫统计"""
        return {
            'total': self.request_count,
            'success': self.success_count,
            'fail': self.fail_count,
            'success_rate': f"{(self.success_count/self.request_count*100) if self.request_count > 0 else 0:.1f}%"
        }

    def print_request_log(self, method: str, url: str,
                         auth_type: Optional[str] = None) -> None:
        """打印请求日志头"""
        print(f"\n{'=' * 50}")
        print(f"{method}请求: {url}")
        if auth_type:
            print(f"认证方式: {auth_type}")
        print("=" * 50)


class CrawlerFramework:
    """爬虫框架主类 - 整合所有功能"""

    def __init__(self):
        self.crawler = CrawlerWithProxy()
        self.proxy_manager = self.crawler.proxy_manager
        self.auth_manager = self.crawler.auth_manager

    def demo_basic_auth(self) -> None:
        """演示Basic认证"""
        print("\n" + "=" * 60)
        print("Basic Auth 认证演示")
        print("=" * 60)

        print("\n原理说明:")
        print("  1. 将 username:password 用冒号连接")
        print("  2. 进行 Base64 编码")
        print("  3. 放在 Authorization: Basic <编码> 请求头中")

        # 演示编码过程
        username = "testuser"
        password = "testpass"
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('ascii')

        print(f"\n编码过程:")
        print(f"  用户名: {username}")
        print(f"  密码: {password}")
        print(f"  合并: {credentials}")
        print(f"  Base64: {encoded}")
        print(f"\n请求头: Authorization: Basic {encoded}")

        # httpbin.org/basic-auth 可以验证Basic认证
        self.crawler.print_request_log('GET', 'https://httpbin.org/basic-auth/user/passwd', 'basic')
        response = self.crawler.request_with_proxy(
            'https://httpbin.org/basic-auth/user/passwd',
            auth_type='basic',
            username='user',
            password='passwd'
        )

        if response:
            print(f"\n响应内容: {response.text}")

    def demo_bearer_token(self) -> None:
        """演示Bearer Token认证"""
        print("\n" + "=" * 60)
        print("Bearer Token 认证演示")
        print("=" * 60)

        print("\n原理说明:")
        print("  1. 将 JWT 令牌直接使用")
        print("  2. 放在 Authorization: Bearer <token> 请求头中")

        # 构造一个测试JWT（使用HS256算法）
        import hmac
        import hashlib

        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": "1234567890",
            "name": "Test User",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }

        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip('=')

        # 模拟签名
        signature = hmac.new(
            b'secret',
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')

        token = f"{header_b64}.{payload_b64}.{signature_b64}"

        print(f"\n生成的JWT:")
        print(f"  {token[:50]}...")

        self.crawler.print_request_log('GET', 'https://httpbin.org/headers', 'bearer')
        response = self.crawler.request_with_proxy(
            'https://httpbin.org/headers',
            auth_type='bearer',
            token=token
        )

        if response:
            print(f"\n响应内容: {response.text[:200]}...")

    def demo_jwt_decode(self) -> None:
        """演示JWT解码"""
        print("\n" + "=" * 60)
        print("JWT 解码演示")
        print("=" * 60)

        # 示例JWT（来自 https://jwt.io 的示例）
        example_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        print(f"\n待解码JWT:")
        print(f"  {example_jwt}")

        self.auth_manager.print_jwt_info(example_jwt)

        # 测试自定义JWT
        print("\n" + "-" * 50)
        print("测试过期检测:")

        # 创建已过期的JWT
        expired_payload = {
            "user_id": 12345,
            "username": "test",
            "exp": int(time.time()) - 3600  # 1小时前过期
        }

        # 构造过期JWT
        header_b64 = base64.urlsafe_b64encode(
            json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
        ).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(expired_payload).encode()
        ).decode().rstrip('=')
        signature_b64 = "test_signature"

        expired_jwt = f"{header_b64}.{payload_b64}.{signature_b64}"

        decoded = self.auth_manager.decode_jwt(expired_jwt)
        if decoded:
            self.auth_manager.is_token_expired(decoded['payload'])

    def demo_proxy_pool(self) -> None:
        """演示代理池"""
        print("\n" + "=" * 60)
        print("代理池管理演示")
        print("=" * 60)

        print("\n模拟添加3个代理:")

        # 模拟添加代理（实际使用需要真实代理）
        self.proxy_manager.add_proxy("http://proxy1.example.com:8080")
        self.proxy_manager.add_proxy("http://proxy2.example.com:8080")
        self.proxy_manager.add_proxy("http://proxy3.example.com:8080")

        print("\n代理池统计:")
        self.proxy_manager.print_stats()

        print("\n模拟轮换获取代理:")
        for i in range(5):
            proxy = self.proxy_manager.get_next_proxy()
            if proxy:
                print(f"  第{i+1}次获取: {proxy.url}")

    def demo_proxy_rotation(self) -> None:
        """演示代理轮换失败重试"""
        print("\n" + "=" * 60)
        print("代理轮换与失败重试演示")
        print("=" * 60)

        # 添加测试代理
        self.proxy_manager.add_proxy("http://127.0.0.1:8080")
        self.proxy_manager.add_proxy("http://127.0.0.1:8081")
        self.proxy_manager.add_proxy("http://127.0.0.1:8082")

        print("\n模拟请求（会失败，因为代理不可用）:")

        # 尝试发送请求（实际会失败，因为没有真实代理）
        response = self.crawler.request_with_proxy(
            'https://httpbin.org/ip',
            timeout=3
        )

        print("\n当前代理池状态:")
        self.proxy_manager.print_stats()

    def run_demo(self) -> None:
        """运行演示"""
        print("=" * 60)
        print("代理池与认证管理器 - 功能演示")
        print("=" * 60)

        while True:
            print("\n" + "-" * 50)
            print("请选择测试功能:")
            print("  1. Basic Auth 认证")
            print("  2. Bearer Token 认证")
            print("  3. JWT 解码")
            print("  4. JWT 过期检测")
            print("  5. 代理池管理")
            print("  6. 代理轮换演示")
            print("  7. 完整统计报告")
            print("  8. 退出")
            print("-" * 50)

            choice = input("请输入选项 (1-8): ").strip()

            if choice == '1':
                self.demo_basic_auth()
            elif choice == '2':
                self.demo_bearer_token()
            elif choice == '3':
                self.demo_jwt_decode()
            elif choice == '4':
                print("\n" + "=" * 60)
                print("JWT 过期检测演示")
                print("=" * 60)
                self.demo_jwt_decode()
            elif choice == '5':
                self.demo_proxy_pool()
            elif choice == '6':
                self.demo_proxy_rotation()
            elif choice == '7':
                print("\n" + "=" * 60)
                print("完整统计报告")
                print("=" * 60)
                self.proxy_manager.print_stats()
                print("\n爬虫请求统计:")
                stats = self.crawler.get_stats()
                print(f"  总请求: {stats['total']}")
                print(f"  成功: {stats['success']}")
                print(f"  失败: {stats['fail']}")
                print(f"  成功率: {stats['success_rate']}")
            elif choice == '8':
                print("\n感谢使用！")
                break
            else:
                print("无效选项，请重新输入")


def main():
    """主函数"""
    framework = CrawlerFramework()
    framework.run_demo()


if __name__ == "__main__":
    main()
