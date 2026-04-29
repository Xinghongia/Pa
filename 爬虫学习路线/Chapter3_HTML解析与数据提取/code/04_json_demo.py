"""
JSON数据提取 - 04_json_demo.py

学习内容：
1. JSON基础解析
2. JSONPath使用
3. 安全获取嵌套数据
4. 大JSON文件流式处理

运行环境：
python 04_json_demo.py
"""

import json
from jsonpath import jsonpath


api_response = {
    "code": 200,
    "message": "success",
    "data": {
        "total": 3,
        "page": 1,
        "page_size": 20,
        "users": [
            {
                "id": 1001,
                "name": "张三",
                "email": "zhangsan@example.com",
                "roles": ["admin", "user"],
                "profile": {
                    "age": 28,
                    "city": "北京",
                    "phone": "13800138000"
                }
            },
            {
                "id": 1002,
                "name": "李四",
                "email": "lisi@example.com",
                "roles": ["user"],
                "profile": {
                    "age": 25,
                    "city": "上海",
                    "phone": "13900139000"
                }
            },
            {
                "id": 1003,
                "name": "王五",
                "email": "wangwu@example.com",
                "roles": ["user", "vip"],
                "profile": {
                    "age": 30,
                    "city": "深圳",
                    "phone": "13700137000"
                }
            }
        ]
    },
    "timestamp": 1704067200
}


def basic_json_parse():
    print("=" * 60)
    print("1. 基础JSON解析")
    print("=" * 60)

    print("\n【1.1 嵌套访问】:")
    print(f"  code: {api_response['code']}")
    print(f"  total: {api_response['data']['total']}")
    print(f"  第一个用户: {api_response['data']['users'][0]['name']}")

    print("\n【1.2 遍历数组】:")
    for user in api_response['data']['users']:
        print(f"  - {user['name']}: {user['email']}")


def jsonpath_usage():
    print("\n" + "=" * 60)
    print("2. JSONPath使用")
    print("=" * 60)

    print("\n【2.1 $】访问根节点:")
    result = jsonpath(api_response, '$.code')
    print(f"  $.code: {result}")

    print("\n【2.2 子节点】$.data.total:")
    result = jsonpath(api_response, '$.data.total')
    print(f"  结果: {result}")

    print("\n【2.3 数组】$.data.users[0]:")
    result = jsonpath(api_response, '$.data.users[0]')
    print(f"  结果: {result[0]['name'] if result else '无'}")

    print("\n【2.4 [*]】所有用户名称:")
    result = jsonpath(api_response, '$.data.users[*].name')
    print(f"  结果: {result}")

    print("\n【2.5 [?( @.key)]】过滤age>=28的用户:")
    result = jsonpath(api_response, '$.data.users[?(@.profile.age>=28)]')
    for user in result:
        print(f"  - {user['name']}, age: {user['profile']['age']}")

    print("\n【2.6 ..key】递归查找所有name:")
    result = jsonpath(api_response, '$..name')
    print(f"  结果: {result}")

    print("\n【2.7 [?()]】有VIP角色的用户:")
    result = jsonpath(api_response, '$.data.users[?(\'vip\' in @.roles)]')
    for user in result:
        print(f"  - {user['name']}: {user['roles']}")

    print("\n【2.8 length】用户数量:")
    result = jsonpath(api_response, '$.data.users.length')
    print(f"  结果: {result[0] if result else 0}")


def safe_access():
    print("\n" + "=" * 60)
    print("3. 安全访问嵌套数据")
    print("=" * 60)

    problem_data = {
        "user": None,
        "order": {},
        "normal": {"name": "测试"}
    }

    print("\n【3.1 不安全访问】:")
    try:
        pass
    except (TypeError, KeyError) as e:
        print(f"  错误: {type(e).__name__}")

    print("\n【3.2 get()链式调用】:")
    user = problem_data.get('user')
    name = (user or {}).get('name', '默认值')
    print(f"  user.name: {name}")

    name = problem_data.get('normal', {}).get('name', '默认值')
    print(f"  normal.name: {name}")

    print("\n【3.3 jsonpath安全访问】:")
    result = jsonpath(problem_data, '$.user.name')
    print(f"  $.user.name: {result[0] if result else '无'}")

    result = jsonpath(problem_data, '$.normal.name')
    print(f"  $.normal.name: {result[0] if result else '无'}")


def save_load_json():
    print("\n" + "=" * 60)
    print("4. JSON文件读写")
    print("=" * 60)

    filename = 'test_data.json'

    print("\n【4.1 写入JSON】:")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(api_response, f, ensure_ascii=False, indent=2)
    print(f"  已保存到: {filename}")

    print("\n【4.2 读取JSON】:")
    with open(filename, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    print(f"  读取成功，code: {loaded_data['code']}")

    import os
    os.remove(filename)
    print("\n  已清理测试文件")


def main():
    basic_json_parse()
    jsonpath_usage()
    safe_access()
    save_load_json()

    print("\n" + "=" * 60)
    print("JSON数据提取演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()