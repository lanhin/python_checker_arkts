#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的METHOD方法名处理测试
"""

import re
from pathlib import Path


def test_method_name_processing():
    """测试方法名处理"""
    print("=== METHOD方法名处理测试 ===\n")
    
    # 测试用例
    test_cases = [
        "ets_string_concat_loop.ETSGLOBAL::concat_loop0",
        "ets_string_concat_loop.ETSGLOBAL::concat_loop5",
        "MyClass<T>::method",
        "namespace::Class::method",
        "test.method-name"
    ]
    
    for method_name in test_cases:
        # 应用与checker.rb相同的处理逻辑
        processed = re.sub(r'::|[<>]|\.|-', '_', method_name)
        print(f"原始方法名: {method_name}")
        print(f"处理后方法名: {processed}")
        print(f"预期文件名模式: *{processed}*.ir")
        print("-" * 50)
    
    print("\n✓ 方法名处理测试完成!")


def test_file_matching():
    """测试文件匹配"""
    print("\n=== 文件匹配测试 ===\n")
    
    # 创建测试目录和文件
    work_dir = Path("/tmp/ets_checker/ir_dump")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建测试文件
    test_files = [
        "001_pass_0001_ets_string_concat_loop_ETSGLOBAL_concat_loop0_BranchElimination.ir",
        "002_pass_0002_ets_string_concat_loop_ETSGLOBAL_concat_loop0_SimplifyStringBuilder.ir",
        "003_pass_0003_ets_string_concat_loop_ETSGLOBAL_concat_loop5_ChecksElimination.ir"
    ]
    
    for filename in test_files:
        file_path = work_dir / filename
        with open(file_path, 'w') as f:
            f.write(f"# Test IR file: {filename}\n")
        print(f"创建文件: {filename}")
    
    # 测试方法名匹配
    method_name = "ets_string_concat_loop.ETSGLOBAL::concat_loop0"
    processed_method = re.sub(r'::|[<>]|\.|-', '_', method_name)
    
    print(f"\n测试方法名: {method_name}")
    print(f"处理后方法名: {processed_method}")
    
    # 查找匹配的文件
    matching_files = list(work_dir.glob(f"*{processed_method}*.ir"))
    
    print(f"匹配的文件:")
    for file in matching_files:
        print(f"  - {file.name}")
    
    print(f"总共找到 {len(matching_files)} 个匹配文件")
    
    if len(matching_files) == 2:  # 应该找到2个文件
        print("✓ 文件匹配测试成功!")
    else:
        print("✗ 文件匹配测试失败!")


if __name__ == "__main__":
    test_method_name_processing()
    test_file_matching() 