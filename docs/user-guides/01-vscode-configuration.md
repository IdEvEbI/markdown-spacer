---
**文档标题**：VS Code 开发环境使用指南
**文档版本**：v1.1
**创建时间**：2025-07-22
**更新时间**：2025-07-22
**维护人员**：刘凡 & 小克
**文档状态**：已完成
---

# VS Code 开发环境使用指南

## 1. 概述

本项目的 `.vscode/` 目录包含 VS Code 工作区配置文件，用于统一开发环境设置，确保团队成员使用一致的开发体验。

## 2. 配置文件说明

### 2.1 settings.json - 工作区设置

**文件路径**：`.vscode/settings.json`

**作用**：定义 VS Code 工作区的全局设置，影响所有打开的文件和功能。

**配置详解**：

```json
{
    // Python 解释器设置
    "python.defaultInterpreterPath": "./venv/bin/python",
    
    // 测试设置
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests/"
    ],
    
    // 文件排除设置
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/.pytest_cache": true
    },
    
    // 编辑器设置
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    
    // 文件关联设置
    "files.associations": {
        "*.toml": "toml",
        "*.md": "markdown"
    }
}
```

**配置项说明**：

| 配置项 | 作用 | 说明 |
|--------|------|------|
| `python.defaultInterpreterPath` | 设置 Python 解释器 | 指向项目的虚拟环境，确保使用正确的 Python 版本和依赖 |
| `python.testing.pytestEnabled` | 启用 pytest 测试 | 在 VS Code 中集成 pytest 测试框架 |
| `python.testing.pytestArgs` | pytest 参数 | 指定测试目录为 `tests/` |
| `files.exclude` | 文件排除规则 | 隐藏不需要显示的文件和目录，如缓存文件、虚拟环境等 |
| `editor.formatOnSave` | 保存时自动格式化 | 保存文件时自动运行代码格式化工具 |
| `editor.codeActionsOnSave.source.organizeImports` | 保存时整理导入 | 自动整理和排序 Python 导入语句 |
| `files.associations` | 文件类型关联 | 为特定文件扩展名指定语言模式 |

### 2.2 extensions.json - 扩展推荐

**文件路径**：`.vscode/extensions.json`

**作用**：推荐团队成员安装的 VS Code 扩展，确保开发环境的一致性。

**配置详解**：

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.mypy-type-checker"
    ]
}
```

**推荐扩展说明**：

| 扩展 ID | 扩展名称 | 作用 |
|---------|----------|------|
| `ms-python.python` | Python | 核心 Python 语言支持，提供语法高亮、智能提示、调试等功能 |
| `ms-python.flake8` | Flake8 | Python 代码风格检查工具，检测代码质量问题 |
| `ms-python.black-formatter` | Black Formatter | Python 代码自动格式化工具，统一代码风格 |
| `ms-python.isort` | isort | Python 导入语句排序和格式化工具 |
| `ms-python.mypy-type-checker` | Mypy Type Checker | Python 静态类型检查工具 |

### 2.3 launch.json - 调试配置

**文件路径**：`.vscode/launch.json`

**作用**：定义 VS Code 调试器的启动配置，支持不同场景的调试需求。

**配置详解**：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Python: markdown-spacer",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/src/markdown_spacer.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "args": [
                "--help"
            ]
        }
    ]
}
```

**调试配置说明**：

#### 配置1：Python: Current File

- **用途**：调试当前打开的 Python 文件
- **适用场景**：开发单个模块或测试文件时
- **特点**：动态调试任何打开的 Python 文件

#### 配置2：Python: markdown-spacer

- **用途**：调试 markdown-spacer 主程序
- **适用场景**：测试命令行工具功能
- **特点**：固定调试主程序，预设 `--help` 参数

**配置项说明**：

| 配置项 | 作用 | 说明 |
|--------|------|------|
| `name` | 配置名称 | 在调试面板中显示的名称 |
| `type` | 调试器类型 | `debugpy` 是新的 Python 调试器 |
| `request` | 请求类型 | `launch` 表示启动新进程进行调试 |
| `program` | 程序路径 | 要调试的 Python 文件路径 |
| `console` | 控制台类型 | `integratedTerminal` 使用 VS Code 集成终端 |
| `cwd` | 工作目录 | 程序运行的工作目录 |
| `env` | 环境变量 | 设置 `PYTHONPATH` 确保模块导入正确 |
| `args` | 命令行参数 | 传递给程序的参数 |

## 3. 使用指南

### 3.1 首次设置

1. **克隆项目**后，VS Code 会自动提示安装推荐的扩展
2. **选择 Python 解释器**：按 `Cmd+Shift+P`，输入 "Python: Select Interpreter"，选择 `./venv/bin/python`
3. **验证配置**：打开任意 Python 文件，确认语法高亮和智能提示正常工作

### 3.2 日常使用

#### 代码开发

- **自动格式化**：保存文件时自动运行 black 格式化
- **导入整理**：保存时自动整理导入语句
- **代码检查**：实时显示 flake8 检查结果

#### 测试运行

- **运行测试**：在测试文件中点击 "Run Test" 按钮
- **调试测试**：在测试函数上设置断点，使用调试模式运行

#### 调试程序

- **调试当前文件**：选择 "Python: Current File" 配置
- **调试主程序**：选择 "Python: markdown-spacer" 配置
- **设置断点**：在代码行号左侧点击设置断点

### 3.3 快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `F5` | 启动调试 | 使用当前调试配置启动调试 |
| `Ctrl+F5` | 运行不调试 | 运行程序但不进入调试模式 |
| `Shift+F5` | 停止调试 | 停止当前调试会话 |
| `F9` | 切换断点 | 在当前行设置或移除断点 |
| `F10` | 单步跳过 | 执行当前行，不进入函数 |
| `F11` | 单步进入 | 进入函数内部调试 |
| `Shift+F11` | 单步跳出 | 从当前函数跳出 |

## 4. 故障排除

### 4.1 常见问题

**Q: Python 解释器路径错误**
A: 确保虚拟环境已创建，路径为 `./venv/bin/python`

**Q: 扩展不工作**
A: 检查扩展是否已安装，重启 VS Code

**Q: 调试配置失败**
A: 确认 `debugpy` 已安装，检查 Python 路径设置

**Q: 代码格式化不生效**
A: 确认 black 和 isort 已安装，检查文件保存设置

### 4.2 配置验证

运行以下命令验证配置：

```bash
# 检查 Python 解释器
python --version

# 检查扩展是否安装
pip list | grep -E "(black|isort|flake8|mypy)"

# 测试代码格式化
black --check src/
isort --check-only src/
flake8 src/
```

## 5. 版本历史

| 版本 | 日期 | 变更内容 | 负责人 |
| ---- | ---- | -------- | ------ |
| v1.1 | 2025-07-22 | 移动到 user-guides 目录，更新文档标题 | 刘凡 & 小克 |
| v1.0 | 2025-07-22 | 初始 VS Code 配置说明 | 刘凡 & 小克 |
