#!/usr/bin/env python3
import os
import re
from pathlib import Path

def fix_imports(directory):
    """修复目录中所有Python文件的导入路径"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file_imports(file_path)

def fix_file_imports(file_path):
    """修复单个文件的导入路径"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换导入路径
    modified_content = re.sub(r'from backend\.', 'from ', content)
    modified_content = re.sub(r'import backend\.', 'import ', modified_content)
    
    if content != modified_content:
        print(f"修复文件: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

if __name__ == "__main__":
    backend_dir = Path("backend")
    fix_imports(backend_dir)
    print("导入路径修复完成！")
