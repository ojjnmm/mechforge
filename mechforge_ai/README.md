# MechForge AI

机械设计专业 AI 垂直助手

## 界面预览

### AI 对话模式

![AI Chat UI](ai-chat-ui.png)

### 知识库检索模式

![Knowledge Base UI](knowledge-base-ui.png)

## 功能特性

- 🤖 **多模型支持**: Ollama / OpenAI / Anthropic / 本地 GGUF
- 📚 **知识库检索**: 纯关键词搜索，拒绝幻觉
- 🎨 **工业科幻风 UI**: 机械控制面板风格
- ⚡ **流式输出**: 实时响应，打字机效果

## 快速开始

```bash
# 安装依赖
pip install -e .

# 启动 AI 对话模式
mechforge-ai
# 或
python run_main.py

# 启动知识库检索模式
mechforge-k
# 或
python run_knowledge.py
```

## 配置

编辑 `config.yaml` 或设置环境变量:

- `OPENAI_API_KEY` - OpenAI API Key
- `ANTHROPIC_API_KEY` - Anthropic API Key
- `OLLAMA_URL` - Ollama 服务地址
- `OLLAMA_MODEL` - Ollama 模型名称

## 版本

当前版本: v0.3.0
