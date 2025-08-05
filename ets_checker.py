#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETS IR验证器 - 基于checker.rb逻辑的Python实现
用于解析ets_string_concat_loop.ets文件中的验证指令并验证IR输出
"""

import os
import re
import glob
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SearchState(Enum):
    NONE = 0
    SEARCH_BODY = 1
    SEARCH_END = 2


@dataclass
class IRScope:
    """IR搜索范围"""
    lines: List[str]
    name: str
    current_index: int = 0

    def find(self, match: str) -> Optional[str]:
        """查找匹配的行"""
        if not match:
            return None
        
        for i, line in enumerate(self.lines[self.current_index:], self.current_index):
            if self._contains(line, match):
                self.current_index = i + 1
                return line
        return None

    def find_next(self, match: str) -> Optional[str]:
        """查找下一个匹配的行"""
        if not match:
            return None
        
        for i, line in enumerate(self.lines[self.current_index:], self.current_index):
            if self._contains(line, match):
                self.current_index = i + 1
                return line
        return None

    def exists(self, match: str) -> bool:
        """检查是否存在匹配的行"""
        if not match:
            return False
        
        for line in self.lines[self.current_index:]:
            if self._contains(line, match):
                return True
        return False

    def find_next_not(self, match: str) -> Optional[str]:
        """查找下一个不匹配的行"""
        if not match:
            return None
        
        for i, line in enumerate(self.lines[self.current_index:], self.current_index):
            if not self._contains(line, match):
                self.current_index = i + 1
                return line
        return None

    def find_block(self, match: str) -> Optional['IRScope']:
        """查找基本块并返回该块的范围"""
        if not match:
            return None
        
        # 查找基本块的开始
        start_index = None
        for i, line in enumerate(self.lines[self.current_index:], self.current_index):
            if self._contains(line, match):
                start_index = i
                break
        
        if start_index is None:
            return None
        
        # 查找基本块的结束（下一个基本块开始或文件结束）
        end_index = len(self.lines)
        for i in range(start_index + 1, len(self.lines)):
            line = self.lines[i]
            # 检查是否是新的基本块开始（通常以 "prop:" 开头）
            if line.strip().startswith("prop:"):
                end_index = i
                break
        
        # 创建新的IRScope，只包含该基本块的内容
        block_lines = self.lines[start_index:end_index]
        block_scope = IRScope(block_lines, f"block_{match}", 0)
        
        # 更新当前索引到基本块结束位置
        self.current_index = end_index
        
        return block_scope

    def count(self, match: str) -> int:
        """统计匹配的行数"""
        if not match:
            return 0
        
        count = 0
        for line in self.lines:
            if self._contains(line, match) and not line.startswith("Method:"):
                count += 1
        return count

    def _contains(self, line: str, match: str) -> bool:
        """检查行是否包含匹配模式"""
        if match.startswith('/') and match.endswith('/'):
            # 正则表达式匹配
            pattern = match[1:-1]
            return bool(re.search(pattern, line))
        else:
            # 字符串匹配
            return match in line

    @classmethod
    def from_file(cls, filename: str, name: str) -> 'IRScope':
        """从文件创建IRScope"""
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return cls(lines, name)


class ETSChecker:
    """ETS IR验证器"""

    def __init__(self, work_dir: str = "/tmp/ets_checker"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # 当前状态
        self.current_method: Optional[str] = None
        self.current_pass: Optional[str] = None
        self.ir_scope: Optional[IRScope] = None
        self.ir_files: List[str] = []
        self.current_file_index: int = 0
        
        # 验证结果
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def raise_error(self, message: str):
        """记录错误"""
        error_msg = f"Test failed: {self.current_method or 'unknown'}"
        if self.current_pass:
            error_msg += f" (Pass: {self.current_pass})"
        error_msg += f" - {message}"
        self.errors.append(error_msg)
        print(f"ERROR: {error_msg}")

    def log_info(self, message: str):
        """记录信息"""
        print(f"INFO: {message}")

    def METHOD(self, match: str):
        """选择要验证的方法"""
        self.current_method = match
        self.log_info(f"Selecting method: {match}")
        
        # 处理方法名，将特殊字符替换为下划线（与checker.rb保持一致）
        processed_method = re.sub(r'::|[<>]|\.|-', '_', match)
        self.log_info(f"Processed method name: {processed_method}")
        
        # 查找包含处理后方法名的IR文件
        ir_pattern = self.work_dir / "ir_dump" / f"*{processed_method}*.ir"
        self.ir_files = sorted(glob.glob(str(ir_pattern)))
        
        if not self.ir_files:
            self.raise_error(f"IR dumps not found for method: {processed_method}")
            return
        
        self.current_file_index = 0
        self.ir_scope = IRScope.from_file(self.ir_files[self.current_file_index], 'IR')
        self.log_info(f"Loaded IR file: {self.ir_files[self.current_file_index]}")
        self.log_info(f"Found {len(self.ir_files)} IR files for method: {match}")

    def PASS_BEFORE(self, pass_name: str):
        """选择指定pass之前的IR文件"""
        self.current_pass = f"Pass before: {pass_name}"
        self.log_info(f"Selecting pass before: {pass_name}")
        
        # 查找包含pass名称的文件
        for i, ir_file in enumerate(self.ir_files):
            if pass_name in os.path.basename(ir_file):
                self.current_file_index = i - 1 if i > 0 else 0
                self.ir_scope = IRScope.from_file(self.ir_files[self.current_file_index], 'IR')
                self.log_info(f"Loaded IR file: {self.ir_files[self.current_file_index]}")
                return
        
        self.raise_error(f"IR file not found for pass: {pass_name}")

    def PASS_AFTER(self, pass_name: str):
        """选择指定pass之后的IR文件"""
        self.current_pass = f"Pass after: {pass_name}"
        self.log_info(f"Selecting pass after: {pass_name}")
        
        # 查找包含pass名称的文件
        for i, ir_file in enumerate(self.ir_files):
            if pass_name in os.path.basename(ir_file):
                self.current_file_index = i
                self.ir_scope = IRScope.from_file(self.ir_files[self.current_file_index], 'IR')
                self.log_info(f"Loaded IR file: {self.ir_files[self.current_file_index]}")
                return
        
        self.raise_error(f"IR file not found for pass: {pass_name}")

    def IN_BLOCK(self, match: str):
        """在指定基本块中搜索"""
        if not self.ir_scope:
            self.raise_error("No IR scope selected")
            return
        
        self.log_info(f"Searching in block: {match}")
        block_scope = self.ir_scope.find_block(f"prop: {match}")
        if not block_scope:
            self.raise_error(f"Block not found: {match}")
        else:
            # 将当前搜索范围切换到找到的基本块
            self.ir_scope = block_scope

    def INST(self, match: str):
        """查找指定指令"""
        if not self.ir_scope:
            self.raise_error("No IR scope selected")
            return
        
        self.log_info(f"Searching for instruction: {match}")
        result = self.ir_scope.find(match)
        if not result:
            self.raise_error(f"Instruction not found: {match}")

    def INST_NOT(self, match: str):
        """验证指令不存在"""
        if not self.ir_scope:
            self.raise_error("No IR scope selected")
            return
        
        self.log_info(f"Verifying instruction not present: {match}")
        exists = self.ir_scope.exists(match)
        if exists:
            self.raise_error(f"Instruction should not exist: {match}")

    def INST_COUNT(self, match: str, expected_count: int):
        """验证指令出现次数"""
        if not self.ir_scope:
            self.raise_error("No IR scope selected")
            return
        
        actual_count = self.ir_scope.count(match)
        self.log_info(f"Counting instruction: {match}, expected: {expected_count}, actual: {actual_count}")
        
        if actual_count != expected_count:
            self.raise_error(f"Instruction count mismatch for {match}: expected={expected_count}, actual={actual_count}")

    def parse_test_file(self, test_file: str):
        """解析测试文件中的验证指令"""
        if not os.path.exists(test_file):
            self.raise_error(f"Test file not found: {test_file}")
            return
        
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 解析验证指令
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or (line.startswith('//') and not line.startswith('//!')):
                continue
            
            # 解析指令
            parts = line[3:].strip().split(None, 1)  # 去掉 '//! '
            if len(parts) < 1:
                continue
            
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            try:
                self._execute_command(command, args, line_num)
            except Exception as e:
                self.raise_error(f"Error executing command '{command}' at line {line_num}: {e}")

    def _execute_command(self, command: str, args: str, line_num: int):
        """执行验证命令"""
        if command == "METHOD":
            # 解析方法名
            method_match = re.search(r'"([^"]+)"', args)
            if method_match:
                self.METHOD(method_match.group(1))
            else:
                self.raise_error(f"Invalid METHOD format at line {line_num}")
        
        elif command == "PASS_BEFORE":
            # 解析pass名称
            pass_match = re.search(r'"([^"]+)"', args)
            if pass_match:
                self.PASS_BEFORE(pass_match.group(1))
            else:
                self.raise_error(f"Invalid PASS_BEFORE format at line {line_num}")
        
        elif command == "PASS_AFTER":
            # 解析pass名称
            pass_match = re.search(r'"([^"]+)"', args)
            if pass_match:
                self.PASS_AFTER(pass_match.group(1))
            else:
                self.raise_error(f"Invalid PASS_AFTER format at line {line_num}")
        
        elif command == "IN_BLOCK":
            # 解析块名称
            block_match = re.search(r'/([^/]+)/', args)
            if block_match:
                self.IN_BLOCK(block_match.group(1))
            else:
                self.raise_error(f"Invalid IN_BLOCK format at line {line_num}")
        
        elif command == "INST":
            # 解析指令模式
            inst_match = re.search(r'/([^/]+)/', args)
            if inst_match:
                self.INST(inst_match.group(1))
            else:
                self.raise_error(f"Invalid INST format at line {line_num}")
        
        elif command == "INST_NOT":
            # 解析指令模式
            inst_match = re.search(r'/([^/]+)/', args)
            if inst_match:
                self.INST_NOT(inst_match.group(1))
            else:
                self.raise_error(f"Invalid INST_NOT format at line {line_num}")
        
        elif command == "INST_COUNT":
            # 解析指令计数
            # 格式: /pattern/,count
            count_match = re.search(r'/([^/]+)/,(\d+)', args)
            if count_match:
                pattern = count_match.group(1)
                count = int(count_match.group(2))
                self.INST_COUNT(pattern, count)
            else:
                self.raise_error(f"Invalid INST_COUNT format at line {line_num}")
        
        elif command in ["CHECKER", "SKIP_IF", "RUN", "RUN_PAOC"]:
            # 这些命令在解析阶段不需要执行
            pass
        
        else:
            self.log_info(f"Unknown command: {command} at line {line_num}")

    def run_validation(self, test_file: str):
        """运行完整的验证流程"""
        self.log_info(f"Starting validation for: {test_file}")
        
        # 解析测试文件
        self.parse_test_file(test_file)
        
        # 输出结果
        if self.errors:
            self.log_info(f"Validation failed with {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  - {error}")
            return False
        else:
            self.log_info("Validation completed successfully!")
            return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ETS IR验证器')
    parser.add_argument('test_file', help='测试文件路径')
    parser.add_argument('--work-dir', default='/tmp/ets_checker', help='工作目录')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建验证器
    checker = ETSChecker(args.work_dir)
    
    # 运行验证
    success = checker.run_validation(args.test_file)
    
    # 返回退出码
    exit(0 if success else 1)


if __name__ == "__main__":
    main() 