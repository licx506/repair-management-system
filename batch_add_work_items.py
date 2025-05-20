#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量添加工作内容测试脚本
可以从CSV文件或命令行参数批量添加工作内容
"""

import json
import sys
import os
import csv
import argparse
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse

# API基础URL
BASE_URL = "http://localhost:8000/api"  # 默认地址
# 如果需要使用不同的地址，请取消下面的注释并修改
# BASE_URL = "http://localhost:8458/api"  # 前端代理地址

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
        return None
    except urllib.error.URLError as e:
        print(f"登录失败: URL错误 {e.reason}")
        return None
    except Exception as e:
        print(f"登录失败: {e}")
        return None

# 添加工作内容
def add_work_item(token, work_item_data):
    """添加工作内容"""
    url = f"{BASE_URL}/work-items/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        data = json.dumps(work_item_data).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')

        for key, value in headers.items():
            req.add_header(key, value)

        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"添加工作内容失败: HTTP错误 {e.code}")
        print(f"响应内容: {e.read().decode('utf-8')}")
        return None
    except urllib.error.URLError as e:
        print(f"添加工作内容失败: URL错误 {e.reason}")
        return None
    except Exception as e:
        print(f"添加工作内容失败: {e}")
        return None

# 从CSV文件加载工作内容
def load_work_items_from_csv(csv_file):
    """从CSV文件加载工作内容数据"""
    work_items = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 转换数值字段
                if 'skilled_labor_days' in row:
                    row['skilled_labor_days'] = float(row['skilled_labor_days'])
                if 'unskilled_labor_days' in row:
                    row['unskilled_labor_days'] = float(row['unskilled_labor_days'])
                if 'unit_price' in row:
                    row['unit_price'] = float(row['unit_price'])

                work_items.append(row)

        return work_items
    except Exception as e:
        print(f"加载CSV文件失败: {e}")
        return []

# 保存结果到CSV文件
def save_results_to_csv(results, output_file):
    """保存结果到CSV文件"""
    if not results:
        print("没有结果可保存")
        return

    try:
        fieldnames = results[0].keys()

        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

        print(f"结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存结果失败: {e}")

# 主函数
def main():
    parser = argparse.ArgumentParser(description='批量添加工作内容')
    parser.add_argument('--username', help='用户名')
    parser.add_argument('--password', help='密码')
    parser.add_argument('--csv', help='CSV文件路径')
    parser.add_argument('--output', help='输出结果的CSV文件路径')
    parser.add_argument('--single', action='store_true', help='添加单个工作内容')
    parser.add_argument('--api-url', help='API基础URL，例如 http://localhost:8000/api')

    args = parser.parse_args()

    # 优先使用命令行参数，其次使用环境变量，最后使用默认值
    username = args.username or os.environ.get('API_USERNAME') or "admin"
    password = args.password or os.environ.get('API_PASSWORD') or "password"

    # 如果指定了API URL，则更新BASE_URL
    if args.api_url:
        global BASE_URL
        BASE_URL = args.api_url
        print(f"使用API URL: {BASE_URL}")

    print(f"使用用户名: {username}")

    # 获取访问令牌
    print("正在登录...")
    token = get_access_token(username, password)

    if not token:
        print("登录失败，无法获取访问令牌")
        print("请检查用户名和密码是否正确")
        print("可以使用 --username 和 --password 参数指定用户名和密码")
        print("例如: python batch_add_work_items.py --username admin --password yourpassword --single")
        sys.exit(1)

    print("登录成功，获取到访问令牌")

    results = []

    if args.single:
        # 添加单个工作内容
        work_item_data = {
            "category": "通信线路",
            "project_number": "TXL2-001",
            "name": "挖、松填光（电）缆沟及接头坑 普通土",
            "unit": "百立方米",
            "skilled_labor_days": 0,
            "unskilled_labor_days": 39.38,
            "unit_price": 5
        }

        print("正在添加工作内容...")
        print(f"工作内容数据: {json.dumps(work_item_data, ensure_ascii=False, indent=2)}")

        result = add_work_item(token, work_item_data)

        if result:
            print("工作内容添加成功!")
            print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            results.append(result)
        else:
            print("工作内容添加失败")

    elif args.csv:
        # 从CSV文件批量添加
        work_items = load_work_items_from_csv(args.csv)

        if not work_items:
            print("没有找到工作内容数据")
            sys.exit(1)

        print(f"从CSV文件加载了 {len(work_items)} 个工作内容")

        for i, item in enumerate(work_items):
            print(f"正在添加第 {i+1}/{len(work_items)} 个工作内容...")
            print(f"工作内容数据: {json.dumps(item, ensure_ascii=False, indent=2)}")

            result = add_work_item(token, item)

            if result:
                print("工作内容添加成功!")
                results.append(result)
            else:
                print("工作内容添加失败")

    else:
        print("请指定 --csv 参数提供CSV文件，或使用 --single 添加单个工作内容")
        sys.exit(1)

    # 保存结果
    if args.output and results:
        save_results_to_csv(results, args.output)

if __name__ == "__main__":
    main()
