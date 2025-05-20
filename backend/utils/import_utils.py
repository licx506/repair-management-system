#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导入工具函数
"""

import csv
import io
import logging
from typing import List, Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

def parse_csv(file_content: bytes) -> List[Dict[str, Any]]:
    """
    解析CSV文件内容为字典列表
    
    Args:
        file_content: CSV文件内容的字节流
        
    Returns:
        字典列表，每个字典代表一行数据
    """
    try:
        # 尝试检测编码
        content = file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = file_content.decode('gbk')
        except UnicodeDecodeError:
            content = file_content.decode('utf-8', errors='ignore')
    
    # 创建CSV读取器
    csv_file = io.StringIO(content)
    reader = csv.DictReader(csv_file)
    
    # 读取所有行
    rows = []
    for row in reader:
        # 清理数据：移除空白字符，跳过空行
        cleaned_row = {}
        has_data = False
        for key, value in row.items():
            if key is None:
                continue
                
            key = key.strip()
            if not key:
                continue
                
            if value is not None:
                value = value.strip()
                if value:
                    has_data = True
            
            cleaned_row[key] = value
        
        if has_data:
            rows.append(cleaned_row)
    
    return rows

def process_import(
    file_content: bytes,
    required_fields: List[str],
    process_row_func: Callable[[Dict[str, Any]], Any],
    validate_func: Optional[Callable[[List[Dict[str, Any]]], None]] = None
) -> List[Any]:
    """
    处理导入的通用函数
    
    Args:
        file_content: 文件内容的字节流
        required_fields: 必需的字段列表
        process_row_func: 处理每一行数据的函数
        validate_func: 验证所有数据的函数（可选）
        
    Returns:
        处理结果列表
    """
    # 解析CSV文件
    rows = parse_csv(file_content)
    
    if not rows:
        raise ValueError("文件为空或格式不正确")
    
    # 检查必需字段
    first_row = rows[0]
    missing_fields = [field for field in required_fields if field not in first_row]
    if missing_fields:
        raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
    
    # 验证数据（如果提供了验证函数）
    if validate_func:
        validate_func(rows)
    
    # 处理每一行数据
    results = []
    for row in rows:
        try:
            result = process_row_func(row)
            results.append(result)
        except Exception as e:
            logger.error(f"处理行数据失败: {row}, 错误: {str(e)}")
            raise ValueError(f"处理数据失败: {str(e)}")
    
    return results
