---
**文档标题**：markdown-spacer 开发环境搭建文档
**文档版本**：v1.0
**创建时间**：2025-07-22
**更新时间**：2025-07-22
**维护人员**：刘凡 & 小克
**文档状态**：进行中
---

# markdown-spacer 开发环境搭建文档

## 1. 环境要求

### 1.1 基础环境

- **Python 版本**：3.12+
- **操作系统**：macOS / Linux / Windows
- **Git 版本**：2.0+
- **内存要求**：建议 4GB+

### 1.2 开发工具

- **代码编辑器**：VS Code
- **终端工具**：iTerm2 / Terminal / PowerShell
- **版本控制**：Git

## 2. 项目结构

### 2.1 目录结构

```ini
markdown-spacer/
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── markdown_spacer.py      # 主程序入口
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── formatter.py        # 格式化核心算法
│   │   ├── file_handler.py     # 文件处理模块
│   │   └── config.py           # 配置管理模块
│   ├── cli/                    # 命令行接口
│   │   ├── __init__.py
│   │   └── parser.py           # 参数解析
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── logger.py           # 日志工具
│       └── validator.py        # 验证工具
├── tests/                      # 测试目录
│   ├── __init__.py
│   ├── test_formatter.py       # 格式化测试
│   ├── test_file_handler.py    # 文件处理测试
│   └── test_cli.py             # 命令行测试
├── docs/                       # 文档目录（已存在）
├── requirements.txt            # 项目依赖
├── requirements-dev.txt        # 开发依赖
├── setup.py                    # 安装配置
├── pyproject.toml              # 项目配置
├── .gitignore                  # Git 忽略文件
├── .markdownlint.jsonc         # Markdown 格式检查
├── README.md                   # 项目说明
└── LICENSE                     # 许可证文件
```

### 2.2 文件说明

- **src/**：核心源代码，按模块组织
- **tests/**：单元测试和集成测试
- **requirements.txt**：生产环境依赖
- **requirements-dev.txt**：开发环境依赖（包含测试工具）
- **setup.py**：Python 包安装配置
- **pyproject.toml**：现代 Python 项目配置

## 3. 环境搭建步骤

### 3.1 克隆项目

```bash
# 克隆项目到本地
git clone https://github.com/IdEvEbI/markdown-spacer.git
cd markdown-spacer

# 切换到开发分支
git checkout develop
```

### 3.2 Python 环境准备

```bash
# 检查 Python 版本
python --version  # 确保 >= 3.12

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3.3 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装项目（开发模式）
pip install -e .
```

### 3.4 开发工具配置

#### VS Code 配置

创建 `.vscode/settings.json`：

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### 预提交钩子配置

```bash
# 安装 pre-commit
pip install pre-commit

# 安装钩子
pre-commit install
```

## 4. 依赖管理

### 4.1 生产依赖

```txt
# requirements.txt
click>=8.0.0
pathlib2>=2.3.0
```

### 4.2 开发依赖

```txt
# requirements-dev.txt
# 测试框架
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# 代码质量
flake8>=6.0.0
black>=23.0.0
isort>=5.12.0

# 类型检查
mypy>=1.0.0

# 预提交钩子
pre-commit>=3.0.0

# 文档工具
sphinx>=6.0.0
sphinx-rtd-theme>=1.2.0
```

### 4.3 项目配置

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "markdown-spacer"
version = "0.1.0"
description = "A Python command-line tool for handling spacing between Chinese, English, and numbers in Markdown files"
authors = [{name = "刘凡", email = "idevebi@163.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "click>=8.0.0",
    "pathlib2>=2.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "flake8>=6.0.0",
    "black>=23.0.0",
    "pre-commit>=3.0.0",
]

[project.scripts]
markdown-spacer = "src.markdown_spacer:main"

[tool.black]
line-length = 88
target-version = ['py312']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing"
```

## 5. pre-commit 钩子配置

### 5.1 作用

- 统一和自动化代码风格检查，保障代码质量，减少低级错误进入主分支。
- 自动执行 black 格式化、flake8 语法检查、isort 导入排序、mypy 类型检查等。
- 只检查 src/ 和 tests/ 目录下的 Python 代码。

### 5.2 配置步骤

1. 确保已安装 pre-commit（见 requirements-dev.txt 或 pyproject.toml）。
2. 在项目根目录新建 .pre-commit-config.yaml，内容如下：

   ```yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.7.0
       hooks:
         - id: black
           language_version: python3.12
           files: ^src/|^tests/
     - repo: https://github.com/pycqa/flake8
       rev: 6.1.0
       hooks:
         - id: flake8
           additional_dependencies: []
           files: ^src/|^tests/
     - repo: https://github.com/PyCQA/isort
       rev: 5.12.0
       hooks:
         - id: isort
           files: ^src/|^tests/
     - repo: https://github.com/pre-commit/mirrors-mypy
       rev: v1.5.1
       hooks:
         - id: mypy
           files: ^src/|^tests/
   ```

3. 安装 pre-commit 钩子（仅需一次）：

   ```bash
   pre-commit install
   ```

4. 手动触发所有文件检查（可选）：

   ```bash
   pre-commit run --all-files
   ```

### 5.3 常见问题与说明

- 如需跳过单次 commit 检查，可用 `git commit --no-verify`。
- 若有大批量格式化需求，建议先手动运行 black/isort，再提交。
- pre-commit 只会检查 src/ 和 tests/ 目录下的 Python 文件。
- 钩子配置可根据团队实际需求调整。

> 建议所有开发者本地安装并启用 pre-commit，保障团队协作代码质量一致性。

## 6. 验证环境

### 6.1 基础验证

```bash
# 验证 Python 环境
python --version
pip list

# 验证项目安装
python -c "import src.markdown_spacer; print('项目导入成功')"
```

### 6.2 代码质量检查

```bash
# 代码格式检查
flake8 src/ tests/

# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 类型检查
mypy src/
```

### 6.3 测试验证

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 7. 开发工作流

### 7.1 日常开发流程

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 拉取最新代码
git pull origin develop

# 3. 创建功能分支
git checkout -b feature/功能名称

# 4. 开发代码
# ... 编写代码 ...

# 5. 运行测试
pytest

# 6. 代码质量检查
flake8 src/ tests/
black src/ tests/
isort src/ tests/

# 7. 提交代码
git add .
git commit -m "feat: 功能描述"

# 8. 推送分支
git push origin feature/功能名称
```

### 7.2 预提交检查

项目配置了 pre-commit 钩子，会在提交前自动运行：

- 代码格式化（black）
- 导入排序（isort）
- 代码检查（flake8）
- 类型检查（mypy）

## 8. 常见问题

### 8.1 环境问题

**Q: Python 版本不匹配**
A: 确保使用 Python 3.12+，可以使用 pyenv 管理 Python 版本

**Q: 虚拟环境激活失败**
A: 检查虚拟环境路径，确保使用正确的激活命令

**Q: 依赖安装失败**
A: 升级 pip，检查网络连接，尝试使用国内镜像源

### 8.2 开发问题

**Q: 测试失败**
A: 检查测试环境，确保所有依赖已安装

**Q: 代码格式检查失败**
A: 运行 `black src/ tests/` 自动格式化代码

**Q: 类型检查错误**
A: 根据 mypy 提示修复类型注解

## 9. 版本历史

| 版本 | 日期 | 变更内容 | 负责人 |
| ---- | ---- | -------- | ------ |
| v1.0 | 2025-07-22 | 初始环境搭建文档 | 刘凡 & 小克 |
| v1.1 | 2025-07-22 | 增加 pre-commit 钩子配置章节，调整文档结构 | 刘凡 & 小克 |
