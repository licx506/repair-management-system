#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试脚本：添加工作内容
使用API添加指定的工作内容
"""

import json
import sys
import os
import urllib.request
import urllib.error
import urllib.parse

# API基础URL
# BASE_URL = "http://localhost:8000/api"  # 默认地址
# 如果需要使用不同的地址，请取消下面的注释并修改
BASE_URL = "http://localhost:8458/api"  # 前端代理地址

# 登录并获取访问令牌
def get_access_token(username, password):
    """登录并获取访问令牌"""
    login_url = f"{BASE_URL}/auth/token"
    login_data = urllib.parse.urlencode({
        "username": username,
        "password": password
    }).encode('utf-8')

    try:
        req = urllib.request.Request(login_url, data=login_data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            token_data = json.loads(response_data)
            return token_data.get("access_token")
    except urllib.error.HTTPError as e:
        print(f"登录失败: HTTP错误 {e.code}")
        print(f"响应内容: {e.read().decode('utf-8')}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"登录失败: URL错误 {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"登录失败: {e}")
        sys.exit(1)

# 添加工作内容
def add_work_item(token, work_item_data):
    """添加工作内容"""
    url = f"{BASE_URL}/work-items/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"请求URL: {url}")
    print(f"请求头: {headers}")

    try:
        data = json.dumps(work_item_data).encode('utf-8')
        print(f"请求数据: {data.decode('utf-8')}")

        req = urllib.request.Request(url, data=data, method='POST')

        for key, value in headers.items():
            req.add_header(key, value)

        print("发送请求...")
        with urllib.request.urlopen(req) as response:
            print(f"响应状态码: {response.status}")
            response_data = response.read().decode('utf-8')
            print(f"响应数据: {response_data}")
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"添加工作内容失败: HTTP错误 {e.code}")
        print(f"请求URL: {url}")
        print(f"请求头: {headers}")
        print(f"请求数据: {work_item_data}")
        error_content = e.read().decode('utf-8')
        print(f"响应内容: {error_content}")

        # 尝试解析JSON错误
        try:
            error_json = json.loads(error_content)
            if 'detail' in error_json:
                print(f"错误详情: {error_json['detail']}")
        except:
            pass

        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"添加工作内容失败: URL错误 {e.reason}")
        print(f"请求URL: {url}")
        sys.exit(1)
    except Exception as e:
        print(f"添加工作内容失败: {e}")
        print(f"请求URL: {url}")
        print(f"请求头: {headers}")
        print(f"请求数据: {work_item_data}")
        sys.exit(1)

# 主函数
def main():
    # 从命令行参数或环境变量获取用户凭据
    import argparse

    parser = argparse.ArgumentParser(description='添加工作内容')
    parser.add_argument('--username', help='用户名')
    parser.add_argument('--password', help='密码')
    args = parser.parse_args()

    # 优先使用命令行参数，其次使用环境变量，最后使用默认值
    username = args.username or os.environ.get('API_USERNAME') or "admin"
    password = args.password or os.environ.get('API_PASSWORD') or "password"

    print(f"使用用户名: {username}")

    # 获取访问令牌
    print("正在登录...")
    token = get_access_token(username, password)
    if not token:
        print("登录失败，请检查用户名和密码")
        sys.exit(1)
    print("登录成功，获取到访问令牌")

    # 工作内容数据
    work_item_data = {
        "category": "通信线路",
        "project_number": "TXL2-001",
        "name": "挖、松填光（电）缆沟及接头坑 普通土",
        "unit": "百立方米",
        "skilled_labor_days": 0,
        "unskilled_labor_days": 39.38,
        "unit_price": 5
    }

    # 添加工作内容
    print("正在添加工作内容...")
    print(f"工作内容数据: {json.dumps(work_item_data, ensure_ascii=False, indent=2)}")

    result = add_work_item(token, work_item_data)

    print("工作内容添加成功!")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    main()
