# MechForge AI 用户指南

## 目录

1. [快速开始](#快速开始)
2. [AI 对话模式](#ai-对话模式)
3. [知识库模式](#知识库模式)
4. [CAE 工作台](#cae-工作台)
5. [Docker 求解器](#docker-求解器)
6. [配置指南](#配置指南)
7. [常见问题](#常见问题)

---

## 快速开始

### 安装

```bash
# 基础安装
pip install mechforge-ai

# 安装 CAE 工作台依赖
pip install mechforge-ai[work]

# 安装所有依赖
pip install mechforge-ai[all]
```

### 启动

```bash
# AI 对话模式
mechforge-ai

# 知识库模式
mechforge-k

# CAE 工作台
mechforge-work
```

---

## AI 对话模式

### 基本命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/rag <问题>` | 查询知识库 |
| `/clear` | 清屏 |
| `/exit` | 退出 |

### 示例对话

```
用户: 请帮我分析一下这个轴承的受力情况

AI: 我来帮您分析轴承的受力情况。首先需要了解几个关键参数：
    1. 轴承类型（深沟球轴承/圆锥滚子轴承/...）
    2. 额定动载荷 C
    3. 实际载荷大小和方向
    
    您能提供这些信息吗？

用户: /rag GB/T 276 轴承额定载荷

AI: [知识库检索结果]
    根据 GB/T 276-2013《滚动轴承 深沟球轴承 外形尺寸》：
    - 额定动载荷 C 的计算公式为...
    - 额定静载荷 C0 的计算公式为...
```

---

## 知识库模式

### 特点

- **只检索不生成**：直接返回原文，避免 AI 幻觉
- **支持多种格式**：PDF、Word、Markdown、文本文件
- **语义检索**：基于向量相似度的智能检索

### 使用方法

```
# 启动知识库模式
mechforge-k

# 搜索
> 齿轮疲劳强度计算

# 结果显示原文和出处
```

### 添加知识

将文件放入 `knowledge/` 目录，系统会自动索引。

---

## CAE 工作台

### 工作流程

```
几何文件 → 网格划分 → 边界条件 → 求解 → 后处理
```

### 支持的文件格式

| 格式 | 说明 |
|------|------|
| `.step`, `.stp` | STEP AP214/AP203 |
| `.iges`, `.igs` | IGES 曲面 |
| `.stl` | STL 三角网格 |
| `.obj` | OBJ 网格 |
| `.brep` | OpenCASCADE BREP |

### 命令详解

#### `/mesh` - 生成网格

```
[MechBot] > /mesh

选择几何文件:
  1. 创建示例: Bracket
  2. 创建示例: Bearing
  3. 本地文件: part.step
  4. 取消

选择: 1

✓ 网格生成完成
  节点: 12,456
  单元: 45,678
  质量: 85.3%
```

#### `/solve` - 执行求解

```
[MechBot] > /solve

⚙ 启动 CalculiX 求解器...
  检查边界条件...
  组装刚度矩阵...
  求解线性方程组...
  计算应力应变...

✓ 求解完成
  最大位移: 0.023 mm
  最大应力: 156.7 MPa
  求解时间: 12.3s
```

#### `/solve --api` - API 远程求解

```
[MechBot] > /api http://localhost:8080
[MechBot] > /solve --api

🌐 使用 API 远程求解...
  端点: http://localhost:8080
  
✓ API 求解完成
  任务ID: a1b2c3d4
```

#### `/show` - 显示结果

```
[MechBot] > /show

📊 启动 PyVista 可视化...
(打开 3D 应力云图窗口)
```

### 边界条件设置

```python
# 在 Python 中设置
from mechforge_work import get_solver_engine, BoundaryCondition, MATERIALS

solver = get_solver_engine()

# 设置材料
solver.set_material_by_name("steel")

# 添加固定约束
solver.add_boundary_condition(BoundaryCondition(
    name="fixed_bottom",
    bc_type="fixed",
    target="face_1",
    values={"x": 0, "y": 0, "z": 0}
))

# 添加力载荷
solver.add_boundary_condition(BoundaryCondition(
    name="applied_force",
    bc_type="force",
    target="face_2",
    values={"fx": 0, "fy": -1000, "fz": 0}
))
```

---

## Docker 求解器

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

### 安装

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
# 启动
mechforge-work docker start

# 停止
mechforge-work docker stop

# 状态
mechforge-work docker status
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/status` | GET | 服务状态 |
| `/solve` | POST | 提交求解任务 |
| `/jobs` | GET | 任务列表 |
| `/jobs/{id}` | GET | 任务状态 |
| `/results/{id}` | GET | 下载结果 |

---

## 配置指南

### 配置文件 `config.yaml`

```yaml
# AI Provider 配置
provider:
  default: "ollama"
  
  ollama:
    url: "http://localhost:11434"
    model: "qwen2.5:1.5b"
  
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"

# 知识库配置
knowledge:
  path: "./knowledge"
  chunk_size: 500
  chunk_overlap: 50

# 求解器配置
solver:
  default_mode: "auto"  # auto, local, api, simulation
  api_endpoint: "http://localhost:8080"
  timeout: 600
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 |
| `OLLAMA_URL` | Ollama 服务地址 |
| `OLLAMA_MODEL` | Ollama 模型名称 |
| `CALCULIX_API` | CalculiX API 端点 |
| `MECHFORGE_LOG_LEVEL` | 日志级别 |

---

## 常见问题

### Q: Gmsh 网格生成失败？

**A:** 检查以下几点：
1. 确保 Gmsh 已安装：`pip install gmsh`
2. 检查几何文件是否有效
3. 尝试调整网格尺寸参数

### Q: CalculiX 未找到？

**A:** 三种解决方案：
1. 安装本地 CalculiX（推荐 Linux）
2. 使用 Docker 容器求解器
3. 使用模拟模式（结果不真实）

### Q: 如何添加自定义材料？

**A:** 在代码中添加：

```python
from mechforge_work.solver_engine import Material, MATERIALS

MATERIALS["custom"] = Material(
    name="CustomMaterial",
    youngs_modulus=150000,  # MPa
    poisson_ratio=0.35,
    density=6500,  # kg/m³
    yield_stress=200  # MPa
)
```

### Q: Docker 容器启动失败？

**A:** 检查：
1. Docker 是否正确安装
2. WSL2 是否启用（Windows）
3. 端口是否被占用

### Q: 如何查看详细日志？

**A:** 设置环境变量：

```bash
# Windows
set MECHFORGE_LOG_LEVEL=DEBUG

# Linux/Mac
export MECHFORGE_LOG_LEVEL=DEBUG
```

---

## 技术支持

- GitHub Issues: https://github.com/yd5768365-hue/mechforge/issues
- 文档: https://github.com/yd5768365-hue/mechforge#readme