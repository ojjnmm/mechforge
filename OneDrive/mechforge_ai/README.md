# MechForge AI

**机械设计师的本地 AI 工作台** —— 终于有一款**真正懂机械、敢说真话、能真算**的工具

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.4.0-green.svg)](https://github.com/yd5768365-hue/mechforge)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 界面预览

### AI 对话模式
![AI Chat UI](ai-chat-ui.png)

### 知识库检索模式
![Knowledge Base UI](knowledge-base-ui.png)

### CAE 工作台模式
![Work Mode UI](work-mode-ui.png)

---

## 为什么机械设计师需要 MechForge？

每天你都在和通用大模型斗智斗勇：它一会儿胡说八道安全系数，一会儿给你云端泄露图纸，跑一次有限元要等半天。

**MechForge 彻底解决这三个痛点**：

### 1. 绝对可信 —— 知识查阅模式"只搬书，不编故事"
- 纯检索 + 原文呈现，AI 绝不允许自由生成
- 查询 GB/JB 手册、零件参数、标准条款时，直接弹出原文 + 出处
- 工程师最怕的"幻觉"在这里被彻底封杀

### 2. 像老工程师一样聊天 —— AI 模式
- 不是一本会说话的手册，而是一位有 10+ 年经验的机械前辈
- 会问工况、提醒裕度、对比选型、指出加工风险
- 支持 /rag 临时调用知识库，聊天与查书无缝切换

### 3. 真正能干活 —— Work 模式 (CAE 工作台)
- 本地网格划分：Gmsh 4.15+ 集成
- 有限元求解：CalculiX 集成 (支持本地/Docker/API)
- 结果可视化：PyVista 0.47+ 支持
- 完整 CAE 工作流：加载几何 → 网格 → 边界条件 → 求解 → 后处理

---

## 安装方式

### 方式一：从 PyPI 安装 (推荐)

```bash
pip install mechforge-ai

# 安装 CAE 工作台依赖
pip install mechforge-ai[work]

# 安装所有依赖
pip install mechforge-ai[all]
```

### 方式二：从 GitHub 安装

```bash
pip install git+https://github.com/yd5768365-hue/mechforge.git
```

### 方式三：克隆后安装

```bash
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge
pip install -e ".[all]"
```

---

## 快速开始

```bash
# AI 对话模式
mechforge-ai

# 知识库检索模式
mechforge-k

# CAE 工作台 (CLI)
mechforge-work

# CAE 工作台 (TUI 交互界面)
mechforge-work --tui
```

---

## CAE 工作台命令

### CLI 模式

| 命令 | 功能 |
|------|------|
| `/mesh` | 选择几何文件并生成网格 |
| `/solve` | 执行有限元求解 |
| `/solve --api` | 使用 API 远程求解 |
| `/api <url>` | 设置/查看 API 端点 |
| `/docker start\|stop` | 管理 Docker 求解器容器 |
| `/discover` | 发现可用的求解器 |
| `/show` | 显示结果云图 |
| `/export` | 导出结果文件 |
| `/status` | 显示求解器状态 |
| `/help` | 查看帮助 |
| `/quit` | 退出程序 |

### TUI 模式

启动 TUI 界面：
```bash
mechforge-work --tui
```

交互流程：
1. 输入 `/mesh` → 文件选择弹窗
2. 选择几何文件 → Gmsh 处理进度
3. 完成后显示网格统计结果
4. 输入 `/solve` → 求解 → 显示应力云图

---

## Docker 求解器容器

### 架构

```
┌─────────────────────────────────────────┐
│           Nginx Gateway :8080           │
│         (负载均衡 + 反向代理)            │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌───────────────┐ ┌───────────────┐
│  Solver 1     │ │  Solver 2     │
│  CalculiX     │ │  CalculiX     │
│  Port: 8081   │ │  Port: 8082   │
└───────────────┘ └───────────────┘
```

### 安装 Docker 求解器

**Windows (WSL2):**
```bash
cd docker
setup-solver.bat
```

**Linux:**
```bash
cd docker
bash setup.sh
```

### 管理命令

```bash
# 启动求解器容器
mechforge-work docker start

# 停止求解器容器
mechforge-work docker stop

# 查看容器状态
mechforge-work docker status

# 发现可用求解器
mechforge-work discover
```

### API 端点

| 端点 | 说明 |
|------|------|
| `GET /status` | 服务状态 |
| `POST /solve` | 提交求解任务 |
| `GET /jobs` | 任务列表 |
| `GET /jobs/{id}` | 任务状态 |
| `GET /results/{id}` | 下载结果 |

---

## 配置

编辑 `config.yaml` 或设置环境变量：

```yaml
# AI Provider 配置
provider:
  default: "ollama"
  ollama:
    url: "http://localhost:11434"
    model: "qwen2.5:1.5b"

# 知识库配置
knowledge:
  path: "./knowledge"
```

环境变量：
- `OPENAI_API_KEY` - OpenAI API Key
- `ANTHROPIC_API_KEY` - Anthropic API Key
- `OLLAMA_URL` - Ollama 服务地址
- `OLLAMA_MODEL` - Ollama 模型名称
- `CALCULIX_API` - CalculiX API 端点

---

## 项目结构

```
mechforge-ai/
├── packages/
│   ├── mechforge_ai/      # AI 对话模式
│   ├── mechforge_core/    # 核心配置
│   ├── mechforge_knowledge/  # 知识库模式
│   ├── mechforge_theme/   # UI 主题
│   └── mechforge_work/    # CAE 工作台
│       ├── mesh_engine.py   # Gmsh 网格引擎
│       ├── solver_engine.py # CalculiX 求解引擎
│       └── viz_engine.py    # PyVista 可视化
├── docker/                  # Docker 求解器
│   ├── calculix-solver/     # CalculiX 容器
│   ├── docker-compose.yml   # 容器编排
│   └── nginx.conf           # 负载均衡
├── config.yaml              # 配置文件
├── pyproject.toml           # 项目配置
└── README.md
```

---

## 依赖版本

| 组件 | 版本 |
|------|------|
| Gmsh | 4.15.1 |
| PyVista | 0.47.1 |
| Trimesh | 4.11.2 |
| Textual | 8.0.0 |
| Rich | 14.3+ |
| CalculiX | 2.21 (Docker) |

---

## 版本历史

查看 [CHANGELOG.md](CHANGELOG.md) 获取完整版本历史。

### v0.4.0 (当前版本)
- ✅ CAE 工作台模式
- ✅ Gmsh 网格生成集成
- ✅ CalculiX 求解器集成 (本地/API/Docker)
- ✅ Docker 容器化求解器
- ✅ 交互式文件选择
- ✅ Textual TUI 界面
- ✅ PyVista 3D 可视化

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## License

MIT License - 详见 [LICENSE](LICENSE) 文件
