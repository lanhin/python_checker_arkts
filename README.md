# ETS IR验证器 - Python实现

基于`checker.rb`逻辑的Python实现，用于解析`ets_string_concat_loop.ets`文件中的验证指令并验证IR输出。

## 项目概述

本项目是ArkTS编译器IR验证工具的Python重实现，主要用于验证编译器优化后的中间表示(IR)是否符合预期。特别适用于验证字符串连接循环优化等编译器优化功能。

## 功能特性

### 1. 支持的验证指令

- **METHOD**: 选择要验证的方法（支持方法名特殊字符处理）
- **PASS_BEFORE/PASS_AFTER**: 选择优化Pass前后的IR
- **IN_BLOCK**: 在指定基本块中搜索
- **INST**: 验证指令存在
- **INST_NOT**: 验证指令不存在
- **INST_COUNT**: 验证指令出现次数

### 2. 核心组件

#### `ets_checker.py` - 主验证器
```python
# 基本用法
python ets_checker.py test_file.ets --work-dir /path/to/work/dir
```

#### `sample_ir_files.py` - 示例IR文件生成器
```python
# 生成示例IR文件
python sample_ir_files.py
```

#### `demo_usage.py` - 使用演示
```python
# 运行完整演示
python demo_usage.py
```

#### `test_method_handling.py` - 方法名处理测试
```python
# 测试方法名处理逻辑
python test_method_handling.py
```

#### `simple_test.py` - 简单测试
```python
# 运行简单测试
python simple_test.py
```

## 验证逻辑详解

### 1. 指令计数验证 (INST_COUNT)

验证IR中特定指令的出现次数是否符合预期。

```bash
//! INST_COUNT /Intrinsic.StdCoreSbAppendString/,2
```

**验证逻辑**:
- 在IR文件中搜索`Intrinsic.StdCoreSbAppendString`
- 统计出现次数
- 验证是否等于2

### 2. 指令存在验证 (INST)

验证特定指令存在于IR中。

```bash
//! INST /StringBuilder::<ctor>/
```

**验证逻辑**:
- 在IR文件中搜索`StringBuilder::<ctor>`
- 如果找到则通过，否则失败

### 3. 指令不存在验证 (INST_NOT)

验证特定指令不存在于IR中。

```bash
//! INST_NOT /Intrinsic.StdCoreSbToString/
```

**验证逻辑**:
- 在IR文件中搜索`Intrinsic.StdCoreSbToString`
- 如果没找到则通过，否则失败

### 4. 基本块验证 (IN_BLOCK)

在指定基本块中搜索指令。

```bash
//! IN_BLOCK /loop/
//! INST /Intrinsic.StdCoreSbAppendString/
```

**验证逻辑**:
- 定位到循环基本块
- 在该块中搜索指定指令

### 5. 优化Pass验证

验证优化前后的IR变化。

```bash
//! PASS_BEFORE "BranchElimination"
//! INST_COUNT /StringBuilder::<ctor>/,2
//! PASS_AFTER "SimplifyStringBuilder"
//! INST_COUNT /StringBuilder::<ctor>/,1
```

**验证逻辑**:
- 选择BranchElimination之前的IR文件
- 验证StringBuilder构造函数出现2次
- 选择SimplifyStringBuilder之后的IR文件
- 验证StringBuilder构造函数出现1次（优化后减少）

### 6. 方法选择验证 (METHOD)

选择要验证的特定方法，支持方法名特殊字符处理。

```bash
//! METHOD "ets_string_concat_loop.ETSGLOBAL::concat_loop0"
```

**验证逻辑**:
- 处理方法名：将`::`、`<>`、`.`、`-`等特殊字符替换为`_`
- 示例：`ETSGLOBAL::concat_loop0` → `ETSGLOBAL_concat_loop0`
- 在IR文件名中搜索处理后的方法名
- 加载匹配的IR文件进行后续验证

## 文件结构

```
.
├── ets_checker.py              # 主验证器
├── sample_ir_files.py          # 示例IR文件生成器
├── demo_usage.py               # 使用演示
├── test_method_handling.py     # 方法名处理测试
├── simple_test.py              # 简单测试
├── test_sample.ets             # 示例测试文件
└── README_Python_Checker.md    # 说明文档
```

## 使用示例

### 1. 基本验证

```bash
# 运行验证器
python ets_checker.py test_sample.ets --work-dir /tmp/ets_checker
```

### 2. 完整演示

```bash
# 运行完整演示
python demo_usage.py
```

### 3. 生成示例IR文件

```bash
# 生成示例IR文件
python sample_ir_files.py
```

### 4. 测试方法名处理

```bash
# 测试方法名处理逻辑
python test_method_handling.py

# 运行简单测试
python simple_test.py
```

## 验证流程

1. **解析测试文件**: 读取`.ets`文件中的验证指令
2. **加载IR文件**: 从`ir_dump`目录加载IR转储文件
3. **执行验证**: 根据指令类型执行相应的验证逻辑
4. **输出结果**: 报告验证成功或失败

## 错误处理

验证器会报告以下类型的错误：

- **文件未找到**: IR文件或测试文件不存在
- **指令未找到**: 期望的指令在IR中不存在
- **计数不匹配**: 指令出现次数与期望不符
- **Pass未找到**: 指定的优化Pass不存在
- **方法未找到**: 指定的方法在IR文件中不存在

## 扩展功能

### 添加新的验证指令

在`ETSChecker`类中添加新的方法：

```python
def NEW_COMMAND(self, args):
    """新的验证命令"""
    # 实现验证逻辑
    pass
```

### 支持新的IR格式

修改`IRScope`类中的解析逻辑：

```python
def _parse_ir_format(self, line):
    """解析新的IR格式"""
    # 实现解析逻辑
    pass
```

## 与原始checker.rb的对比

| 功能 | checker.rb | ets_checker.py |
|------|------------|----------------|
| 语言 | Ruby | Python |
| 复杂度 | 高 | 中等 |
| 可读性 | 中等 | 高 |
| 扩展性 | 中等 | 高 |
| 维护性 | 中等 | 高 |
| 方法名处理 | 支持 | 支持（修正后） |
| 错误报告 | 详细 | 详细 |

## 技术实现

### 核心类设计

#### `IRScope`类
- 负责IR文件的搜索和匹配
- 支持正则表达式和字符串匹配
- 提供计数、查找、块搜索等功能

#### `ETSChecker`类
- 主要的验证器类
- 管理验证状态和IR文件
- 执行各种验证指令

### 方法名处理逻辑

```python
# 与checker.rb保持一致的处理逻辑
processed_method = re.sub(r'::|[<>]|\.|-', '_', method_name)
```

### 文件匹配机制

```python
# 使用glob模式匹配IR文件
ir_pattern = work_dir / "ir_dump" / f"*{processed_method}*.ir"
ir_files = sorted(glob.glob(str(ir_pattern)))
```

## 注意事项

1. **IR文件格式**: 确保IR文件格式与验证器期望的格式一致
2. **路径配置**: 正确设置工作目录和IR文件路径
3. **编码问题**: 确保文件使用UTF-8编码
4. **权限问题**: 确保有足够的文件读写权限
5. **方法名处理**: 注意方法名中的特殊字符会被替换为下划线

## 测试和验证

### 运行所有测试

```bash
# 1. 生成示例IR文件
python sample_ir_files.py

# 2. 运行验证器
python ets_checker.py test_sample.ets --work-dir /tmp/ets_checker

# 3. 运行演示
python demo_usage.py

# 4. 运行测试
python test_method_handling.py
python simple_test.py
```

### 验证要点

1. **方法名处理**: 确保特殊字符正确替换
2. **文件匹配**: 确保能正确找到IR文件
3. **指令验证**: 确保指令计数和存在性验证正确
4. **错误处理**: 确保错误信息清晰有用

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目基于Apache License 2.0许可证。

## 更新日志

### v1.0.0
- 初始版本，实现基本的IR验证功能
- 支持所有主要验证指令
- 实现方法名特殊字符处理
- 添加完整的测试和演示

### v1.1.0
- 修正METHOD方法名处理逻辑
- 改进错误报告和日志输出
- 添加更多测试用例
- 完善文档说明 