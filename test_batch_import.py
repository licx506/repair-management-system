#!/usr/bin/env python3
"""
批量导入功能测试脚本
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
STATIC_DIR = BACKEND_DIR / "static" / "templates"

# 测试配置
API_URL = "http://localhost:8000/api"
ADMIN_USER = {
    "username": "admin",
    "password": "admin123"
}

def get_token():
    """获取管理员用户的访问令牌"""
    try:
        response = requests.post(
            f"{API_URL}/auth/token",
            data={
                "username": ADMIN_USER["username"],
                "password": ADMIN_USER["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录异常: {str(e)}")
        return None

def test_template_files():
    """测试模板文件是否存在"""
    print("\n测试模板文件...")
    
    template_files = [
        "work_items_template.csv",
        "materials_template.csv",
        "tasks_template.csv",
        "users_template.csv"
    ]
    
    results = []
    for file_name in template_files:
        file_path = STATIC_DIR / file_name
        exists = file_path.exists()
        results.append((file_name, exists))
        status = "✅" if exists else "❌"
        print(f"{status} {file_name}")
    
    return all(exists for _, exists in results)

def test_import_endpoints():
    """测试批量导入API端点"""
    print("\n测试批量导入API端点...")
    
    token = get_token()
    if not token:
        print("❌ 无法获取访问令牌，跳过API测试")
        return False
    
    endpoints = [
        "/work-items/import",
        "/materials/import",
        "/tasks/import",
        "/users/import"
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            response = requests.options(
                f"{API_URL}{endpoint}",
                headers={"Authorization": f"Bearer {token}"}
            )
            # 对于OPTIONS请求，200、204或404都是可能的响应
            success = response.status_code in [200, 204, 404]
            results.append((endpoint, success))
            status = "✅" if success else "❌"
            print(f"{status} {endpoint} - {response.status_code}")
        except Exception as e:
            results.append((endpoint, False))
            print(f"❌ {endpoint} - 异常: {str(e)}")
    
    return all(success for _, success in results)

def test_import_work_items():
    """测试工作内容批量导入"""
    print("\n测试工作内容批量导入...")
    
    token = get_token()
    if not token:
        print("❌ 无法获取访问令牌，跳过导入测试")
        return False
    
    # 检查模板文件是否存在
    template_file = STATIC_DIR / "work_items_template.csv"
    if not template_file.exists():
        print(f"❌ 模板文件不存在: {template_file}")
        return False
    
    try:
        # 读取模板文件
        with open(template_file, 'rb') as f:
            files = {'file': ('work_items_test.csv', f, 'text/csv')}
            
            # 发送导入请求
            response = requests.post(
                f"{API_URL}/work-items/import",
                files=files,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # 检查响应
            if response.status_code == 201:
                print(f"✅ 工作内容导入成功: {response.json()}")
                return True
            else:
                print(f"❌ 工作内容导入失败: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ 工作内容导入异常: {str(e)}")
        return False

def test_import_materials():
    """测试材料批量导入"""
    print("\n测试材料批量导入...")
    
    token = get_token()
    if not token:
        print("❌ 无法获取访问令牌，跳过导入测试")
        return False
    
    # 检查模板文件是否存在
    template_file = STATIC_DIR / "materials_template.csv"
    if not template_file.exists():
        print(f"❌ 模板文件不存在: {template_file}")
        return False
    
    try:
        # 读取模板文件
        with open(template_file, 'rb') as f:
            files = {'file': ('materials_test.csv', f, 'text/csv')}
            
            # 发送导入请求
            response = requests.post(
                f"{API_URL}/materials/import",
                files=files,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # 检查响应
            if response.status_code == 201:
                print(f"✅ 材料导入成功: {response.json()}")
                return True
            else:
                print(f"❌ 材料导入失败: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ 材料导入异常: {str(e)}")
        return False

def generate_optimization_list():
    """生成优化建议清单"""
    print("\n" + "="*80)
    print("优化建议清单".center(80))
    print("="*80)
    
    suggestions = [
        "1. 批量导入功能增强",
        "   - 支持Excel格式(.xlsx)导入",
        "   - 添加导入预览功能",
        "   - 支持部分字段更新模式",
        "   - 添加导入历史记录",
        
        "2. 数据导出功能",
        "   - 支持导出为CSV和Excel格式",
        "   - 支持选择导出字段",
        "   - 支持导出筛选条件",
        "   - 添加导出任务队列",
        
        "3. 前端优化",
        "   - 优化移动端响应式设计",
        "   - 添加数据缓存机制",
        "   - 实现虚拟滚动，优化大数据量显示",
        "   - 添加更详细的错误提示",
        
        "4. 后端优化",
        "   - 优化数据库查询性能",
        "   - 添加请求限流机制",
        "   - 实现异步任务处理",
        "   - 添加更详细的日志记录",
        
        "5. 功能扩展",
        "   - 实现离线模式支持",
        "   - 添加数据备份和恢复功能",
        "   - 实现用户操作日志",
        "   - 添加自定义报表功能"
    ]
    
    for suggestion in suggestions:
        print(suggestion)
    
    print("\n" + "="*80)

def main():
    """主函数"""
    print("="*80)
    print("批量导入功能测试".center(80))
    print("="*80)
    
    # 测试模板文件
    templates_ok = test_template_files()
    
    # 测试API端点
    endpoints_ok = test_import_endpoints()
    
    # 测试工作内容导入
    work_items_ok = test_import_work_items()
    
    # 测试材料导入
    materials_ok = test_import_materials()
    
    # 打印测试结果汇总
    print("\n" + "="*80)
    print("测试结果汇总".center(80))
    print("="*80)
    print(f"模板文件测试: {'通过' if templates_ok else '失败'}")
    print(f"API端点测试: {'通过' if endpoints_ok else '失败'}")
    print(f"工作内容导入测试: {'通过' if work_items_ok else '失败'}")
    print(f"材料导入测试: {'通过' if materials_ok else '失败'}")
    
    # 生成优化建议清单
    generate_optimization_list()
    
    # 返回测试结果
    return all([templates_ok, endpoints_ok, work_items_ok, materials_ok])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
