#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统管理工具
整合所有管理脚本，提供统一的功能选择菜单
首次运行时会检查系统环境并自动安装所需依赖
"""

import os
import sys
import subprocess
import argparse
import logging
import shutil
import datetime
import glob
import re
from pathlib import Path
import time
from datetime import datetime, timedelta
import json
import platform

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
LOGS_DIR = ROOT_DIR / "logs"
CONFIG_DIR = ROOT_DIR / ".config"

# 创建日志目录和配置目录
LOGS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# 配置文件路径
FIRST_RUN_FLAG_FILE = CONFIG_DIR / "first_run_completed"
ENV_CHECK_FILE = CONFIG_DIR / "env_check.json"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("system_manager")

def is_first_run():
    """检查是否首次运行"""
    return not FIRST_RUN_FLAG_FILE.exists()

def mark_first_run_completed():
    """标记首次运行已完成"""
    with open(FIRST_RUN_FLAG_FILE, 'w') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("首次运行标记已设置")

def save_env_check_result(result):
    """保存环境检查结果"""
    with open(ENV_CHECK_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("环境检查结果已保存")

def load_env_check_result():
    """加载环境检查结果"""
    if not ENV_CHECK_FILE.exists():
        return {}
    try:
        with open(ENV_CHECK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载环境检查结果失败: {e}")
        return {}

def run_command(command, cwd=None, capture_output=True):
    """运行命令并返回结果"""
    try:
        logger.info(f"执行命令: {command}")
        if capture_output:
            result = subprocess.run(
                command,
                cwd=cwd or ROOT_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(
                command,
                cwd=cwd or ROOT_DIR,
                shell=True
            )
            return result.returncode == 0, "", ""
    except Exception as e:
        logger.error(f"执行命令失败: {e}")
        return False, "", str(e)

def check_python_version():
    """检查Python版本"""
    logger.info("检查Python版本...")
    required_version = (3, 8)
    current_version = sys.version_info

    if current_version.major < required_version[0] or (current_version.major == required_version[0] and current_version.minor < required_version[1]):
        logger.warning(f"Python版本不满足要求: 当前 {current_version.major}.{current_version.minor}, 需要 {required_version[0]}.{required_version[1]}+")
        return False, f"Python {required_version[0]}.{required_version[1]}+"

    logger.info(f"Python版本检查通过: {current_version.major}.{current_version.minor}.{current_version.micro}")
    return True, f"{current_version.major}.{current_version.minor}.{current_version.micro}"

def check_pip():
    """检查pip是否可用"""
    logger.info("检查pip...")
    success, stdout, stderr = run_command("pip --version")

    if not success:
        logger.warning("pip未安装或不可用")
        return False, None

    logger.info(f"pip检查通过: {stdout.strip()}")
    return True, stdout.strip()

def check_node():
    """检查Node.js是否可用"""
    logger.info("检查Node.js...")
    success, stdout, stderr = run_command("node --version")

    if not success:
        logger.warning("Node.js未安装或不可用")
        return False, None

    version = stdout.strip()
    logger.info(f"Node.js检查通过: {version}")
    return True, version

def check_npm():
    """检查npm是否可用"""
    logger.info("检查npm...")
    success, stdout, stderr = run_command("npm --version")

    if not success:
        logger.warning("npm未安装或不可用")
        return False, None

    version = stdout.strip()
    logger.info(f"npm检查通过: {version}")
    return True, version

def check_python_dependencies():
    """检查Python依赖"""
    logger.info("检查Python依赖...")
    requirements_file = ROOT_DIR / "requirements.txt"

    if not requirements_file.exists():
        logger.warning(f"requirements.txt文件不存在: {requirements_file}")
        return False, []

    # 获取已安装的包
    success, stdout, stderr = run_command("pip freeze")
    if not success:
        logger.warning("无法获取已安装的Python包")
        return False, []

    installed_packages = {line.split('==')[0].lower(): line for line in stdout.strip().split('\n') if line}

    # 读取requirements.txt
    with open(requirements_file, 'r') as f:
        required_packages = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

    # 检查缺失的包
    missing_packages = []
    for package in required_packages:
        if '==' in package:
            package_name = package.split('==')[0].lower()
            package_version = package.split('==')[1]
            if package_name not in installed_packages:
                missing_packages.append(package)
            # 可以进一步检查版本，但这里简化处理
        else:
            package_name = package.lower()
            if package_name not in installed_packages:
                missing_packages.append(package)

    if missing_packages:
        logger.warning(f"缺少以下Python依赖: {', '.join(missing_packages)}")
        return False, missing_packages

    logger.info("Python依赖检查通过")
    return True, []

def install_python_dependencies():
    """安装Python依赖"""
    logger.info("安装Python依赖...")
    requirements_file = ROOT_DIR / "requirements.txt"

    if not requirements_file.exists():
        logger.warning(f"requirements.txt文件不存在: {requirements_file}")
        return False

    success, stdout, stderr = run_command(f"pip install -r {requirements_file}")
    if not success:
        logger.error(f"安装Python依赖失败: {stderr}")
        return False

    logger.info("Python依赖安装成功")
    return True

def check_node_dependencies():
    """检查Node.js依赖"""
    logger.info("检查Node.js依赖...")
    package_json = FRONTEND_DIR / "package.json"

    if not package_json.exists():
        logger.warning(f"package.json文件不存在: {package_json}")
        return False, []

    # 检查node_modules目录是否存在
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists() or not node_modules.is_dir():
        logger.warning("前端依赖未安装 (node_modules目录不存在)")
        return False, ["前端依赖未安装"]

    # 检查package-lock.json是否存在
    package_lock = FRONTEND_DIR / "package-lock.json"
    if not package_lock.exists():
        logger.warning("前端依赖可能未完全安装 (package-lock.json不存在)")
        return False, ["前端依赖未完全安装"]

    logger.info("Node.js依赖检查通过")
    return True, []

def install_node_dependencies():
    """安装Node.js依赖"""
    logger.info("安装Node.js依赖...")

    success, stdout, stderr = run_command("npm install", cwd=FRONTEND_DIR)
    if not success:
        logger.error(f"安装Node.js依赖失败: {stderr}")
        return False

    logger.info("Node.js依赖安装成功")
    return True

def check_system_requirements():
    """检查系统要求"""
    logger.info("检查系统要求...")
    result = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "system": platform.system(),
        "platform": platform.platform(),
        "python": {},
        "node": {},
        "dependencies": {},
        "directories": {},
        "overall": "pass"
    }

    # 检查Python
    python_ok, python_version = check_python_version()
    result["python"]["version"] = python_version
    result["python"]["status"] = "pass" if python_ok else "fail"

    # 检查pip
    pip_ok, pip_version = check_pip()
    result["python"]["pip"] = pip_version
    result["python"]["pip_status"] = "pass" if pip_ok else "fail"

    # 检查Node.js
    node_ok, node_version = check_node()
    result["node"]["version"] = node_version
    result["node"]["status"] = "pass" if node_ok else "fail"

    # 检查npm
    npm_ok, npm_version = check_npm()
    result["node"]["npm"] = npm_version
    result["node"]["npm_status"] = "pass" if npm_ok else "fail"

    # 检查Python依赖
    py_deps_ok, missing_py_deps = check_python_dependencies()
    result["dependencies"]["python"] = "pass" if py_deps_ok else "fail"
    result["dependencies"]["missing_python"] = missing_py_deps

    # 检查Node.js依赖
    node_deps_ok, missing_node_deps = check_node_dependencies()
    result["dependencies"]["node"] = "pass" if node_deps_ok else "fail"
    result["dependencies"]["missing_node"] = missing_node_deps

    # 检查目录结构
    result["directories"]["backend"] = "pass" if BACKEND_DIR.exists() and BACKEND_DIR.is_dir() else "fail"
    result["directories"]["frontend"] = "pass" if FRONTEND_DIR.exists() and FRONTEND_DIR.is_dir() else "fail"
    result["directories"]["logs"] = "pass" if LOGS_DIR.exists() and LOGS_DIR.is_dir() else "fail"

    # 总体结果
    if not python_ok or not pip_ok or not py_deps_ok or not node_ok or not npm_ok or not node_deps_ok:
        result["overall"] = "fail"

    save_env_check_result(result)
    return result

def setup_environment():
    """设置运行环境"""
    logger.info("正在设置运行环境...")

    # 检查系统要求
    env_check = check_system_requirements()

    # 安装缺失的依赖
    if env_check["dependencies"]["python"] == "fail" and env_check["python"]["pip_status"] == "pass":
        logger.info("正在安装缺失的Python依赖...")
        install_python_dependencies()

    if env_check["dependencies"]["node"] == "fail" and env_check["node"]["npm_status"] == "pass":
        logger.info("正在安装缺失的Node.js依赖...")
        install_node_dependencies()

    # 再次检查环境
    env_check = check_system_requirements()

    # 如果仍有问题，提示用户
    if env_check["overall"] == "fail":
        logger.warning("环境设置未完全成功，请查看日志并手动解决问题")
        return False

    logger.info("环境设置成功")
    return True

def clear_screen():
    """清除屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """打印标题"""
    clear_screen()
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80)

def print_footer():
    """打印页脚"""
    print("\n" + "="*80)
    input("按回车键继续...")

def manage_database():
    """数据库管理"""
    while True:
        print_header("数据库管理")
        print("1. 检查数据库结构")
        print("2. 修复数据库结构")
        print("3. 重建工作内容表")
        print("4. 初始化数据库")
        print("5. 备份数据库")
        print("0. 返回主菜单")
        print("="*80)

        choice = input("请选择操作 [0-5]: ")

        if choice == '0':
            break
        elif choice == '1':
            run_command("python db_manager.py --check", capture_output=False)
        elif choice == '2':
            run_command("python db_manager.py --fix", capture_output=False)
        elif choice == '3':
            run_command("python db_manager.py --rebuild", capture_output=False)
        elif choice == '4':
            run_command("python db_manager.py --init", capture_output=False)
        elif choice == '5':
            run_command("python db_manager.py --backup", capture_output=False)
        else:
            print("无效的选择，请重试")

        print_footer()

def manage_system():
    """系统管理"""
    while True:
        print_header("系统管理")
        print("1. 启动系统（前后端）")
        print("2. 只启动后端")
        print("3. 只启动前端")
        print("4. 停止系统")
        print("5. 查看系统状态")
        print("6. 创建管理员用户")
        print("7. 查看后端日志")
        print("8. 查看前端日志")
        print("0. 返回主菜单")
        print("="*80)

        choice = input("请选择操作 [0-8]: ")

        if choice == '0':
            break
        elif choice == '1':
            run_command("python run.py --background", capture_output=False)
        elif choice == '2':
            run_command("python run.py --backend-only --background", capture_output=False)
        elif choice == '3':
            run_command("python run.py --frontend-only --background", capture_output=False)
        elif choice == '4':
            run_command("python run.py --stop", capture_output=False)
        elif choice == '5':
            run_command("python run.py --status", capture_output=False)
        elif choice == '6':
            run_command("python run.py --create-admin", capture_output=False)
        elif choice == '7':
            run_command("python run.py --log-backend", capture_output=False)
        elif choice == '8':
            run_command("python run.py --log-frontend", capture_output=False)
        else:
            print("无效的选择，请重试")

        print_footer()

def run_tests():
    """运行测试"""
    while True:
        print_header("测试管理")
        print("1. 运行所有测试")
        print("2. 运行后端测试")
        print("3. 运行批量导入测试")
        print("4. 检查系统结构")
        print("0. 返回主菜单")
        print("="*80)

        choice = input("请选择操作 [0-4]: ")

        if choice == '0':
            break
        elif choice == '1':
            run_command("python test_all.py", capture_output=False)
        elif choice == '2':
            run_command("python test.py", capture_output=False)
        elif choice == '3':
            run_command("python test_batch_import.py", capture_output=False)
        elif choice == '4':
            success, stdout, stderr = run_command("python test_all.py")
            if success:
                print("系统结构检查通过")
            else:
                print("系统结构检查失败")
                print(stderr)
        else:
            print("无效的选择，请重试")

        print_footer()

def manage_data():
    """数据管理"""
    while True:
        print_header("数据管理")
        print("1. 初始化工作内容数据")
        print("2. 批量添加工作内容")
        print("3. 检查工作内容数据")
        print("4. 修复导入路径")
        print("0. 返回主菜单")
        print("="*80)

        choice = input("请选择操作 [0-4]: ")

        if choice == '0':
            break
        elif choice == '1':
            run_command("python init_work_items.py", capture_output=False)
        elif choice == '2':
            # 获取用户名和密码
            username = input("请输入用户名 (默认: admin): ") or "admin"
            password = input("请输入密码 (默认: admin123): ") or "admin123"

            # 选择导入方式
            print("\n请选择导入方式:")
            print("1. 添加单个预定义工作内容")
            print("2. 从CSV文件批量导入")
            import_choice = input("请选择 [1-2]: ")

            if import_choice == '1':
                run_command(f"python batch_add_work_items.py --username {username} --password {password} --single", capture_output=False)
            elif import_choice == '2':
                csv_file = input("请输入CSV文件路径: ")
                if os.path.exists(csv_file):
                    run_command(f"python batch_add_work_items.py --username {username} --password {password} --csv {csv_file}", capture_output=False)
                else:
                    print(f"文件不存在: {csv_file}")
            else:
                print("无效的选择")
        elif choice == '3':
            run_command("python check_work_items.py", capture_output=False)
        elif choice == '4':
            run_command("python fix_imports.py", capture_output=False)
        else:
            print("无效的选择，请重试")

        print_footer()

def manage_logs():
    """日志管理"""
    while True:
        print_header("日志管理")
        print("1. 查看日志文件列表")
        print("2. 查看后端日志")
        print("3. 查看前端日志")
        print("4. 清理旧日志文件")
        print("5. 压缩日志文件")
        print("6. 查看日志统计信息")
        print("0. 返回主菜单")
        print("="*80)

        choice = input("请选择操作 [0-6]: ")

        if choice == '0':
            break
        elif choice == '1':
            list_log_files()
        elif choice == '2':
            run_command("python run.py --log-backend", capture_output=False)
        elif choice == '3':
            run_command("python run.py --log-frontend", capture_output=False)
        elif choice == '4':
            clean_old_logs()
        elif choice == '5':
            compress_logs()
        elif choice == '6':
            show_log_stats()
        else:
            print("无效的选择，请重试")

        print_footer()

def list_log_files():
    """列出日志文件"""
    print_header("日志文件列表")

    # 获取所有日志文件
    log_files = sorted(LOGS_DIR.glob("*.log"), key=os.path.getmtime, reverse=True)

    if not log_files:
        print("没有找到日志文件")
        return

    # 显示日志文件列表
    print(f"{'序号':<6}{'文件名':<40}{'大小':<10}{'修改时间':<20}")
    print("-" * 80)

    for i, log_file in enumerate(log_files, 1):
        # 获取文件信息
        file_size = os.path.getsize(log_file) / 1024  # KB
        mod_time = datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')

        # 显示文件信息
        print(f"{i:<6}{log_file.name:<40}{file_size:.2f} KB{mod_time:<20}")

def clean_old_logs():
    """清理旧日志文件"""
    print_header("清理旧日志文件")

    # 获取所有应用日志文件（app_*.log）
    app_logs = list(LOGS_DIR.glob("app_*.log"))

    if not app_logs:
        print("没有找到应用日志文件")
        return

    # 询问清理选项
    print("请选择清理选项：")
    print("1. 按日期清理（保留最近N天的日志）")
    print("2. 按数量清理（保留最近N个日志文件）")
    print("3. 按大小清理（删除大于N KB的日志文件）")
    print("4. 清理空日志文件")
    print("0. 返回")

    option = input("请选择 [0-4]: ")

    if option == '0':
        return
    elif option == '1':
        # 按日期清理
        days = input("请输入要保留的天数 [默认: 30]: ") or "30"
        try:
            days = int(days)
            if days < 0:
                print("天数必须大于等于0")
                return

            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days)

            # 筛选需要删除的文件
            files_to_delete = []
            for log_file in app_logs:
                mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if mod_time < cutoff_date:
                    files_to_delete.append(log_file)

            if not files_to_delete:
                print(f"没有找到超过 {days} 天的日志文件")
                return

            # 确认删除
            print(f"将删除以下 {len(files_to_delete)} 个日志文件：")
            for log_file in files_to_delete:
                mod_time = datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{log_file.name} - {mod_time}")

            confirm = input("确认删除这些文件？(y/n): ")
            if confirm.lower() != 'y':
                print("取消删除")
                return

            # 删除文件
            for log_file in files_to_delete:
                try:
                    os.remove(log_file)
                    print(f"已删除: {log_file.name}")
                except Exception as e:
                    print(f"删除 {log_file.name} 失败: {e}")

            print(f"成功删除 {len(files_to_delete)} 个日志文件")
        except ValueError:
            print("请输入有效的天数")
    elif option == '2':
        # 按数量清理
        count = input("请输入要保留的最近日志文件数量 [默认: 10]: ") or "10"
        try:
            count = int(count)
            if count < 0:
                print("数量必须大于等于0")
                return

            # 按修改时间排序
            sorted_logs = sorted(app_logs, key=os.path.getmtime, reverse=True)

            # 确定要删除的文件
            files_to_keep = sorted_logs[:count]
            files_to_delete = sorted_logs[count:]

            if not files_to_delete:
                print(f"没有多余的日志文件需要删除")
                return

            # 确认删除
            print(f"将删除以下 {len(files_to_delete)} 个日志文件：")
            for log_file in files_to_delete:
                mod_time = datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{log_file.name} - {mod_time}")

            confirm = input("确认删除这些文件？(y/n): ")
            if confirm.lower() != 'y':
                print("取消删除")
                return

            # 删除文件
            for log_file in files_to_delete:
                try:
                    os.remove(log_file)
                    print(f"已删除: {log_file.name}")
                except Exception as e:
                    print(f"删除 {log_file.name} 失败: {e}")

            print(f"成功删除 {len(files_to_delete)} 个日志文件")
        except ValueError:
            print("请输入有效的数量")
    elif option == '3':
        # 按大小清理
        size = input("请输入要删除的日志文件大小阈值（KB）[默认: 100]: ") or "100"
        try:
            size = float(size)
            if size < 0:
                print("大小必须大于等于0")
                return

            # 筛选需要删除的文件
            files_to_delete = []
            for log_file in app_logs:
                file_size = os.path.getsize(log_file) / 1024  # KB
                if file_size > size:
                    files_to_delete.append((log_file, file_size))

            if not files_to_delete:
                print(f"没有找到大于 {size} KB 的日志文件")
                return

            # 确认删除
            print(f"将删除以下 {len(files_to_delete)} 个日志文件：")
            for log_file, file_size in files_to_delete:
                print(f"{log_file.name} - {file_size:.2f} KB")

            confirm = input("确认删除这些文件？(y/n): ")
            if confirm.lower() != 'y':
                print("取消删除")
                return

            # 删除文件
            for log_file, _ in files_to_delete:
                try:
                    os.remove(log_file)
                    print(f"已删除: {log_file.name}")
                except Exception as e:
                    print(f"删除 {log_file.name} 失败: {e}")

            print(f"成功删除 {len(files_to_delete)} 个日志文件")
        except ValueError:
            print("请输入有效的大小")
    elif option == '4':
        # 清理空日志文件
        empty_logs = []
        for log_file in app_logs:
            if os.path.getsize(log_file) == 0:
                empty_logs.append(log_file)

        if not empty_logs:
            print("没有找到空日志文件")
            return

        # 确认删除
        print(f"将删除以下 {len(empty_logs)} 个空日志文件：")
        for log_file in empty_logs:
            print(f"{log_file.name}")

        confirm = input("确认删除这些文件？(y/n): ")
        if confirm.lower() != 'y':
            print("取消删除")
            return

        # 删除文件
        for log_file in empty_logs:
            try:
                os.remove(log_file)
                print(f"已删除: {log_file.name}")
            except Exception as e:
                print(f"删除 {log_file.name} 失败: {e}")

        print(f"成功删除 {len(empty_logs)} 个空日志文件")
    else:
        print("无效的选择")

def compress_logs():
    """压缩日志文件"""
    print_header("压缩日志文件")

    # 获取所有应用日志文件（app_*.log）
    app_logs = list(LOGS_DIR.glob("app_*.log"))

    if not app_logs:
        print("没有找到应用日志文件")
        return

    # 询问压缩选项
    print("请选择压缩选项：")
    print("1. 压缩所有应用日志文件")
    print("2. 压缩指定日期之前的日志文件")
    print("3. 压缩指定大小以上的日志文件")
    print("0. 返回")

    option = input("请选择 [0-3]: ")

    if option == '0':
        return
    elif option == '1':
        # 压缩所有应用日志文件
        archive_name = f"app_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        archive_path = LOGS_DIR / archive_name

        # 确认压缩
        print(f"将压缩 {len(app_logs)} 个日志文件到 {archive_name}")
        confirm = input("确认压缩？(y/n): ")
        if confirm.lower() != 'y':
            print("取消压缩")
            return

        # 创建压缩文件
        try:
            import zipfile
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for log_file in app_logs:
                    zipf.write(log_file, arcname=log_file.name)

            # 询问是否删除原文件
            delete_original = input("压缩成功，是否删除原日志文件？(y/n): ")
            if delete_original.lower() == 'y':
                for log_file in app_logs:
                    try:
                        os.remove(log_file)
                        print(f"已删除: {log_file.name}")
                    except Exception as e:
                        print(f"删除 {log_file.name} 失败: {e}")

            print(f"成功压缩 {len(app_logs)} 个日志文件到 {archive_name}")
        except Exception as e:
            print(f"压缩日志文件失败: {e}")
    elif option == '2':
        # 压缩指定日期之前的日志文件
        days = input("请输入要压缩多少天前的日志文件 [默认: 7]: ") or "7"
        try:
            days = int(days)
            if days < 0:
                print("天数必须大于等于0")
                return

            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days)

            # 筛选需要压缩的文件
            files_to_compress = []
            for log_file in app_logs:
                mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if mod_time < cutoff_date:
                    files_to_compress.append(log_file)

            if not files_to_compress:
                print(f"没有找到超过 {days} 天的日志文件")
                return

            # 确认压缩
            print(f"将压缩以下 {len(files_to_compress)} 个日志文件：")
            for log_file in files_to_compress:
                mod_time = datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"{log_file.name} - {mod_time}")

            confirm = input("确认压缩这些文件？(y/n): ")
            if confirm.lower() != 'y':
                print("取消压缩")
                return

            # 创建压缩文件
            archive_name = f"app_logs_before_{cutoff_date.strftime('%Y%m%d')}.zip"
            archive_path = LOGS_DIR / archive_name

            try:
                import zipfile
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for log_file in files_to_compress:
                        zipf.write(log_file, arcname=log_file.name)

                # 询问是否删除原文件
                delete_original = input("压缩成功，是否删除原日志文件？(y/n): ")
                if delete_original.lower() == 'y':
                    for log_file in files_to_compress:
                        try:
                            os.remove(log_file)
                            print(f"已删除: {log_file.name}")
                        except Exception as e:
                            print(f"删除 {log_file.name} 失败: {e}")

                print(f"成功压缩 {len(files_to_compress)} 个日志文件到 {archive_name}")
            except Exception as e:
                print(f"压缩日志文件失败: {e}")
        except ValueError:
            print("请输入有效的天数")
    elif option == '3':
        # 压缩指定大小以上的日志文件
        size = input("请输入要压缩的日志文件大小阈值（KB）[默认: 50]: ") or "50"
        try:
            size = float(size)
            if size < 0:
                print("大小必须大于等于0")
                return

            # 筛选需要压缩的文件
            files_to_compress = []
            for log_file in app_logs:
                file_size = os.path.getsize(log_file) / 1024  # KB
                if file_size > size:
                    files_to_compress.append((log_file, file_size))

            if not files_to_compress:
                print(f"没有找到大于 {size} KB 的日志文件")
                return

            # 确认压缩
            print(f"将压缩以下 {len(files_to_compress)} 个日志文件：")
            for log_file, file_size in files_to_compress:
                print(f"{log_file.name} - {file_size:.2f} KB")

            confirm = input("确认压缩这些文件？(y/n): ")
            if confirm.lower() != 'y':
                print("取消压缩")
                return

            # 创建压缩文件
            archive_name = f"app_logs_large_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            archive_path = LOGS_DIR / archive_name

            try:
                import zipfile
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for log_file, _ in files_to_compress:
                        zipf.write(log_file, arcname=log_file.name)

                # 询问是否删除原文件
                delete_original = input("压缩成功，是否删除原日志文件？(y/n): ")
                if delete_original.lower() == 'y':
                    for log_file, _ in files_to_compress:
                        try:
                            os.remove(log_file)
                            print(f"已删除: {log_file.name}")
                        except Exception as e:
                            print(f"删除 {log_file.name} 失败: {e}")

                print(f"成功压缩 {len(files_to_compress)} 个日志文件到 {archive_name}")
            except Exception as e:
                print(f"压缩日志文件失败: {e}")
        except ValueError:
            print("请输入有效的大小")
    else:
        print("无效的选择")

def show_log_stats():
    """显示日志统计信息"""
    print_header("日志统计信息")

    # 获取所有日志文件
    all_logs = list(LOGS_DIR.glob("*.log"))
    app_logs = list(LOGS_DIR.glob("app_*.log"))
    backend_log = LOGS_DIR / "backend.log"
    frontend_log = LOGS_DIR / "frontend.log"

    # 计算总大小
    total_size = sum(os.path.getsize(log) for log in all_logs) / (1024 * 1024)  # MB
    app_logs_size = sum(os.path.getsize(log) for log in app_logs) / (1024 * 1024)  # MB
    backend_log_size = os.path.getsize(backend_log) / (1024 * 1024) if backend_log.exists() else 0  # MB
    frontend_log_size = os.path.getsize(frontend_log) / (1024 * 1024) if frontend_log.exists() else 0  # MB

    # 显示统计信息
    print(f"日志文件总数: {len(all_logs)}")
    print(f"应用日志文件数: {len(app_logs)}")
    print(f"总大小: {total_size:.2f} MB")
    print(f"应用日志大小: {app_logs_size:.2f} MB")
    print(f"后端日志大小: {backend_log_size:.2f} MB")
    print(f"前端日志大小: {frontend_log_size:.2f} MB")

    # 显示最大的5个日志文件
    print("\n最大的5个日志文件:")
    sorted_logs = sorted(all_logs, key=os.path.getsize, reverse=True)[:5]
    for log in sorted_logs:
        size = os.path.getsize(log) / (1024 * 1024)  # MB
        print(f"{log.name}: {size:.2f} MB")

    # 显示最近修改的5个日志文件
    print("\n最近修改的5个日志文件:")
    sorted_logs = sorted(all_logs, key=os.path.getmtime, reverse=True)[:5]
    for log in sorted_logs:
        mod_time = datetime.fromtimestamp(os.path.getmtime(log)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{log.name}: {mod_time}")

def show_main_menu():
    """显示主菜单"""
    while True:
        print_header("维修项目管理系统 - 系统管理工具")
        print("1. 数据库管理")
        print("2. 系统管理")
        print("3. 测试管理")
        print("4. 数据管理")
        print("5. 日志管理")
        print("6. 查看系统信息")
        print("7. 环境管理")
        print("0. 退出")
        print("="*80)

        choice = input("请选择操作 [0-7]: ")

        if choice == '0':
            print("退出程序")
            break
        elif choice == '1':
            manage_database()
        elif choice == '2':
            manage_system()
        elif choice == '3':
            run_tests()
        elif choice == '4':
            manage_data()
        elif choice == '5':
            manage_logs()
        elif choice == '6':
            show_system_info()
        elif choice == '7':
            manage_environment()
        else:
            print("无效的选择，请重试")

def manage_environment():
    """环境管理"""
    while True:
        print_header("环境管理")
        print("1. 检查系统环境")
        print("2. 安装/更新依赖")
        print("3. 查看环境检查历史")
        print("4. 强制重新检查环境")
        print("0. 返回主菜单")
        print("="*80)

        choice = input("请选择操作 [0-4]: ")

        if choice == '0':
            break
        elif choice == '1':
            env_check = check_system_requirements()
            show_env_check_result(env_check)
        elif choice == '2':
            print_header("安装/更新依赖")
            if setup_environment():
                print("环境设置成功！")
            else:
                print("环境设置未完全成功，请查看日志并手动解决问题。")
            print_footer()
        elif choice == '3':
            env_check = load_env_check_result()
            if env_check:
                show_env_check_result(env_check)
            else:
                print("未找到环境检查历史记录")
                print_footer()
        elif choice == '4':
            handle_first_run()
        else:
            print("无效的选择，请重试")

        if choice != '0':
            print_footer()

def show_system_info():
    """显示系统信息"""
    print_header("系统信息")

    # 检查Python版本
    print(f"Python版本: {sys.version}")

    # 检查操作系统
    print(f"操作系统: {os.name} - {sys.platform}")

    # 检查项目路径
    print(f"项目根目录: {ROOT_DIR}")
    print(f"后端目录: {BACKEND_DIR}")
    print(f"前端目录: {FRONTEND_DIR}")

    # 检查数据库
    db_path = BACKEND_DIR / "repair_management.db"
    if os.path.exists(db_path):
        print(f"数据库文件: {db_path} (存在)")
        # 获取数据库大小
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # 转换为MB
        print(f"数据库大小: {db_size:.2f} MB")
    else:
        print(f"数据库文件: {db_path} (不存在)")

    # 检查系统状态
    success, stdout, stderr = run_command("python run.py --status")
    if success:
        print("\n系统状态:")
        print(stdout)

    print_footer()

def show_env_check_result(env_check):
    """显示环境检查结果"""
    print_header("环境检查结果")

    print(f"系统: {env_check['system']} ({env_check['platform']})")
    print(f"检查时间: {env_check['timestamp']}")
    print("\nPython环境:")
    print(f"  版本: {env_check['python'].get('version', '未知')} - {'通过' if env_check['python'].get('status') == 'pass' else '不满足要求'}")
    print(f"  pip: {env_check['python'].get('pip', '未安装')} - {'通过' if env_check['python'].get('pip_status') == 'pass' else '不可用'}")

    print("\nNode.js环境:")
    print(f"  版本: {env_check['node'].get('version', '未安装')} - {'通过' if env_check['node'].get('status') == 'pass' else '不满足要求'}")
    print(f"  npm: {env_check['node'].get('npm', '未安装')} - {'通过' if env_check['node'].get('npm_status') == 'pass' else '不可用'}")

    print("\n依赖检查:")
    print(f"  Python依赖: {'通过' if env_check['dependencies'].get('python') == 'pass' else '缺少依赖'}")
    if env_check['dependencies'].get('python') != 'pass' and env_check['dependencies'].get('missing_python'):
        print(f"    缺少: {', '.join(env_check['dependencies'].get('missing_python', []))}")

    print(f"  Node.js依赖: {'通过' if env_check['dependencies'].get('node') == 'pass' else '缺少依赖'}")
    if env_check['dependencies'].get('node') != 'pass' and env_check['dependencies'].get('missing_node'):
        print(f"    缺少: {', '.join(env_check['dependencies'].get('missing_node', []))}")

    print("\n目录检查:")
    print(f"  后端目录: {'存在' if env_check['directories'].get('backend') == 'pass' else '不存在'}")
    print(f"  前端目录: {'存在' if env_check['directories'].get('frontend') == 'pass' else '不存在'}")
    print(f"  日志目录: {'存在' if env_check['directories'].get('logs') == 'pass' else '不存在'}")

    print("\n总体结果: " + ("通过" if env_check['overall'] == 'pass' else "需要修复"))

    print_footer()

def handle_first_run():
    """处理首次运行"""
    print_header("首次运行系统检查")
    print("检测到这是首次运行系统管理工具，将进行环境检查和设置...")

    # 检查系统环境
    env_check = check_system_requirements()

    # 显示检查结果
    show_env_check_result(env_check)

    # 如果环境不满足要求，询问是否自动安装
    if env_check["overall"] != "pass":
        print("\n系统环境不满足要求，需要安装或更新以下组件:")

        if env_check["python"]["status"] != "pass":
            print(f"- Python {env_check['python'].get('version', '3.8+')} (当前版本不满足要求)")

        if env_check["python"]["pip_status"] != "pass":
            print("- pip (未安装或不可用)")

        if env_check["node"]["status"] != "pass":
            print("- Node.js (未安装或版本过低)")

        if env_check["node"]["npm_status"] != "pass":
            print("- npm (未安装或不可用)")

        if env_check["dependencies"]["python"] != "pass":
            print("- Python依赖 (缺少必要的包)")

        if env_check["dependencies"]["node"] != "pass":
            print("- Node.js依赖 (前端依赖未安装)")

        print("\n是否尝试自动安装缺失的组件？(y/n): ", end="")
        choice = input().lower()

        if choice == 'y':
            print("\n正在设置环境...")
            if setup_environment():
                print("环境设置成功！")
            else:
                print("\n环境设置未完全成功，请参考以下手动安装步骤:")
                print("1. 确保安装了Python 3.8+")
                print("2. 确保安装了pip")
                print("3. 安装Python依赖: pip install -r requirements.txt")
                print("4. 确保安装了Node.js和npm")
                print("5. 安装前端依赖: cd frontend && npm install")
                print("\n完成上述步骤后，请重新运行此脚本。")
        else:
            print("\n您选择了不自动安装组件，请手动安装所需组件后再运行系统。")
    else:
        print("\n系统环境检查通过，可以正常使用所有功能。")

    # 标记首次运行已完成
    mark_first_run_completed()

    print("\n首次运行检查完成，按回车键继续...")
    input()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='系统管理工具')
    parser.add_argument('--db', action='store_true', help='数据库管理')
    parser.add_argument('--system', action='store_true', help='系统管理')
    parser.add_argument('--test', action='store_true', help='测试管理')
    parser.add_argument('--data', action='store_true', help='数据管理')
    parser.add_argument('--logs', action='store_true', help='日志管理')
    parser.add_argument('--info', action='store_true', help='显示系统信息')
    parser.add_argument('--check-env', action='store_true', help='检查系统环境')
    parser.add_argument('--setup-env', action='store_true', help='设置系统环境')
    parser.add_argument('--force-first-run', action='store_true', help='强制执行首次运行检查')

    # 日志管理相关参数
    parser.add_argument('--list-logs', action='store_true', help='列出日志文件')
    parser.add_argument('--clean-logs', action='store_true', help='清理旧日志文件')
    parser.add_argument('--clean-empty-logs', action='store_true', help='清理空日志文件')
    parser.add_argument('--compress-logs', action='store_true', help='压缩日志文件')
    parser.add_argument('--log-stats', action='store_true', help='显示日志统计信息')
    parser.add_argument('--days', type=int, default=30, help='日志保留天数（用于清理和压缩）')
    parser.add_argument('--count', type=int, default=10, help='日志保留数量（用于清理）')
    parser.add_argument('--size', type=float, default=100, help='日志大小阈值（KB，用于清理和压缩）')

    args = parser.parse_args()

    # 检查是否首次运行或强制执行首次运行检查
    if is_first_run() or args.force_first_run:
        handle_first_run()

    # 检查系统环境
    if args.check_env:
        env_check = check_system_requirements()
        show_env_check_result(env_check)
        return

    # 设置系统环境
    if args.setup_env:
        print_header("设置系统环境")
        if setup_environment():
            print("环境设置成功！")
        else:
            print("环境设置未完全成功，请查看日志并手动解决问题。")
        print_footer()
        return

    # 处理日志管理相关的命令行参数
    if args.list_logs:
        list_log_files()
        return

    if args.clean_empty_logs:
        # 获取所有应用日志文件（app_*.log）
        app_logs = list(LOGS_DIR.glob("app_*.log"))
        empty_logs = [log for log in app_logs if os.path.getsize(log) == 0]

        if not empty_logs:
            print("没有找到空日志文件")
            return

        print(f"将删除 {len(empty_logs)} 个空日志文件")
        for log_file in empty_logs:
            try:
                os.remove(log_file)
                print(f"已删除: {log_file.name}")
            except Exception as e:
                print(f"删除 {log_file.name} 失败: {e}")
        return

    if args.clean_logs:
        # 获取所有应用日志文件（app_*.log）
        app_logs = list(LOGS_DIR.glob("app_*.log"))

        if not app_logs:
            print("没有找到应用日志文件")
            return

        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=args.days)

        # 筛选需要删除的文件
        files_to_delete = []
        for log_file in app_logs:
            mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if mod_time < cutoff_date:
                files_to_delete.append(log_file)

        if not files_to_delete:
            print(f"没有找到超过 {args.days} 天的日志文件")
            return

        print(f"将删除 {len(files_to_delete)} 个超过 {args.days} 天的日志文件")
        for log_file in files_to_delete:
            try:
                os.remove(log_file)
                print(f"已删除: {log_file.name}")
            except Exception as e:
                print(f"删除 {log_file.name} 失败: {e}")
        return

    if args.compress_logs:
        # 获取所有应用日志文件（app_*.log）
        app_logs = list(LOGS_DIR.glob("app_*.log"))

        if not app_logs:
            print("没有找到应用日志文件")
            return

        # 创建压缩文件
        archive_name = f"app_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        archive_path = LOGS_DIR / archive_name

        try:
            import zipfile
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for log_file in app_logs:
                    zipf.write(log_file, arcname=log_file.name)

            print(f"成功压缩 {len(app_logs)} 个日志文件到 {archive_path}")

            # 询问是否删除原文件
            delete_original = input("是否删除原日志文件？(y/n): ")
            if delete_original.lower() == 'y':
                for log_file in app_logs:
                    try:
                        os.remove(log_file)
                        print(f"已删除: {log_file.name}")
                    except Exception as e:
                        print(f"删除 {log_file.name} 失败: {e}")
        except Exception as e:
            print(f"压缩日志文件失败: {e}")
        return

    if args.log_stats:
        show_log_stats()
        return

    # 如果没有指定任何参数，显示交互式菜单
    if not any([args.db, args.system, args.test, args.data, args.logs, args.info]):
        show_main_menu()
        return

    # 执行指定的操作
    if args.db:
        manage_database()

    if args.system:
        manage_system()

    if args.test:
        run_tests()

    if args.data:
        manage_data()

    if args.logs:
        manage_logs()

    if args.info:
        show_system_info()

if __name__ == "__main__":
    main()
