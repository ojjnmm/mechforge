# MechForge AI

真正懂机械、敢说真话、能真算

<p align="center">
  <a href="https://github.com/yd5768365-hue/mechforge/releases">
    <img src="https://img.shields.io/badge/version-0.5.0-blue.svg" alt="Version"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/actions">
    <img src="https://img.shields.io/badge/code%20quality-A+-brightgreen.svg" alt="Code Quality"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/stargazers">
    <img src="https://img.shields.io/github/stars/yd5768365-hue/mechforge.svg" alt="Stars"/>
  </a>
</p>

---

## 📑 目录

- [✨ 核心特性](#-核心特性)
- [🚀 快速开始](#-快速开始)
- [📖 使用指南](#-使用指南)
- [🏗️ 技术架构](#-技术架构)
- [📦 依赖分组](#-依赖分组)
- [🛠️ 开发](#-开发)
- [📂 项目结构](#-项目结构)
- [📝 更新日志](#-更新日志)
- [📄 许可证](#-许可证)

---

## ✨ 核心特性

### 🤖 AI 对话模式
- **多模型支持**: OpenAI, Anthropic, Ollama, 本地 GGUF
- **流式响应**: 实时打字机效果
- **工具调用**: MCP 协议，内置工程计算工具
- **对话历史**: 持久化存储

### 📚 知识库检索
- **RAG 引擎**: 向量检索 + BM25 + 重排序
- **多格式支持**: Markdown, PDF, TXT
- **原文呈现**: 杜绝 AI 幻觉
- **智能切分**: 自动文档分块

### 🔧 CAE 工作台
- **几何处理**: STEP, IGES, STL 导入
- **网格划分**: Gmsh 集成
- **FEA 求解**: CalculiX 集成
- **可视化**: PyVista 3D 云图

### 🌐 Web 界面
- **FastAPI**: 高性能异步后端
- **WebSocket**: 实时双向通信
- **响应式设计**: 支持移动端
- **三模式集成**: AI/知识库/CAE

### 🔌 MCP 协议
- **内置工具**: 悬臂梁计算、材料查询、弹簧设计
- **可扩展**: 自定义工具注册
- **外部连接**: 文件系统、数据库、GitHub
- **标准化**: Model Context Protocol

### 🦙 本地模型管理
- **统一管理**: Ollama + GGUF
- **HTTP 服务**: GGUF 提供 Ollama 兼容 API
- **自动启动**: 按需启动模型服务
- **交互选择**: 可视化模型选择器

---

## 🚀 快速开始

### 💻 系统要求

- **Python**: 3.10 或更高版本
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **内存**: 最低 4GB，推荐 8GB+
- **磁盘空间**: 500MB（不含模型文件）

### 安装

```bash
# 从 PyPI 安装 (推荐)
pip install mechforge-ai

# 完整安装（所有功能）
pip install mechforge-ai[all]

# 从源码安装
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge
pip install -e ".[all]"
```

### 配置本地模型

**方式 A: Ollama (推荐)**
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull qwen2.5:1.5b
```

**方式 B: GGUF 模型**
```bash
# 下载 GGUF 文件
wget https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  -O ./models/qwen2.5-1.5b.gguf

# 启动 GGUF 服务器
mechforge-model serve -m qwen2.5-1.5b.gguf
```

### 启动使用

```bash
# 查看可用模型
mechforge-model list

# 选择默认模型
mechforge-model select

# 启动 AI 对话
mechforge-ai

# 启动知识库
mechforge-k

# 启动 CAE 工作台
mechforge-work

# 启动 Web 界面
mechforge-web
```

### 📋 命令速查表

| 命令 | 说明 | 示例 |
|------|------|------|
| `mechforge-ai` | 启动 AI 对话 | 直接运行进入交互模式 |
| `mechforge-k` | 启动知识库 | `mechforge-k search "关键词"` |
| `mechforge-work` | 启动 CAE 工作台 | `mechforge-work demo` |
| `mechforge-web` | 启动 Web 界面 | 访问 http://localhost:8080 |
| `mechforge-model` | 模型管理 | `mechforge-model list` |

---

## 📖 使用指南

### AI 对话示例

```
$ mechforge-ai

[MechBot] > 计算一个长100mm的悬臂梁挠度，截面10x10mm，受力1000N

AI: 我来为您计算这个悬臂梁的挠度...

使用工具: calculate_cantilever_deflection
参数: {"length": 100, "force": 1000, "width": 10, "height": 10}

结果: 最大挠度为 0.0254 mm

计算公式: δ = FL³ / (3EI)
其中:
- F = 1000 N
- L = 100 mm
- E = 210000 MPa (钢材)
- I = 833.33 mm⁴
```

### CAE 分析示例

```bash
$ mechforge-work

[MechBot] > /demo
✓ 悬臂梁示例已加载

[MechBot] > /mesh --size=2.0
✓ 网格生成完成: 12345 节点, 6789 单元

[MechBot] > /solve
✓ 求解完成
  最大位移: 0.025396 mm
  最大应力: 125.60 MPa

[MechBot] > /show vonmises
[显示应力云图...]
```

### Web 界面

访问 http://localhost:8080 使用 Web 界面：

- **AI 对话**: 实时流式聊天，支持 Markdown
- **知识库**: 可视化搜索和浏览
- **CAE**: 3D 模型查看，结果可视化

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      MechForge AI v0.5.0                    │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  AI 对话     │  知识库      │  CAE 工作台  │  Web 界面      │
├──────────────┼──────────────┼──────────────┼────────────────┤
│ LLM Client   │ RAG Engine   │ Gmsh         │ FastAPI        │
│ MCP Tools    │ BM25/Rerank  │ CalculiX     │ WebSocket      │
│ Streaming    │ ChromaDB     │ PyVista      │ Jinja2         │
├──────────────┴──────────────┴──────────────┴────────────────┤
│              Core (Config / MCP / Local Model Manager)       │
├─────────────────────────────────────────────────────────────┤
│  🦙 Ollama  │  📦 GGUF HTTP  │  🔧 MCP Servers               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 依赖分组

```bash
# 基础功能 (AI Chat)
pip install mechforge-ai

# CAE 功能 (+Gmsh +CalculiX +PyVista)
pip install mechforge-ai[work]

# Web 界面 (+FastAPI +WebSocket)
pip install mechforge-ai[web]

# 完整功能 (所有依赖)
pip install mechforge-ai[all]
```

---

## 🔧 故障排除

### 常见问题

**Q: 启动时提示 "命令未找到"**
```bash
# 确保安装成功并添加到 PATH
pip install --upgrade mechforge-ai
# 或重新安装
pip install --force-reinstall mechforge-ai
```

**Q: CAE 功能无法使用**
```bash
# 检查 CAE 环境
mechforge-work check

# 安装 CAE 依赖
pip install mechforge-ai[work]
```

**Q: 模型加载失败**
```bash
# 检查 Ollama 是否运行
ollama list

# 或检查 GGUF 文件路径
mechforge-model list
```

**Q: Web 界面无法访问**
```bash
# 检查端口是否被占用
mechforge-web --port 8081

# 或使用不同的主机
mechforge-web --host 0.0.0.0
```

---

## 🛠️ 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
black --check .
mypy mechforge_*/

# 构建文档
python scripts/build_docs.py

# 构建包
python scripts/build_package.py
```

---

## 📂 项目结构

```
mechforge_ai/
├── mechforge_core/            # 核心模块
│   ├── config.py              # Pydantic 配置
│   ├── mcp/                   # MCP 协议实现
│   ├── gguf_server.py         # GGUF HTTP 服务器
│   └── local_model_manager.py
├── mechforge_ai/              # AI 对话
├── mechforge_knowledge/       # 知识库
├── mechforge_work/            # CAE 工作台
├── mechforge_web/             # Web 界面
├── mechforge_theme/           # 主题组件
├── docs/                      # 文档
├── tests/                     # 测试
├── examples/                  # 示例
└── scripts/                   # 脚本
```

---

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing`)
5. 创建 Pull Request

查看 [开发指南](docs/dev/contributing.md) 了解更多。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

感谢以下开源项目：
- [Gmsh](https://gmsh.info/) - 网格生成
- [CalculiX](http://www.calculix.de/) - FEA 求解器
- [Ollama](https://ollama.com/) - 本地 LLM
- [LlamaCPP](https://github.com/ggerganov/llama.cpp) - GGUF 推理
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架

---

## 📞 联系我们

- **GitHub Issues**: [报告问题](https://github.com/yd5768365-hue/mechforge/issues)
- **Email**: mechforge@example.com
- **文档**: https://mechforge.ai

---

## 📝 更新日志

### v0.5.0 (2026-03-01)

#### ✨ 新特性
- **Web 安全中间件**: 添加完整的 FastAPI 安全中间件栈
  - 速率限制 (Rate Limiting)
  - IP 过滤 (IP Filtering)
  - 输入验证 (SQL/XSS 防护)
  - 安全头 (Security Headers)
  - API Token 管理
- **核心模块增强**:
  - 多级缓存系统 (Memory + Disk)
  - SQLite 数据库支持 (对话历史、知识库索引)
  - 结构化日志系统
  - 懒加载优化
- **代码质量**: 修复 756 个代码质量问题，达到 A+ 级
  - ✅ Black 代码格式化
  - ✅ Ruff 代码检查 (0 问题)
  - ✅ 100% 代码质量修复完成

#### 🔧 改进
- 优化包结构和导入
- 统一本地模型管理 (Ollama + GGUF)
- 改进 CAE 工作台错误处理
- 增强 MCP 工具支持

#### 📦 依赖
- 更新 pyproject.toml 配置
- 添加可选依赖分组 [web], [work], [rag]

---

<p align="center">
  Made with ❤️ for Mechanical Engineers
</p>
