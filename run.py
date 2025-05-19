#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import signal
import argparse
import webbrowser
import atexit
import logging
import datetime
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
LOGS_DIR = ROOT_DIR / "logs"

# 创建日志目录
LOGS_DIR.mkdir(exist_ok=True)

# 配置日志
log_file = LOGS_DIR / f"app_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run")

# 进程列表
processes = []

# PID文件路径
BACKEND_PID_FILE = ROOT_DIR / "backend.pid"
FRONTEND_PID_FILE = ROOT_DIR / "frontend.pid"

def run_command(command, cwd=None, env=None, background=False, stdout=None, stderr=None):
    """运行命令并返回进程

    Args:
        command: 要运行的命令
        cwd: 工作目录
        env: 环境变量
        background: 是否在后台运行
        stdout: 标准输出重定向
        stderr: 标准错误重定向
    """
    if background and stdout is None:
        stdout = subprocess.DEVNULL
    if background and stderr is None:
        stderr = subprocess.DEVNULL

    if sys.platform == 'win32':
        process = subprocess.Popen(command, shell=True, cwd=cwd, env=env,
                                  stdout=stdout, stderr=stderr)
    else:
        process = subprocess.Popen(command, shell=True, cwd=cwd, env=env,
                                  preexec_fn=os.setsid, stdout=stdout, stderr=stderr)
    return process

def start_backend(background=False):
    """启动后端服务

    Args:
        background: 是否在后台运行
    """
    # 检查后端是否已经在运行
    backend_pid = read_pid(BACKEND_PID_FILE)
    if backend_pid and is_process_running(backend_pid):
        logger.info(f"后端服务已经在运行 (PID: {backend_pid})")
        return None

    logger.info("正在启动后端服务...")
    env = os.environ.copy()

    # 准备日志文件
    if background:
        log_path = LOGS_DIR / "backend.log"
        log_file = open(log_path, "a")
        logger.info(f"后端日志将写入: {log_path}")
    else:
        log_file = None

    # 启动进程
    process = run_command(
        "uvicorn main:app --reload --host 0.0.0.0 --port 8000",
        cwd=BACKEND_DIR,
        env=env,
        background=background,
        stdout=log_file,
        stderr=log_file
    )

    if background:
        # 保存PID
        save_pid(BACKEND_PID_FILE, process.pid)
        logger.info(f"后端服务已在后台启动 (PID: {process.pid})")
    else:
        processes.append(process)
        logger.info("后端服务已启动，地址: http://localhost:8000")

    return process

def start_frontend(background=False):
    """启动前端服务

    Args:
        background: 是否在后台运行
    """
    # 检查前端是否已经在运行
    frontend_pid = read_pid(FRONTEND_PID_FILE)
    if frontend_pid and is_process_running(frontend_pid):
        logger.info(f"前端服务已经在运行 (PID: {frontend_pid})")
        return None

    logger.info("正在启动前端服务...")
    env = os.environ.copy()

    # 准备日志文件
    if background:
        log_path = LOGS_DIR / "frontend.log"
        log_file = open(log_path, "a")
        logger.info(f"前端日志将写入: {log_path}")
    else:
        log_file = None

    # 启动进程
    process = run_command(
        "npm run dev",
        cwd=FRONTEND_DIR,
        env=env,
        background=background,
        stdout=log_file,
        stderr=log_file
    )

    if background:
        # 保存PID
        save_pid(FRONTEND_PID_FILE, process.pid)
        logger.info(f"前端服务已在后台启动 (PID: {process.pid})")
    else:
        processes.append(process)
        logger.info("前端服务已启动，地址: http://localhost:8458")

    return process

def save_pid(pid_file, pid):
    """保存进程ID到文件"""
    with open(pid_file, 'w') as f:
        f.write(str(pid))
    logger.info(f"进程ID {pid} 已保存到 {pid_file}")

def read_pid(pid_file):
    """从文件读取进程ID"""
    if not os.path.exists(pid_file):
        return None
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        return pid
    except (ValueError, IOError) as e:
        logger.error(f"读取PID文件失败: {e}")
        return None

def is_process_running(pid):
    """检查进程是否在运行"""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def kill_process(pid):
    """杀死进程"""
    if not is_process_running(pid):
        return False

    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        return True
    except (subprocess.SubprocessError, OSError) as e:
        logger.error(f"杀死进程 {pid} 失败: {e}")
        return False

def stop_backend():
    """停止后端服务"""
    backend_pid = read_pid(BACKEND_PID_FILE)
    if not backend_pid:
        logger.info("未找到后端服务的PID文件")
        return False

    if not is_process_running(backend_pid):
        logger.info(f"后端服务 (PID: {backend_pid}) 已经不在运行")
        if os.path.exists(BACKEND_PID_FILE):
            os.remove(BACKEND_PID_FILE)
        return True

    logger.info(f"正在停止后端服务 (PID: {backend_pid})...")
    if kill_process(backend_pid):
        logger.info(f"后端服务已停止")
        if os.path.exists(BACKEND_PID_FILE):
            os.remove(BACKEND_PID_FILE)
        return True
    else:
        logger.error(f"停止后端服务失败")
        return False

def stop_frontend():
    """停止前端服务"""
    frontend_pid = read_pid(FRONTEND_PID_FILE)
    if not frontend_pid:
        logger.info("未找到前端服务的PID文件")
        return False

    if not is_process_running(frontend_pid):
        logger.info(f"前端服务 (PID: {frontend_pid}) 已经不在运行")
        if os.path.exists(FRONTEND_PID_FILE):
            os.remove(FRONTEND_PID_FILE)
        return True

    logger.info(f"正在停止前端服务 (PID: {frontend_pid})...")
    if kill_process(frontend_pid):
        logger.info(f"前端服务已停止")
        if os.path.exists(FRONTEND_PID_FILE):
            os.remove(FRONTEND_PID_FILE)
        return True
    else:
        logger.error(f"停止前端服务失败")
        return False

def cleanup():
    """清理所有进程"""
    logger.info("正在关闭所有服务...")
    for process in processes:
        if sys.platform == 'win32':
            process.terminate()
        else:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except:
                process.terminate()
    logger.info("所有服务已关闭")

def create_admin_user():
    """创建管理员用户"""
    import sqlite3
    from passlib.context import CryptContext

    # 连接数据库
    db_path = BACKEND_DIR / "repair_management.db"
    if not db_path.exists():
        print("数据库文件不存在，请先启动后端服务")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 检查用户是否已存在
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if cursor.fetchone():
        print("管理员用户已存在")
        conn.close()
        return

    # 创建密码哈希
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("admin123")

    # 插入管理员用户
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, full_name, role, is_active) VALUES (?, ?, ?, ?, ?, ?)",
        ("admin", "admin@example.com", hashed_password, "管理员", "admin", 1)
    )
    conn.commit()
    conn.close()
    print("管理员用户已创建，用户名: admin，密码: admin123")

def view_log(log_file):
    """查看日志文件的最后几行"""
    if not os.path.exists(log_file):
        logger.error(f"日志文件不存在: {log_file}")
        return

    try:
        # 使用tail命令查看日志文件的最后50行
        if sys.platform == 'win32':
            # Windows下使用PowerShell的Get-Content命令
            subprocess.run(['powershell', '-Command', f'Get-Content -Tail 50 {log_file}'], check=True)
        else:
            # Linux/Mac下使用tail命令
            subprocess.run(['tail', '-n', '50', log_file], check=True)
    except subprocess.SubprocessError as e:
        logger.error(f"查看日志文件失败: {e}")
        # 尝试直接读取文件
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-50:]:  # 只显示最后50行
                    print(line.strip())
        except Exception as e:
            logger.error(f"读取日志文件失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="维修项目管理系统启动脚本")
    parser.add_argument("--backend-only", action="store_true", help="只启动后端服务")
    parser.add_argument("--frontend-only", action="store_true", help="只启动前端服务")
    parser.add_argument("--create-admin", action="store_true", help="创建管理员用户")
    parser.add_argument("--open-browser", action="store_true", help="自动打开浏览器")
    parser.add_argument("--background", action="store_true", help="在后台运行服务")
    parser.add_argument("--stop", action="store_true", help="停止所有服务")
    parser.add_argument("--stop-backend", action="store_true", help="停止后端服务")
    parser.add_argument("--stop-frontend", action="store_true", help="停止前端服务")
    parser.add_argument("--status", action="store_true", help="查看服务状态")
    parser.add_argument("--log-backend", action="store_true", help="查看后端日志")
    parser.add_argument("--log-frontend", action="store_true", help="查看前端日志")

    args = parser.parse_args()

    # 只在非后台模式下注册退出处理函数
    if not args.background:
        atexit.register(cleanup)

    try:
        # 创建管理员用户
        if args.create_admin:
            create_admin_user()
            return

        # 停止服务
        if args.stop or args.stop_backend or args.stop_frontend:
            if args.stop or args.stop_backend:
                stop_backend()
            if args.stop or args.stop_frontend:
                stop_frontend()
            return

        # 查看服务状态
        if args.status:
            backend_pid = read_pid(BACKEND_PID_FILE)
            frontend_pid = read_pid(FRONTEND_PID_FILE)

            if backend_pid and is_process_running(backend_pid):
                logger.info(f"后端服务正在运行 (PID: {backend_pid})")
            else:
                logger.info("后端服务未运行")

            if frontend_pid and is_process_running(frontend_pid):
                logger.info(f"前端服务正在运行 (PID: {frontend_pid})")
            else:
                logger.info("前端服务未运行")
            return

        # 查看日志
        if args.log_backend:
            backend_log = LOGS_DIR / "backend.log"
            logger.info(f"查看后端日志 ({backend_log}):")
            view_log(backend_log)
            return

        if args.log_frontend:
            frontend_log = LOGS_DIR / "frontend.log"
            logger.info(f"查看前端日志 ({frontend_log}):")
            view_log(frontend_log)
            return

        # 启动服务
        if args.backend_only:
            backend_process = start_backend(background=args.background)
        elif args.frontend_only:
            frontend_process = start_frontend(background=args.background)
        else:
            backend_process = start_backend(background=args.background)
            time.sleep(2)  # 等待后端启动
            frontend_process = start_frontend(background=args.background)

        # 在后台运行时，直接返回
        if args.background:
            logger.info("服务已在后台启动")
            return

        # 打开浏览器
        if args.open_browser and not args.backend_only:
            time.sleep(3)  # 等待前端启动
            webbrowser.open("http://localhost:8458")

        # 等待用户中断
        logger.info("按 Ctrl+C 停止服务...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在停止服务...")
    finally:
        # 只在前台运行服务时执行清理
        if not args.background and not args.stop and not args.stop_backend and not args.stop_frontend and not args.status and not args.log_backend and not args.log_frontend and not args.create_admin:
            cleanup()

if __name__ == "__main__":
    main()
