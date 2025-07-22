---
**文档标题**：协作指令集
**文档版本**：v1.0
**创建时间**：2025-07-22
**更新时间**：2025-07-22
**维护人员**：刘凡 & 小克
**文档状态**：进行中
---

# 协作指令集

## 1. 文档说明

本指令集标准化常用的协作操作流程，减少重复说明，提升协作效率。

## 2. 分支管理指令

### 2.1 开发分支创建

```bash
# 创建并切换到开发分支
git checkout -b develop
git push -u origin develop

# 创建功能分支
git checkout -b feature/功能名称
```

### 2.2 文档提交流程

```bash
# 添加文档
git add docs/路径/文档名.md

# 提交文档（遵循 commit 规范）
git commit -m "docs: 文档类型和内容描述"

# 推送到远程
git push origin 分支名
```

### 2.3 代码提交流程

```bash
# 添加代码文件
git add src/路径/文件名.py

# 提交代码（遵循 commit 规范）
git commit -m "feat: 功能描述"

# 推送到远程
git push origin 分支名
```

### 2.4 Feature 分支合并后清理

**指令**：`sync-feature-to-develop`

**适用场景**：完成 feature 分支开发并合并到 develop 后，清理本地和远程分支，准备新一轮开发。

**操作步骤**：

1. 切换到 develop 分支

   ```bash
   git checkout develop
   ```

2. 拉取 develop 分支最新代码

   ```bash
   git pull origin develop
   ```

3. 删除本地 feature 分支

   ```bash
   git branch -d feature/xxx
   ```

4. 更新远程分支缓存，清理已删除的远程分支

   ```bash
   git fetch --prune
   ```

**注意事项**：

- 合并 PR 后再删除本地分支，确保代码已同步
- `feature/xxx` 替换为实际分支名

## 3. 开发流程指令

### 3.0 新会话初始化

**指令**：`init-session`

**步骤**：

1. 读取协作指令集：`docs/standards/07-collaboration-commands.md`
2. 确认当前项目状态和分支
3. 根据任务类型切换合适身份
4. 开始具体任务执行

### 3.1 身份切换规范

**系统架构师**：技术设计、架构规划、环境搭建
**高级 Python 开发工程师**：核心算法、代码实现、性能优化  
**文档工程师**：文档编写、格式规范、内容整理
**测试工程师**：测试用例、质量保证、问题排查

### 3.2 环境搭建流程

**指令**：`setup-dev-env`

**步骤**：

1. 新建开发分支：`git checkout -b develop && git push -u origin develop`
2. 新建环境搭建分支：`git checkout -b feature/setup-development-environment`
3. 编写环境搭建文档：`docs/design/02-environment-setup.md`
4. 实现环境搭建步骤
5. 提交并推送：`git add . && git commit -m "feat: 环境搭建" && git push origin feature/setup-development-environment`
6. 创建 PR，等待合并

### 3.3 功能开发流程

**指令**：`dev-feature 功能名称`

**步骤**：

1. 从 develop 分支创建功能分支：`git checkout develop && git pull && git checkout -b feature/功能名称`
2. 编写技术设计文档（如需要）
3. 实现功能代码
4. 编写测试用例
5. 提交并推送
6. 创建 PR，等待代码审查

### 3.4 文档编写流程

**指令**：`write-doc 文档类型 文档名称`

**步骤**：

1. 确定文档类型（design/requirements/testing/user-guides）
2. 创建文档：`docs/类型/编号-文档名称.md`
3. 遵循 `docs/standards/02-content-standards.md` 格式
4. 提交文档：`git add docs/类型/编号-文档名称.md && git commit -m "docs: 添加文档名称" && git push origin 分支名`

## 4. 常用指令速查

### 4.1 Git 操作

| 指令 | 说明 | 示例 |
| ---- | ---- | ---- |
| `git status` | 查看状态 | - |
| `git log --oneline -5` | 查看最近提交 | - |
| `git branch -a` | 查看所有分支 | - |
| `git checkout 分支名` | 切换分支 | `git checkout develop` |
| `git pull origin 分支名` | 拉取远程更新 | `git pull origin develop` |

### 4.2 文档操作

| 指令 | 说明 | 示例 |
| ---- | ---- | ---- |
| `write-doc design 环境搭建` | 编写设计文档 | 创建 `docs/design/02-environment-setup.md` |
| `write-doc requirements 新功能` | 编写需求文档 | 创建 `docs/requirements/02-新功能-requirements.md` |
| `write-doc testing 测试策略` | 编写测试文档 | 创建 `docs/testing/01-test-strategy.md` |

### 4.3 开发操作

| 指令 | 说明 | 示例 |
| ---- | ---- | ---- |
| `init-session` | 新会话初始化 | 读取指令集，确认状态，切换身份 |
| `switch-role 角色名` | 身份切换 | `switch-role 系统架构师` |
| `setup-dev-env` | 环境搭建 | 完整的环境搭建流程 |
| `dev-feature 功能名称` | 功能开发 | 开发指定功能 |
| `test-feature 功能名称` | 功能测试 | 测试指定功能 |
| `sync-feature-to-develop` | Feature 分支合并后清理 | 合并 PR 后本地分支清理 |

## 5. 协作规范

### 5.1 分支命名

- **开发分支**：`develop`
- **功能分支**：`feature/功能名称`
- **修复分支**：`fix/问题描述`
- **文档分支**：`docs/文档类型`

### 5.2 提交规范

- **文档提交**：`docs: 文档类型和内容描述`
- **功能提交**：`feat: 功能描述`
- **修复提交**：`fix: 问题描述`
- **重构提交**：`refactor: 重构描述`

### 5.3 文档规范

- **遵循格式**：`docs/standards/02-content-standards.md`
- **命名规范**：`编号-文档名称.md`
- **版本管理**：每次修改更新版本号

## 6. 版本历史

| 版本 | 日期 | 变更内容 | 负责人 |
| ---- | ---- | -------- | ------ |
| v1.0 | 2025-07-22 | 初始协作指令集 | 刘凡 & 小克 |
