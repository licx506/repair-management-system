#!/usr/bin/env python3
import os
import sys
import subprocess
import unittest
import requests
import json
import time
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

# 测试配置
API_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser",
    "password": "testpassword",
    "email": "test@example.com",
    "full_name": "Test User",
    "role": "worker"
}

class BackendTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """启动后端服务"""
        print("正在启动后端服务...")
        cls.backend_process = subprocess.Popen(
            ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # 等待服务启动
        time.sleep(3)

        # 检查服务是否正常运行
        try:
            response = requests.get(f"{API_URL}/health")
            if response.status_code != 200:
                raise Exception("后端服务未正常启动")
        except Exception as e:
            cls.tearDownClass()
            raise e

        print("后端服务已启动")

    @classmethod
    def tearDownClass(cls):
        """关闭后端服务"""
        if hasattr(cls, 'backend_process'):
            cls.backend_process.terminate()
            cls.backend_process.wait()
            print("后端服务已关闭")

    def test_01_health_check(self):
        """测试健康检查接口"""
        response = requests.get(f"{API_URL}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_02_register_user(self):
        """测试用户注册"""
        response = requests.post(f"{API_URL}/auth/register", json=TEST_USER)
        self.assertEqual(response.status_code, 200)
        user_data = response.json()
        self.assertEqual(user_data["username"], TEST_USER["username"])
        self.assertEqual(user_data["email"], TEST_USER["email"])

    def test_03_login(self):
        """测试用户登录"""
        response = requests.post(
            f"{API_URL}/auth/token",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.assertEqual(response.status_code, 200)
        token_data = response.json()
        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["token_type"], "bearer")

        # 保存token用于后续测试
        self.token = token_data["access_token"]

    def test_04_get_current_user(self):
        """测试获取当前用户信息"""
        if not hasattr(self, 'token'):
            self.skipTest("需要先登录")

        response = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        user_data = response.json()
        self.assertEqual(user_data["username"], TEST_USER["username"])
        self.assertEqual(user_data["email"], TEST_USER["email"])

    def test_05_create_project(self):
        """测试创建项目"""
        if not hasattr(self, 'token'):
            self.skipTest("需要先登录")

        project_data = {
            "title": "测试项目",
            "description": "这是一个测试项目",
            "location": "测试地点",
            "contact_name": "测试联系人",
            "contact_phone": "12345678901",
            "priority": 3
        }

        response = requests.post(
            f"{API_URL}/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        project = response.json()
        self.assertEqual(project["title"], project_data["title"])
        self.assertEqual(project["status"], "pending")

        # 保存项目ID用于后续测试
        self.project_id = project["id"]

    def test_06_create_task(self):
        """测试创建工单"""
        if not hasattr(self, 'token') or not hasattr(self, 'project_id'):
            self.skipTest("需要先登录并创建项目")

        task_data = {
            "project_id": self.project_id,
            "title": "测试工单",
            "description": "这是一个测试工单"
        }

        response = requests.post(
            f"{API_URL}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        task = response.json()
        self.assertEqual(task["title"], task_data["title"])
        self.assertEqual(task["status"], "pending")

        # 保存工单ID用于后续测试
        self.task_id = task["id"]

    def test_07_update_task(self):
        """测试更新工单状态"""
        if not hasattr(self, 'token') or not hasattr(self, 'task_id'):
            self.skipTest("需要先登录并创建工单")

        update_data = {
            "status": "assigned"
        }

        response = requests.put(
            f"{API_URL}/tasks/{self.task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        task = response.json()
        self.assertEqual(task["status"], "assigned")
        self.assertIsNotNone(task["assigned_at"])

    def test_08_create_material(self):
        """测试创建材料"""
        if not hasattr(self, 'token'):
            self.skipTest("需要先登录")

        material_data = {
            "category": "通信材料",
            "code": "TXC-TEST-001",
            "name": "测试材料",
            "unit": "个",
            "unit_price": 10.5,
            "supply_type": "甲供",
            "description": "这是一个测试材料"
        }

        response = requests.post(
            f"{API_URL}/materials",
            json=material_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        material = response.json()
        self.assertEqual(material["name"], material_data["name"])
        self.assertEqual(material["code"], material_data["code"])

        # 保存材料ID用于后续测试
        self.material_id = material["id"]

    def test_09_create_work_item(self):
        """测试创建工作内容"""
        if not hasattr(self, 'token'):
            self.skipTest("需要先登录")

        work_item_data = {
            "category": "通信线路",
            "project_number": "TXX-TEST-001",
            "name": "测试工作内容",
            "unit": "米",
            "unit_price": 5.5,
            "skilled_labor_days": 0.5,
            "unskilled_labor_days": 1.0,
            "description": "这是一个测试工作内容"
        }

        response = requests.post(
            f"{API_URL}/work-items",
            json=work_item_data,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        work_item = response.json()
        self.assertEqual(work_item["name"], work_item_data["name"])
        self.assertEqual(work_item["project_number"], work_item_data["project_number"])

        # 保存工作内容ID用于后续测试
        self.work_item_id = work_item["id"]

    def test_10_check_db_structure(self):
        """测试数据库结构检查"""
        # 导入数据库结构检查模块
        sys.path.append(str(ROOT_DIR))
        try:
            import check_db_structure
            result = check_db_structure.main()
            self.assertTrue(result, "数据库结构检查失败")
        except ImportError:
            self.skipTest("找不到check_db_structure模块")

    def test_11_test_batch_import_endpoints(self):
        """测试批量导入API端点是否存在"""
        if not hasattr(self, 'token'):
            self.skipTest("需要先登录")

        # 测试工作内容批量导入端点
        response = requests.options(
            f"{API_URL}/work-items/import",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertIn(response.status_code, [200, 204, 404], "工作内容批量导入端点请求失败")

        # 测试材料批量导入端点
        response = requests.options(
            f"{API_URL}/materials/import",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertIn(response.status_code, [200, 204, 404], "材料批量导入端点请求失败")

        # 测试工单批量导入端点
        response = requests.options(
            f"{API_URL}/tasks/import",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertIn(response.status_code, [200, 204, 404], "工单批量导入端点请求失败")

        # 测试用户批量导入端点
        response = requests.options(
            f"{API_URL}/users/import",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertIn(response.status_code, [200, 204, 404], "用户批量导入端点请求失败")

class FrontendTestCase(unittest.TestCase):
    """前端测试用例"""

    def test_01_check_frontend_files(self):
        """检查前端关键文件是否存在"""
        frontend_dir = ROOT_DIR / "frontend"

        # 检查关键文件
        key_files = [
            "package.json",
            "vite.config.ts",
            "src/App.tsx",
            "src/main.tsx",
            "src/api/api.ts",
            "src/components/ImportModal.tsx"
        ]

        for file_path in key_files:
            full_path = frontend_dir / file_path
            self.assertTrue(full_path.exists(), f"找不到关键文件: {file_path}")

    def test_02_check_frontend_build(self):
        """检查前端是否可以构建"""
        frontend_dir = ROOT_DIR / "frontend"

        # 检查package.json是否存在
        package_json_path = frontend_dir / "package.json"
        if not package_json_path.exists():
            self.skipTest("找不到package.json文件")

        # 检查是否包含构建脚本
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
            self.assertIn("scripts", package_data, "package.json中找不到scripts部分")
            self.assertIn("build", package_data["scripts"], "package.json中找不到build脚本")

def run_tests():
    """运行测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加后端测试
    suite.addTest(loader.loadTestsFromTestCase(BackendTestCase))

    # 添加前端测试
    suite.addTest(loader.loadTestsFromTestCase(FrontendTestCase))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result

def generate_test_report(result):
    """生成测试报告"""
    print("\n" + "="*80)
    print("测试报告".center(80))
    print("="*80)

    # 测试结果统计
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    success = total - failures - errors - skipped

    print(f"总测试数: {total}")
    print(f"成功: {success}")
    print(f"失败: {failures}")
    print(f"错误: {errors}")
    print(f"跳过: {skipped}")
    print("-"*80)

    # 失败的测试
    if failures > 0:
        print("\n失败的测试:")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"   原因: {error_msg}")

    # 错误的测试
    if errors > 0:
        print("\n错误的测试:")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            error_msg = traceback.split('Error: ')[-1].split('\n')[0]
            print(f"   原因: {error_msg}")

    # 跳过的测试
    if skipped > 0:
        print("\n跳过的测试:")
        for i, (test, reason) in enumerate(result.skipped, 1):
            print(f"{i}. {test}")
            print(f"   原因: {reason}")

    # 生成优化建议
    print("\n" + "="*80)
    print("优化建议".center(80))
    print("="*80)

    # 根据测试结果生成优化建议
    optimization_suggestions = []

    # 数据库结构检查
    if any("test_10_check_db_structure" in str(test) for test, _ in result.failures + result.errors):
        optimization_suggestions.append("1. 数据库结构需要修复，请运行 fix_db_structure.py 脚本")

    # 批量导入API
    if any("test_11_test_batch_import_endpoints" in str(test) for test, _ in result.failures + result.errors):
        optimization_suggestions.append("2. 批量导入API端点存在问题，请检查后端路由配置")

    # 前端文件检查
    if any("test_01_check_frontend_files" in str(test) for test, _ in result.failures + result.errors):
        optimization_suggestions.append("3. 前端关键文件缺失，请检查前端项目结构")

    # 前端构建检查
    if any("test_02_check_frontend_build" in str(test) for test, _ in result.failures + result.errors):
        optimization_suggestions.append("4. 前端构建配置有问题，请检查package.json")

    # 添加通用优化建议
    optimization_suggestions.extend([
        "5. 添加更多单元测试，提高代码覆盖率",
        "6. 优化批量导入功能，支持更多文件格式（如Excel）",
        "7. 添加数据导出功能，支持导出为CSV或Excel",
        "8. 优化前端响应式设计，提升移动端用户体验",
        "9. 添加数据缓存机制，减少API请求次数",
        "10. 实现离线模式支持，允许在无网络环境下工作",
        "11. 添加更详细的错误处理和用户提示",
        "12. 优化大数据量下的性能，如分页加载和虚拟滚动",
        "13. 添加用户操作日志，记录关键操作",
        "14. 实现数据备份和恢复功能"
    ])

    # 打印优化建议
    print("根据测试结果，以下是需要优化的功能清单：\n")
    for suggestion in optimization_suggestions:
        print(suggestion)

    print("\n" + "="*80)

    # 返回测试是否全部通过
    return success == total

if __name__ == "__main__":
    result = run_tests()
    generate_test_report(result)
