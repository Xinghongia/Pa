"""
浏览器抓包分析流程 - 05_network_analysis.py

学习内容：
1. 如何使用浏览器开发者工具分析请求
2. 识别API接口的特征
3. 提取请求参数的方法
4. 复现AJAX请求

运行环境：
python 05_network_analysis.py
"""

print("=" * 60)
print("浏览器开发者工具 - 抓包分析指南")
print("=" * 60)

guide = """
【目标】分析 https://example.com/users 页面，找出数据来源

步骤1: 打开Network面板
-----------------------------
1. 按F12打开开发者工具
2. 点击 Network（网络）标签
3. 勾选 "XHR" 过滤（只显示AJAX请求）
4. 勾选 "Preserve log"（保留日志）

步骤2: 触发数据加载
-----------------------------
1. 访问目标页面 https://example.com/users
2. 滚动页面触发加载（如果需要）
3. 观察Network面板新增的请求

步骤3: 分析XHR请求
-----------------------------
找到类似这样的请求：
  Name: users?page=1&limit=20
  Status: 200
  Type: xhr
  Time: 150ms

点击请求查看详情：

【Headers - General】
  Request URL: https://api.example.com/users?page=1&limit=20
  Request Method: GET
  Status Code: 200 OK

【Headers - Request Headers】
  Accept: application/json
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
  Referer: https://example.com/users
  User-Agent: Mozilla/5.0...

【Headers - Query String Parameters】
  page: 1
  limit: 20

【Response / Preview】
  查看JSON响应数据

步骤4: 识别API特征
-----------------------------
特征1: URL包含 /api/ 或 .json
  https://api.example.com/users
  https://example.com/data/users.json

特征2: 返回JSON格式
  Content-Type: application/json

特征3: Type显示为 xhr
  不是 document (HTML) 或 script (JS)

步骤5: 提取请求参数
-----------------------------
固定参数（直接使用）:
  - page, limit 等分页参数

动态参数（需要生成）:
  - timestamp: int(time.time())
  - token: 从cookie或页面提取
  - sign: 需要分析JS生成逻辑

步骤6: 复现请求
-----------------------------
使用Python复现（见下方代码示例）
"""


code_example = '''
import requests

headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...',
    'Referer': 'https://example.com/users',
    'User-Agent': 'Mozilla/5.0...'
}

response = requests.get(
    'https://api.example.com/users',
    params={'page': 1, 'limit': 20},
    headers=headers
)

data = response.json()
print(data)
'''


def main():
    print(guide)
    print("\n【Python复现代码】:")
    print(code_example)


if __name__ == "__main__":
    main()