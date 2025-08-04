#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETS验证器使用演示
"""

import subprocess
import sys
from pathlib import Path


def run_demo():
    """运行演示"""
    print("=== ETS IR验证器演示 ===\n")
    
    # 1. 生成示例IR文件
    print("1. 生成示例IR文件...")
    try:
        subprocess.run([sys.executable, "sample_ir_files.py"], check=True)
        print("✓ 示例IR文件生成成功\n")
    except subprocess.CalledProcessError as e:
        print(f"✗ 生成IR文件失败: {e}")
        return
    
    # 2. 运行验证器
    print("2. 运行ETS验证器...")
    try:
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
            print("✓ 验证成功!")
        else:
            print("✗ 验证失败!")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 运行验证器失败: {e}")
        return
    
    # 3. 显示IR文件内容
    print("\n3. 示例IR文件内容:")
    ir_dir = Path("/tmp/ets_checker/ir_dump")
    for ir_file in sorted(ir_dir.glob("*.ir")):
        print(f"\n--- {ir_file.name} ---")
        with open(ir_file, 'r') as f:
            print(f.read())


def explain_validation_logic():
    """解释验证逻辑"""
    print("\n=== 验证逻辑说明 ===\n")
    
    print("1. 指令计数验证 (INST_COUNT):")
    print("   - 统计IR中特定指令的出现次数")
    print("   - 格式: //! INST_COUNT /pattern/,expected_count")
    print("   - 示例: //! INST_COUNT /Intrinsic.StdCoreSbAppendString/,2")
    print("   - 验证IR中StdCoreSbAppendString指令出现2次\n")
    
    print("2. 指令存在验证 (INST):")
    print("   - 验证特定指令存在于IR中")
    print("   - 格式: //! INST /pattern/")
    print("   - 示例: //! INST /StringBuilder::<ctor>/")
    print("   - 验证IR中存在StringBuilder构造函数\n")
    
    print("3. 指令不存在验证 (INST_NOT):")
    print("   - 验证特定指令不存在于IR中")
    print("   - 格式: //! INST_NOT /pattern/")
    print("   - 示例: //! INST_NOT /Intrinsic.StdCoreSbToString/")
    print("   - 验证IR中不存在StdCoreSbToString指令\n")
    
    print("4. 基本块验证 (IN_BLOCK):")
    print("   - 在指定基本块中搜索指令")
    print("   - 格式: //! IN_BLOCK /block_name/")
    print("   - 示例: //! IN_BLOCK /loop/")
    print("   - 在循环基本块中搜索后续指令\n")
    
    print("5. 优化Pass验证:")
    print("   - PASS_BEFORE: 验证优化前的IR")
    print("   - PASS_AFTER: 验证优化后的IR")
    print("   - 示例: //! PASS_AFTER \"SimplifyStringBuilder\"")
    print("   - 验证SimplifyStringBuilder优化后的IR\n")
    
    print("6. 方法选择 (METHOD):")
    print("   - 选择要验证的特定方法")
    print("   - 格式: //! METHOD \"method_name\"")
    print("   - 示例: //! METHOD \"ets_string_concat_loop.ETSGLOBAL::concat_loop0\"")
    print("   - 选择concat_loop0方法进行验证\n")


if __name__ == "__main__":
    run_demo()
    explain_validation_logic() 