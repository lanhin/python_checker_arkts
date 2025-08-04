#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试METHOD方法名处理的正确性
"""

import re
import subprocess
import sys
from pathlib import Path


def test_method_name_processing():
    """测试方法名处理逻辑"""
    print("=== 测试方法名处理逻辑 ===\n")
    
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


def test_ir_file_matching():
    """测试IR文件匹配"""
    print("\n=== 测试IR文件匹配 ===\n")
    
    # 创建测试IR文件
    work_dir = Path("/tmp/ets_checker/ir_dump")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建一些测试IR文件
    test_files = [
        "001_pass_0001_ets_string_concat_loop_ETSGLOBAL_concat_loop0_BranchElimination.ir",
        "002_pass_0002_ets_string_concat_loop_ETSGLOBAL_concat_loop0_SimplifyStringBuilder.ir",
        "003_pass_0003_ets_string_concat_loop_ETSGLOBAL_concat_loop5_ChecksElimination.ir",
        "004_pass_0004_other_method_SomePass.ir"
    ]
    
    for filename in test_files:
        file_path = work_dir / filename
        with open(file_path, 'w') as f:
            f.write(f"# Test IR file: {filename}\n")
        print(f"创建测试文件: {filename}")
    
    # 测试方法名匹配
    method_name = "ets_string_concat_loop.ETSGLOBAL::concat_loop0"
    processed_method = re.sub(r'::|[<>]|\.|-', '_', method_name)
    
    print(f"\n测试方法名: {method_name}")
    print(f"处理后方法名: {processed_method}")
    
    # 查找匹配的文件
    pattern = work_dir / f"*{processed_method}*.ir"
    matching_files = list(work_dir.glob(f"*{processed_method}*.ir"))
    
    print(f"匹配的文件:")
    for file in matching_files:
        print(f"  - {file.name}")
    
    print(f"总共找到 {len(matching_files)} 个匹配文件")


def test_checker_integration():
    """测试验证器集成"""
    print("\n=== 测试验证器集成 ===\n")
    
    try:
        # 运行验证器
        result = subprocess.run([
            sys.executable, "ets_checker.py",
            "test_sample.ets",
            "--work-dir", "/tmp/ets_checker"
        ], capture_output=True, text=True)
        
        print("验证器输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✓ 验证器运行成功!")
        else:
            print("✗ 验证器运行失败!")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 运行验证器失败: {e}")


def main():
    """主函数"""
    print("开始测试METHOD方法名处理...\n")
    
    # 1. 测试方法名处理逻辑
    test_method_name_processing()
    
    # 2. 测试IR文件匹配
    test_ir_file_matching()
    
    # 3. 测试验证器集成
    test_checker_integration()
    
    print("\n测试完成!")


if __name__ == "__main__":
    main() 