#!/usr/bin/env python3
"""
维修项目管理系统环境检测脚本
用于检测当前环境是否满足系统运行要求
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def log_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def run_command(command, capture_output=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def check_python():
    """检查Python环境"""
    log_info("检查Python环境...")

    # 检查Python版本
    success, stdout, stderr = run_command("python3 --version")
    if success:
        version = stdout.split()[1]
        major, minor = map(int, version.split('.')[:2])
        if major >= 3 and minor >= 8:
            log_success(f"Python版本: {version} ✓")
        else:
            log_warning(f"Python版本: {version} (建议3.8+)")
    else:
        log_error("Python3未安装")
        return False

    # 检查pip
    success, stdout, stderr = run_command("python3 -m pip --version")
    if success:
        log_success(f"pip已安装 ✓")
    else:
        log_error("pip未安装")
        return False

    return True

def check_nodejs():
    """检查Node.js环境"""
    log_info("检查Node.js环境...")

    # 检查Node.js版本
    success, stdout, stderr = run_command("node --version")
    if success:
        version = stdout.strip()
        major_version = int(version[1:].split('.')[0])
        if major_version >= 16:
            log_success(f"Node.js版本: {version} ✓")
        else:
            log_warning(f"Node.js版本: {version} (建议16+)")
    else:
        log_error("Node.js未安装")
        return False

    # 检查npm
    success, stdout, stderr = run_command("npm --version")
    if success:
        version = stdout.strip()
        log_success(f"npm版本: {version} ✓")
    else:
        log_error("npm未安装")
        return False

    return True

def check_system_dependencies():
    """检查系统依赖"""
    log_info("检查系统依赖...")

    dependencies = ['git', 'curl', 'wget']
    all_ok = True

    for dep in dependencies:
        success, stdout, stderr = run_command(f"which {dep}")
        if success:
            log_success(f"{dep}已安装 ✓")
        else:
            log_warning(f"{dep}未安装")
            all_ok = False

    return all_ok

def check_python_dependencies():
    """检查Python依赖"""
    log_info("检查Python依赖...")

    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'python-jose',
        'passlib',
        'python-multipart'
    ]

    missing_packages = []

    for package in required_packages:
        import_name = package.replace("-", "_")
        success, stdout, stderr = run_command(f"python3 -c 'import {import_name}'")
        if success:
            log_success(f"{package}已安装 ✓")
        else:
            log_warning(f"{package}未安装")
            missing_packages.append(package)

    if missing_packages:
        log_info("可以运行以下命令安装缺失的Python依赖:")
        log_info(f"python3 -m pip install {' '.join(missing_packages)}")
        return False

    return True

def check_frontend_dependencies():
    """检查前端依赖"""
    log_info("检查前端依赖...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        log_warning("frontend目录不存在")
        return False

    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        log_warning("package.json文件不存在")
        return False

    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        log_warning("node_modules目录不存在，需要运行 npm install")
        return False

    # 检查关键依赖
    try:
        with open(package_json, 'r', encoding='utf-8') as f:
            package_data = json.load(f)

        dependencies = package_data.get('dependencies', {})
        required_deps = ['react', 'antd', 'axios', 'react-router-dom']

        for dep in required_deps:
            if dep in dependencies:
                log_success(f"{dep}已配置 ✓")
            else:
                log_warning(f"{dep}未配置")

        log_success("前端依赖检查完成 ✓")
        return True

    except Exception as e:
        log_error(f"检查前端依赖时出错: {e}")
        return False

def check_project_structure():
    """检查项目结构"""
    log_info("检查项目结构...")

    required_files = [
        "requirements.txt",
        "run.py",
        "backend/main.py",
        "backend/database.py",
        "frontend/package.json",
        "frontend/vite.config.ts"
    ]

    required_dirs = [
        "backend",
        "frontend",
        "backend/models",
        "backend/routers",
        "backend/schemas",
        "frontend/src"
    ]

    all_ok = True

    # 检查文件
    for file_path in required_files:
        if Path(file_path).exists():
            log_success(f"{file_path} ✓")
        else:
            log_error(f"{file_path} 不存在")
            all_ok = False

    # 检查目录
    for dir_path in required_dirs:
        if Path(dir_path).exists() and Path(dir_path).is_dir():
            log_success(f"{dir_path}/ ✓")
        else:
            log_error(f"{dir_path}/ 不存在")
            all_ok = False

    return all_ok

def check_ports():
    """检查端口占用情况"""
    log_info("检查端口占用情况...")

    ports = [8000, 8458]

    for port in ports:
        # 检查端口是否被占用
        success, stdout, stderr = run_command(f"netstat -tlnp 2>/dev/null | grep :{port} || ss -tlnp 2>/dev/null | grep :{port}")
        if success and stdout:
            log_warning(f"端口 {port} 已被占用")
            log_info(f"占用详情: {stdout}")
        else:
            log_success(f"端口 {port} 可用 ✓")

def check_database():
    """检查数据库"""
    log_info("检查数据库...")

    db_file = Path("backend/repair_management.db")
    if db_file.exists():
        log_success("数据库文件存在 ✓")

        # 检查数据库是否可以连接
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()

            if tables:
                log_success(f"数据库包含 {len(tables)} 个表 ✓")
            else:
                log_warning("数据库为空，可能需要初始化")

        except Exception as e:
            log_error(f"数据库连接失败: {e}")
            return False
    else:
        log_warning("数据库文件不存在，首次运行时会自动创建")

    return True

def generate_report():
    """生成环境检测报告"""
    log_info("生成环境检测报告...")

    checks = [
        ("Python环境", check_python),
        ("Node.js环境", check_nodejs),
        ("系统依赖", check_system_dependencies),
        ("项目结构", check_project_structure),
        ("Python依赖", check_python_dependencies),
        ("前端依赖", check_frontend_dependencies),
        ("端口检查", check_ports),
        ("数据库检查", check_database)
    ]

    results = {}

    print("\n" + "="*60)
    print("环境检测报告")
    print("="*60)

    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 30)
        try:
            result = check_func()
            results[name] = result
        except Exception as e:
            log_error(f"检查 {name} 时出错: {e}")
            results[name] = False

    print("\n" + "="*60)
    print("检测结果汇总:")
    print("="*60)

    all_passed = True
    for name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{name}: {status}{Colors.NC}")
        if not result:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        log_success("所有检查都通过！系统可以正常运行。")
        print("\n启动系统:")
        print("python3 run.py")
    else:
        log_warning("部分检查未通过，建议运行初始化脚本:")
        print("bash init_environment.sh")
    print("="*60)

def main():
    """主函数"""
    print("维修项目管理系统环境检测")
    print("="*60)

    # 检查是否在项目根目录
    if not Path("run.py").exists():
        log_error("请在项目根目录运行此脚本")
        sys.exit(1)

    generate_report()

if __name__ == "__main__":
    main()
