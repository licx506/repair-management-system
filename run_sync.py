#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件同步工具启动脚本

这是一个位于项目根目录的启动脚本，用于启动文件同步工具。
"""

import sys
import os

# 将sync目录添加到模块搜索路径
sync_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sync')
sys.path.insert(0, sync_dir)

print(f"Python搜索路径: {sys.path}")
print(f"当前工作目录: {os.getcwd()}")
print(f"sync目录: {sync_dir}")

try:
    # 导入cli模块
    from cli import run_cli
    print("成功导入cli模块")
except ImportError as e:
    print(f"导入cli模块失败: {str(e)}")
    sys.exit(1)

def main():
    """主函数"""
    run_cli()

if __name__ == "__main__":
    main()
