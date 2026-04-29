# 代理池与认证管理器 - 架构流程图与详细解析

## 流程图

```mermaid
flowchart TD
    Start([程序启动]) --> Main["CrawlerFramework()"]

    Main --> Init["初始化各组件<br/>ProxyManager + AuthManager + CrawlerWithProxy"]

    subgraph proxy_manager["ProxyManager - 代理池管理"]
        Init --> ProxyInit["初始化代理列表<br/>proxies: List<br/>current_index: int<br/>failed_set: Set"]
        ProxyInit --> AddProxy["add_proxy() 添加代理"]
        AddProxy --> ProxyList["代理列表 ProxyInfo[]"]
    end

    subgraph auth_manager["AuthManager - 认证管理"]
        Init --> AuthInit["静态方法<br/>create_basic_auth()<br/>create_bearer_token()<br/>decode_jwt()"]
        AuthInit --> AuthMethods["三种认证方式"]
        AuthMethods --> Basic["Basic Auth<br/>用户名:密码 → Base64"]
        AuthMethods --> Bearer["Bearer Token<br/>JWT → Authorization头"]
        AuthMethods --> JWT["JWT解码<br/>Header.Payload.Signature"]
    end

    subgraph crawler["CrawlerWithProxy - 爬虫核心"]
        Init --> CrawlerInit["初始化Session<br/>请求计数器"]
        CrawlerInit --> Request["request_with_proxy()"]
    end

    subgraph request_flow["request_with_proxy 请求流程"]
        Request --> GetProxy["get_next_proxy()"]
        GetProxy --> CheckProxy{"代理可用?"}
        CheckProxy -->|是| BuildProxies["构建proxies字典"]
        CheckProxy -->|否| PrintNoProxy["打印无可用代理"]
        PrintNoProxy --> ReturnNone["return None"]
        BuildProxies --> BuildHeaders["构建请求头"]
        BuildHeaders --> CheckAuth{"auth_type?"}
        CheckAuth -->|basic| AddBasic["add_basic_auth()"]
        CheckAuth -->|bearer| AddBearer["add_bearer_token()"]
        CheckAuth -->|无| SkipAuth
        AddBasic --> SendRequest["requests.get/post()"]
        AddBearer --> SendRequest
        SkipAuth --> SendRequest
        SendRequest --> CheckResponse{"状态码 < 400?"}
        CheckResponse -->|成功| MarkSuccess["mark_proxy_success()"]
        CheckResponse -->|失败| MarkFail["mark_proxy_failed()"]
        MarkSuccess --> ReturnResponse["return response"]
        MarkFail --> ReturnNone
    end

    subgraph jwt_decode["JWT解码流程"]
        JWTDecode["decode_jwt()"] --> SplitToken["split('.')"]
        SplitToken --> CheckParts{"3个部分?"}
        CheckParts -->|否| ReturnNone2["return None"]
        CheckParts -->|是| DecodeHeader["Base64URL解码Header"]
        DecodeHeader --> DecodePayload["Base64URL解码Payload"]
        DecodePayload --> CheckExpiry["is_token_expired()"]
        CheckExpiry --> ReturnDecoded["return {header, payload}"]
    end

    subgraph demo_menu["演示菜单"]
        Menu["run_demo()"] --> Choice1["1. Basic Auth"]
        Menu --> Choice2["2. Bearer Token"]
        Menu --> Choice3["3. JWT解码"]
        Menu --> Choice4["4. JWT过期检测"]
        Menu --> Choice5["5. 代理池管理"]
        Menu --> Choice6["6. 代理轮换"]
        Menu --> Choice7["7. 完整统计"]
        Menu --> Choice8["8. 退出"]
    end

    ReturnNone --> End([结束])
    ReturnResponse --> End
    PrintNoProxy --> End

    style Start fill:#e1f5fe
    style End fill:#e8f5e9
    style proxy_manager fill:#fff3e0
    style auth_manager fill:#e3f2fd
    style crawler fill:#f3e5f5
    style request_flow fill:#fce4ec
    style jwt_decode fill:#e0f2f1
    style demo_menu fill:#fff9c4
```

---

## 详细流程解析

### 第一阶段：程序初始化

#### 1. 主类初始化
```python
class CrawlerFramework:
    def __init__(self):
        self.crawler = CrawlerWithProxy()
        self.proxy_manager = self.crawler.proxy_manager
        self.auth_manager = self.crawler.auth_manager
```
- 创建爬虫框架，整合三个核心组件
- 统一对外提供代理和认证功能

#### 2. ProxyInfo 数据类
```python
@dataclass
class ProxyInfo:
    """代理信息"""
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    success_count: int = 0
    fail_count: int = 0
    avg_response_time: float = 0.0
    is_failed: bool = False
```
- 使用 `@dataclass` 装饰器简化数据类定义
- 记录每个代理的成功/失败次数和响应时间

---

### 第二阶段：代理池管理 `ProxyManager`

#### 1. 添加代理
```python
def add_proxy(self, proxy_url: str, username: Optional[str] = None,
              password: Optional[str] = None) -> None:
    proxy_info = ProxyInfo(url=proxy_url, username=username, password=password)
    self.proxies.append(proxy_info)
```
- 支持带认证的代理
- 用户名密码会在请求时附加到代理URL中

#### 2. 获取下一个代理
```python
def get_next_proxy(self) -> Optional[ProxyInfo]:
    # 轮换获取未失败的代理
    for _ in range(max_attempts):
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        if proxy.url not in self.failed_set:
            return proxy
```
- **轮换策略**：按顺序获取代理，用完一轮再从头开始
- **失败跳过**：失败的代理会被跳过
- **失败恢复**：所有代理都失败过则清除失败记录

#### 3. 标记成功/失败
```python
def mark_proxy_success(self, proxy_url: str, response_time: float) -> None:
    proxy.success_count += 1
    proxy.avg_response_time = proxy.total_response_time / proxy.success_count

def mark_proxy_failed(self, proxy_url: str) -> None:
    self.failed_set.add(proxy_url)
    proxy.fail_count += 1
```
- 记录成功次数和响应时间，用于选择最快代理
- 记录失败次数，用于评估代理质量

---

### 第三阶段：认证管理 `AuthManager`

#### 1. Basic Auth 认证
```python
@staticmethod
def create_basic_auth(username: str, password: str) -> Dict[str, str]:
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
    return {'Authorization': f'Basic {encoded}'}
```

**原理：**
```
用户名: testuser
密码:   testpass
合并:   testuser:testpass
Base64: dGVzdHVzZXI6dGVzdHBhc3M=
请求头: Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3M=
```

**特点：**
- 简单但不够安全（Base64可逆）
- 通常用于内部API或测试环境

#### 2. Bearer Token 认证
```python
@staticmethod
def create_bearer_token(token: str) -> Dict[str, str]:
    return {'Authorization': f'Bearer {token}'}
```

**原理：**
```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
请求头: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**特点：**
- 最常用的API认证方式
- JWT令牌本身包含签名，无法伪造

#### 3. JWT 解码
```python
@staticmethod
def decode_jwt(token: str) -> Optional[Dict]:
    parts = token.split('.')
    if len(parts) != 3:
        return None

    # Base64URL解码
    header = json.loads(base64.b64decode(parts[0] + '=='))
    payload = json.loads(base64.b64decode(parts[1] + '=='))

    return {'header': header, 'payload': payload, 'signature': parts[2]}
```

**JWT结构：**
```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
|______Header______|.__________Payload__________|.________Signature________|
```

| 部分 | 内容 | 示例 |
|------|------|------|
| Header | 算法和类型 | `{"alg": "HS256", "typ": "JWT"}` |
| Payload | 用户数据和声明 | `{"sub": "1234567890", "name": "John Doe"}` |
| Signature | 签名验证 | HMAC-SHA256(header.payload, secret) |

#### 4. JWT 过期检测
```python
@staticmethod
def is_token_expired(payload: Dict) -> bool:
    if 'exp' not in payload:
        return False
    return payload['exp'] < time.time()
```

**Payload常见字段：**
| 字段 | 含义 | 示例 |
|------|------|------|
| `iss` | 签发者 | "https://auth.example.com" |
| `sub` | 用户ID/主题 | "1234567890" |
| `aud` | 受众 | "my-app" |
| `exp` | 过期时间 | 1707000000 |
| `iat` | 签发时间 | 1706996400 |
| `nbf` | 生效时间 | 1706996400 |
| `name` | 用户名称 | "John Doe" |

---

### 第四阶段：爬虫请求 `CrawlerWithProxy`

#### 1. 发送代理请求
```python
def request_with_proxy(self, url: str, method: str = 'GET',
                      auth_type: Optional[str] = None,
                      token: Optional[str] = None,
                      **kwargs) -> Optional[requests.Response]:
    # 1. 获取代理
    proxy = self.proxy_manager.get_next_proxy()

    # 2. 构建代理字典
    proxies = {'http': proxy.get_formatted_proxy(),
               'https': proxy.get_formatted_proxy()}

    # 3. 添加认证头
    headers = kwargs.get('headers', {})
    if auth_type == 'basic':
        headers.update(self.auth_manager.create_basic_auth(...))
    elif auth_type == 'bearer':
        headers.update(self.auth_manager.create_bearer_token(token))

    # 4. 发送请求
    response = self.session.get(url, proxies=proxies, **kwargs)

    # 5. 标记结果
    if response.status_code < 400:
        self.proxy_manager.mark_proxy_success(proxy.url, response_time)
    else:
        self.proxy_manager.mark_proxy_failed(proxy.url)
```

#### 2. 完整请求流程
```
获取代理 → 构建代理URL → 添加认证头 → 发送请求 → 标记结果
    ↓           ↓              ↓           ↓          ↓
 轮换获取   带认证信息     Basic/Bearer  requests  成功/失败
```

---

### 第五阶段：代理认证

#### 1. 带认证的代理URL格式
```python
def get_formatted_proxy(self) -> str:
    if self.username and self.password:
        parsed = urlparse(self.url)
        return f"{parsed.scheme}://{self.username}:{self.password}@{parsed.netloc}"
    return self.url
```

**转换示例：**
```
原始:     http://proxy.example.com:8080
带认证:   http://user:pass@proxy.example.com:8080
```

#### 2. requests中的代理格式
```python
proxies = {
    'http': 'http://user:pass@proxy.example.com:8080',
    'https': 'http://user:pass@proxy.example.com:8080'
}

response = requests.get(url, proxies=proxies)
```

---

### 第六阶段：演示菜单

```
请选择测试功能:
  1. Basic Auth 认证      → demo_basic_auth()
  2. Bearer Token 认证   → demo_bearer_token()
  3. JWT 解码            → demo_jwt_decode()
  4. JWT 过期检测        → demo_jwt_decode()
  5. 代理池管理          → demo_proxy_pool()
  6. 代理轮换演示        → demo_proxy_rotation()
  7. 完整统计报告        → print_stats()
  8. 退出                → break
```

---

## 核心功能总结

### 1. 代理池管理
| 功能 | 方法 | 说明 |
|------|------|------|
| 添加代理 | `add_proxy()` | 支持带用户名密码的代理 |
| 获取代理 | `get_next_proxy()` | 轮换获取，跳过失败的 |
| 标记成功 | `mark_proxy_success()` | 更新成功次数和响应时间 |
| 标记失败 | `mark_proxy_failed()` | 加入失败集合 |
| 查看统计 | `get_stats()` | 成功率、可用数量等 |

### 2. 认证管理
| 功能 | 方法 | 说明 |
|------|------|------|
| Basic Auth | `create_basic_auth()` | 用户名密码Base64编码 |
| Bearer Token | `create_bearer_token()` | JWT放入Authorization头 |
| JWT解码 | `decode_jwt()` | 解析Header和Payload |
| 过期检测 | `is_token_expired()` | 检查exp字段 |

### 3. 爬虫整合
| 功能 | 说明 |
|------|------|
| 代理+认证 | 同时使用代理和认证 |
| 自动重试 | 失败后自动换代理 |
| 统计报告 | 请求次数、成功率和响应时间 |

---

## 实际使用方法

### 1. 使用真实代理
```python
from projectC import CrawlerWithProxy

crawler = CrawlerWithProxy()

# 添加代理（需要真实代理）
crawler.add_proxy("http://123.456.789.000:8080", "user", "pass")

# 发送请求
response = crawler.request_with_proxy(
    "https://httpbin.org/ip",
    auth_type='bearer',
    token='your_jwt_token'
)
```

### 2. 只使用认证
```python
response = crawler.request_with_proxy(
    "https://api.example.com/data",
    auth_type='basic',
    username='myuser',
    password='mypassword'
)
```

### 3. 查看统计
```python
stats = crawler.get_stats()
print(f"总请求: {stats['total']}")
print(f"成功率: {stats['success_rate']}")

crawler.proxy_manager.print_stats()
```

---

## 验收标准达成

| 标准 | 状态 | 说明 |
|------|------|------|
| 代理配置 | ✅ | 支持HTTP/HTTPS代理 |
| 代理认证 | ✅ | 支持用户名密码认证 |
| Token认证 | ✅ | Bearer Token自动附加 |
| JWT解析 | ✅ | 完整解码Header和Payload |
| 代理轮换 | ✅ | 自动轮换和失败重试 |

---

## 合规提醒

- 代理池功能为学习用途，需要真实代理时请使用合法来源
- 认证功能仅用于理解HTTP协议原理
- 实际使用时请遵守相关法律法规和网站robots协议

---

## 拓展方向

1. **代理健康检查**：定时检测代理可用性，自动移除失效代理
2. **响应时间优化**：根据响应时间选择最快代理
3. **代理来源**：对接免费代理API或代理服务商
4. **分布式代理**：支持多机器共享代理池
5. **代理权重**：根据成功率设置代理使用权重