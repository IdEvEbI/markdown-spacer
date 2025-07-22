---
**文档标题**：项目文档目录
**文档版本**：v1.1
**创建时间**：2025-07-22
**更新时间**：2025-07-22
**维护人员**：刘凡 & 小克
**文档状态**：已完成
---

# 项目文档目录

## 1. 文档体系概述

本项目采用按文档类型分目录的策略，使用数字前缀的文档命名规范，确保文档结构清晰、易于维护和扩展。

## 2. 文档导航

### 2.1 项目文档结构规范

- **[01-documentation-standards.md](01-documentation-standards.md)** - 项目文档结构规范
  - 文档命名规范
  - 目录结构约定
  - 文档维护规范

### 2.2 规范文档目录（standards/）

- **[01-workflow-guide.md](standards/01-workflow-guide.md)** - 协作工作流程
  - 开发工作习惯
  - 任务管理方式
  - AI 协作偏好
  - 代码管理方式

- **[02-content-standards.md](standards/02-content-standards.md)** - 文档内容规范
  - 文档头部信息格式
  - 文档结构规范（总分总结构）
  - 文档格式规范（中英文空格、代码段语言等）
  - 质量检查清单

### 2.3 需求文档目录（requirements/）

- **[01-markdown-spacer-requirements.md](requirements/01-markdown-spacer-requirements.md)** - markdown-spacer 产品需求文档
  - 项目概述
  - 功能需求
  - 技术需求
  - 项目约束

### 2.4 设计文档目录（design/）

- **[01-technical-design.md](design/01-technical-design.md)** - 技术架构设计
- **[02-algorithm-design.md](design/02-algorithm-design.md)** - 核心算法设计
- **[03-api-design.md](design/03-api-design.md)** - 接口设计文档

### 2.5 测试文档目录（testing/）

- **[01-test-strategy.md](testing/01-test-strategy.md)** - 测试策略文档
- **[02-unit-test-plan.md](testing/02-unit-test-plan.md)** - 单元测试计划
- **[03-integration-test-plan.md](testing/03-integration-test-plan.md)** - 集成测试计划

### 2.6 用户文档目录（user-guides/）

- **[01-user-guide.md](user-guides/01-user-guide.md)** - 用户使用指南
- **[02-installation-guide.md](user-guides/02-installation-guide.md)** - 安装部署指南
- **[03-api-reference.md](user-guides/03-api-reference.md)** - API 参考文档

### 2.7 项目管理目录（project/）

- **[01-todo-list.md](project/01-todo-list.md)** - 项目进度跟踪
- **[02-release-notes.md](project/02-release-notes.md)** - 版本发布说明
- **[03-changelog.md](project/03-changelog.md)** - 变更日志

### 2.8 会话记录目录（sessions/）

- **[sessions/](sessions/)** - 会话记录目录
  - [session-2025-07-20.md](sessions/session-2025-07-20.md) - 2025-07-20 会话记录
  - [session-2025-07-22.md](sessions/session-2025-07-22.md) - 2025-07-22 会话记录

## 3. 目录结构说明

```ini
docs/
├── 01-documentation-standards.md  # 项目文档结构规范
├── standards/              # 规范文档目录
│   ├── 01-workflow-guide.md
│   └── 02-content-standards.md
├── requirements/           # 需求文档目录
│   └── 01-markdown-spacer-requirements.md
├── design/                # 设计文档目录
│   ├── 01-technical-design.md
│   ├── 02-algorithm-design.md
│   └── 03-api-design.md
├── testing/               # 测试文档目录
│   ├── 01-test-strategy.md
│   ├── 02-unit-test-plan.md
│   └── 03-integration-test-plan.md
├── user-guides/           # 用户文档目录
│   ├── 01-user-guide.md
│   ├── 02-installation-guide.md
│   └── 03-api-reference.md
├── project/               # 项目管理目录
│   ├── 01-todo-list.md
│   ├── 02-release-notes.md
│   └── 03-changelog.md
├── sessions/              # 会话记录目录
│   ├── session-2025-07-20.md
│   ├── session-2025-07-22.md
│   └── README.md
└── README.md              # 文档目录导航（本文档）
```

## 4. 文档阅读建议

### 4.1 新项目成员

1. 先阅读 **[01-documentation-standards.md](01-documentation-standards.md)** 了解项目文档结构
2. 阅读 **[standards/01-workflow-guide.md](standards/01-workflow-guide.md)** 了解协作方式
3. 阅读 **[standards/02-content-standards.md](standards/02-content-standards.md)** 了解文档格式规范
4. 阅读 **[requirements/01-markdown-spacer-requirements.md](requirements/01-markdown-spacer-requirements.md)** 了解项目需求
5. 查看 **[project/01-todo-list.md](project/01-todo-list.md)** 了解当前进度

### 4.2 开发阶段

1. 查看 **[design/01-technical-design.md](design/01-technical-design.md)** 了解技术架构
2. 参考 **[testing/01-test-strategy.md](testing/01-test-strategy.md)** 进行测试开发
3. 更新 **[project/01-todo-list.md](project/01-todo-list.md)** 跟踪进度

### 4.3 使用阶段

1. 阅读 **[user-guides/01-user-guide.md](user-guides/01-user-guide.md)** 了解使用方法
2. 参考 **[user-guides/03-api-reference.md](user-guides/03-api-reference.md)** 了解 API 接口
3. 查看 **[project/02-release-notes.md](project/02-release-notes.md)** 了解版本更新

## 5. 文档维护

### 5.1 更新原则

- 遵循 **[01-documentation-standards.md](01-documentation-standards.md)** 中的规范
- 遵循 **[standards/02-content-standards.md](standards/02-content-standards.md)** 中的格式规范
- 及时更新文档版本和状态
- 保持文档间的链接正确

### 5.2 贡献指南

- 新文档按数字前缀规范命名
- 将文档放在对应的功能目录下
- 遵循文档内容规范
- 及时更新本文档的导航链接
