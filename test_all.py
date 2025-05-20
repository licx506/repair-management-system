#!/usr/bin/env python3
"""
系统综合测试脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent

def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80)

def run_command(command, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd or ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_backend_structure():
    """检查后端项目结构"""
    print_header("检查后端项目结构")
    
    backend_dir = ROOT_DIR / "backend"
    
    # 检查关键目录
    key_dirs = ["models", "routers", "schemas", "utils"]
    for dir_name in key_dirs:
        dir_path = backend_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录不存在: {dir_name}")
    
    # 检查关键文件
    key_files = ["main.py", "database.py"]
    for file_name in key_files:
        file_path = backend_dir / file_name
        if file_path.exists() and file_path.is_file():
            print(f"✅ 文件存在: {file_name}")
        else:
            print(f"❌ 文件不存在: {file_name}")
    
    # 检查静态文件目录
    static_dir = backend_dir / "static" / "templates"
    if static_dir.exists() and static_dir.is_dir():
        print(f"✅ 静态文件目录存在")
        
        # 检查模板文件
        template_files = [
            "work_items_template.csv",
            "materials_template.csv",
            "tasks_template.csv",
            "users_template.csv"
        ]
        for file_name in template_files:
            file_path = static_dir / file_name
            if file_path.exists() and file_path.is_file():
                print(f"  ✅ 模板文件存在: {file_name}")
            else:
                print(f"  ❌ 模板文件不存在: {file_name}")
    else:
        print(f"❌ 静态文件目录不存在")

def check_frontend_structure():
    """检查前端项目结构"""
    print_header("检查前端项目结构")
    
    frontend_dir = ROOT_DIR / "frontend"
    
    # 检查关键目录
    key_dirs = ["src", "public"]
    for dir_name in key_dirs:
        dir_path = frontend_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录不存在: {dir_name}")
    
    # 检查src子目录
    src_subdirs = ["api", "components", "contexts", "layouts", "pages", "utils"]
    for dir_name in src_subdirs:
        dir_path = frontend_dir / "src" / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ src子目录存在: {dir_name}")
        else:
            print(f"❌ src子目录不存在: {dir_name}")
    
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
        if full_path.exists() and full_path.is_file():
            print(f"✅ 文件存在: {file_path}")
        else:
            print(f"❌ 文件不存在: {file_path}")

def check_database_structure():
    """检查数据库结构"""
    print_header("检查数据库结构")
    
    # 检查数据库文件是否存在
    db_path = ROOT_DIR / "backend" / "repair_management.db"
    if db_path.exists() and db_path.is_file():
        print(f"✅ 数据库文件存在: {db_path}")
        
        # 运行数据库结构检查脚本
        check_script = ROOT_DIR / "check_db_structure.py"
        if check_script.exists() and check_script.is_file():
            print("正在运行数据库结构检查脚本...")
            success, stdout, stderr = run_command(f"python {check_script}")
            if success:
                print("✅ 数据库结构检查通过")
            else:
                print("❌ 数据库结构检查失败")
                print(f"错误信息: {stderr}")
        else:
            print(f"❌ 数据库结构检查脚本不存在: {check_script}")
    else:
        print(f"❌ 数据库文件不存在: {db_path}")

def run_backend_tests():
    """运行后端测试"""
    print_header("运行后端测试")
    
    # 运行测试脚本
    success, stdout, stderr = run_command("python test.py")
    if success:
        print("✅ 后端测试通过")
    else:
        print("❌ 后端测试失败")
        print(f"错误信息: {stderr}")
    
    # 打印测试输出
    if stdout:
        print("\n测试输出:")
        print(stdout)

def run_batch_import_tests():
    """运行批量导入测试"""
    print_header("运行批量导入测试")
    
    # 检查批量导入测试脚本是否存在
    test_script = ROOT_DIR / "test_batch_import.py"
    if test_script.exists() and test_script.is_file():
        print("正在运行批量导入测试脚本...")
        success, stdout, stderr = run_command(f"python {test_script}")
        if success:
            print("✅ 批量导入测试通过")
        else:
            print("❌ 批量导入测试失败")
            print(f"错误信息: {stderr}")
        
        # 打印测试输出
        if stdout:
            print("\n测试输出:")
            print(stdout)
    else:
        print(f"❌ 批量导入测试脚本不存在: {test_script}")

def generate_optimization_list():
    """生成优化建议清单"""
    print_header("优化建议清单")
    
    suggestions = [
        "1. 数据库优化",
        "   - 添加更多索引，提高查询性能",
        "   - 优化表结构，减少冗余数据",
        "   - 添加数据库迁移工具，支持版本控制",
        "   - 实现数据库备份和恢复功能",
        
        "2. 批量导入功能增强",
        "   - 支持Excel格式(.xlsx)导入",
        "   - 添加导入预览功能",
        "   - 支持部分字段更新模式",
        "   - 添加导入历史记录",
        "   - 支持导入错误处理和恢复",
        
        "3. 数据导出功能",
        "   - 支持导出为CSV和Excel格式",
        "   - 支持选择导出字段",
        "   - 支持导出筛选条件",
        "   - 添加导出任务队列",
        "   - 支持定时导出和自动发送",
        
        "4. 前端优化",
        "   - 优化移动端响应式设计",
        "   - 添加数据缓存机制",
        "   - 实现虚拟滚动，优化大数据量显示",
        "   - 添加更详细的错误提示",
        "   - 优化页面加载速度",
        "   - 添加更多交互动画",
        
        "5. 后端优化",
        "   - 优化数据库查询性能",
        "   - 添加请求限流机制",
        "   - 实现异步任务处理",
        "   - 添加更详细的日志记录",
        "   - 优化错误处理机制",
        "   - 添加API版本控制",
        
        "6. 功能扩展",
        "   - 实现离线模式支持",
        "   - 添加数据备份和恢复功能",
        "   - 实现用户操作日志",
        "   - 添加自定义报表功能",
        "   - 实现工作流定制",
        "   - 添加消息通知系统",
        
        "7. 安全性增强",
        "   - 添加更多权限控制",
        "   - 实现API访问限制",
        "   - 添加敏感操作审计",
        "   - 优化密码策略",
        "   - 添加二次验证机制",
        
        "8. 文档完善",
        "   - 添加API文档自动生成",
        "   - 完善用户操作手册",
        "   - 添加开发者文档",
        "   - 添加部署文档",
        "   - 添加常见问题解答"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

def main():
    """主函数"""
    print_header("系统综合测试")
    
    # 检查后端项目结构
    check_backend_structure()
    
    # 检查前端项目结构
    check_frontend_structure()
    
    # 检查数据库结构
    check_database_structure()
    
    # 运行后端测试
    run_backend_tests()
    
    # 运行批量导入测试
    run_batch_import_tests()
    
    # 生成优化建议清单
    generate_optimization_list()
    
    print("\n" + "="*80)
    print("测试完成".center(80))
    print("="*80)

if __name__ == "__main__":
    main()
