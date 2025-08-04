#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成示例IR文件用于演示ETS验证器
"""

import os
from pathlib import Path


def create_sample_ir_files():
    """创建示例IR文件"""
    work_dir = Path("/tmp/ets_checker/ir_dump")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建BranchElimination之前的IR文件
    # 注意：方法名中的::被替换为_，所以ETSGLOBAL::concat_loop0变成ETSGLOBAL_concat_loop0
    branch_elim_before = work_dir / "001_pass_0001_ets_string_concat_loop_ETSGLOBAL_concat_loop0_BranchElimination.ir"
    with open(branch_elim_before, 'w') as f:
        f.write("""Method: ets_string_concat_loop.ETSGLOBAL::concat_loop0
BB 0 (loop)
  v0 = StringBuilder::<ctor>()
  v1 = Intrinsic.StdCoreSbAppendString(v0, v2)
  v3 = Intrinsic.StdCoreSbAppendString(v1, v4)
  v5 = Intrinsic.StdCoreSbToString(v3)
  return v5
""")
    
    # 创建SimplifyStringBuilder之后的IR文件
    simplify_after = work_dir / "002_pass_0002_ets_string_concat_loop_ETSGLOBAL_concat_loop0_SimplifyStringBuilder.ir"
    with open(simplify_after, 'w') as f:
        f.write("""Method: ets_string_concat_loop.ETSGLOBAL::concat_loop0
BB 0 (prehead)
  v0 = StringBuilder::<ctor>()
  v1 = Intrinsic.StdCoreSbAppendString(v0, v2)
BB 1 (loop)
  v3 = Intrinsic.StdCoreSbAppendString(v1, v4)
BB 2 (exit)
  v5 = Intrinsic.StdCoreSbToString(v3)
  return v5
""")
    
    # 创建ChecksElimination之后的IR文件
    checks_elim_after = work_dir / "003_pass_0003_ets_string_concat_loop_ETSGLOBAL_concat_loop5_ChecksElimination.ir"
    with open(checks_elim_after, 'w') as f:
        f.write("""Method: ets_string_concat_loop.ETSGLOBAL::concat_loop5
BB 0 (prehead)
  v0 = StringBuilder::<ctor>()
  v1 = Intrinsic.StdCoreSbAppendString(v0, v2)
BB 1 (loop)
  v3 = Intrinsic.StdCoreSbAppendString2(v1, v4)
BB 2 (exit)
  v5 = Intrinsic.StdCoreSbToString(v3)
  return v5
""")
    
    print(f"Created sample IR files in {work_dir}")
    print("Files created:")
    for ir_file in work_dir.glob("*.ir"):
        print(f"  - {ir_file.name}")


if __name__ == "__main__":
    create_sample_ir_files() 