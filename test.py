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

def run_tests():
    """运行测试"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()
