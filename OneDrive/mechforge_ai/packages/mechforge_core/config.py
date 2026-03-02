"""
MechForge AI 配置管理

参考 opencode 项目配置模式，支持:
- YAML/JSON 配置文件
- Provider 配置（多种 AI 提供商）
- MCP 服务器配置
- 环境变量覆盖
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


def _get_app_dir() -> Path:
    """获取应用目录"""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent.parent.parent


def _get_config_dir() -> Path:
    """获取配置目录"""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local"
    else:
        base = Path.home() / ".config"
    return base / "mechforge"


def _get_default_config_file() -> Path:
    """获取默认配置文件"""
    # 优先级: ~/.mechforge/config.yaml > ./config.yaml > 内置配置
    user_config = _get_config_dir() / "config.yaml"
    if user_config.exists():
        return user_config

    local_config = Path.cwd() / "mechforge-config.yaml"
    if local_config.exists():
        return local_config

    # 内置配置
    return _get_app_dir() / "packages" / "core" / "src" / "mechforge_core" / "config.yaml"


# ==================== Provider 配置 ====================


@dataclass
class OpenAIConfig:
    """OpenAI 配置"""
    api_key: str = ""
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"

    def __post_init__(self):
        # 从环境变量读取 API Key
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY", "")


@dataclass
class AnthropicConfig:
    """Anthropic 配置"""
    api_key: str = ""
    model: str = "claude-3-haiku-20240307"
    base_url: str = "https://api.anthropic.com"

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY", "")


@dataclass
class OllamaConfig:
    """Ollama 本地模型配置"""
    url: str = "http://localhost:11434"
    model: str = "qwen2.5:1.5b"
    auto_start: bool = True


@dataclass
class LocalGGUFConfig:
    """本地 GGUF 模型配置"""
    llm_model: str = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    embedding_model: str = "bge-m3-Q8_0.gguf"
    model_dir: str = "./models"
    n_ctx: int = 2048
    n_gpu_layers: int = 0


@dataclass
class ProviderConfig:
    """AI Provider 配置"""
    default: str = "ollama"
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = field(default_factory=AnthropicConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    local: LocalGGUFConfig = field(default_factory=LocalGGUFConfig)


# ==================== 知识库配置 ====================


@dataclass
class RAGConfig:
    """RAG 配置"""
    enabled: bool = False
    top_k: int = 5
    cache_dir: str = ".cache/rag"
    embedding_model: str = "all-MiniLM-L6-v2"


@dataclass
class KnowledgeConfig:
    """知识库配置"""
    path: str = "./knowledge"
    rag: RAGConfig = field(default_factory=RAGConfig)


# ==================== MCP 配置 ====================


@dataclass
class MCPServerConfig:
    """单个 MCP 服务器配置"""
    command: str = ""
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class MCPConfig:
    """MCP 配置"""
    enabled: bool = False
    servers: dict[str, MCPServerConfig] = field(default_factory=dict)


# ==================== UI 配置 ====================


@dataclass
class UIConfig:
    """UI 配置"""
    theme: str = "dark"
    color: bool = True
    show_status: bool = True


# ==================== 日志配置 ====================


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "info"
    file: str = ".logs/mechforge.log"


# ==================== 聊天配置 ====================


@dataclass
class ChatConfig:
    """聊天配置"""
    history_limit: int = 50
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048


# ==================== 主配置类 ====================


@dataclass
class MechForgeConfig:
    """MechForge AI 主配置"""

    provider: ProviderConfig = field(default_factory=ProviderConfig)
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    chat: ChatConfig = field(default_factory=ChatConfig)

    # 内部字段
    _config_file: Path | None = field(init=False, repr=False)

    def __post_init__(self):
        self._config_file = _get_default_config_file()

    @classmethod
    def from_file(cls, config_path: str | None = None) -> "MechForgeConfig":
        """从文件加载配置"""
        if config_path:
            path = Path(config_path)
        else:
            path = _get_default_config_file()

        if not path.exists():
            return cls()

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # 解析各个配置项
            provider_data = data.get("provider", {})
            provider = ProviderConfig(
                default=provider_data.get("default", "ollama"),
                openai=OpenAIConfig(**provider_data.get("openai", {})),
                anthropic=AnthropicConfig(**provider_data.get("anthropic", {})),
                ollama=OllamaConfig(**provider_data.get("ollama", {})),
                local=LocalGGUFConfig(**provider_data.get("local", {})),
            )

            knowledge_data = data.get("knowledge", {})
            rag_data = knowledge_data.get("rag", {})
            knowledge = KnowledgeConfig(
                path=knowledge_data.get("path", "./knowledge"),
                rag=RAGConfig(**rag_data),
            )

            mcp_data = data.get("mcp", {})
            servers = {}
            for name, server_data in mcp_data.get("servers", {}).items():
                servers[name] = MCPServerConfig(**server_data)
            mcp = MCPConfig(
                enabled=mcp_data.get("enabled", False),
                servers=servers,
            )

            return cls(
                provider=provider,
                knowledge=knowledge,
                mcp=mcp,
                ui=UIConfig(**data.get("ui", {})),
                logging=LoggingConfig(**data.get("logging", {})),
                chat=ChatConfig(**data.get("chat", {})),
            )
        except Exception as e:
            print(f"警告: 加载配置文件失败: {e}, 使用默认配置")
            return cls()

    @classmethod
    def from_env(cls) -> "MechForgeConfig":
        """从环境变量加载配置（覆盖文件配置）"""
        config = cls()

        # Provider 配置环境变量覆盖
        if api_key := os.getenv("OPENAI_API_KEY"):
            config.provider.openai.api_key = api_key
        if api_key := os.getenv("ANTHROPIC_API_KEY"):
            config.provider.anthropic.api_key = api_key
        if url := os.getenv("OLLAMA_URL"):
            config.provider.ollama.url = url
        if model := os.getenv("OLLAMA_MODEL"):
            config.provider.ollama.model = model

        # 知识库目录
        if path := os.getenv("MECHFORGE_KNOWLEDGE_PATH"):
            config.knowledge.path = path

        # RAG 配置
        if enabled := os.getenv("MECHFORGE_RAG"):
            config.knowledge.rag.enabled = enabled.lower() == "true"

        # 日志级别
        if level := os.getenv("MECHFORGE_LOG_LEVEL"):
            config.logging.level = level

        return config

    def get_active_provider(self) -> str:
        """获取当前激活的 AI 提供商"""
        # 检查环境变量
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"

        # 使用配置的默认值
        return self.provider.default

    def get_provider_config(self, provider: str | None = None) -> Any:
        """获取指定 provider 的配置"""
        provider = provider or self.get_active_provider()

        if provider == "openai":
            return self.provider.openai
        elif provider == "anthropic":
            return self.provider.anthropic
        elif provider == "ollama":
            return self.provider.ollama
        elif provider == "local":
            return self.provider.local

        return self.provider.ollama

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "provider": {
                "default": self.provider.default,
                "openai": {
                    "api_key": self.provider.openai.api_key,
                    "model": self.provider.openai.model,
                    "base_url": self.provider.openai.base_url,
                },
                "anthropic": {
                    "api_key": self.provider.anthropic.api_key,
                    "model": self.provider.anthropic.model,
                    "base_url": self.provider.anthropic.base_url,
                },
                "ollama": {
                    "url": self.provider.ollama.url,
                    "model": self.provider.ollama.model,
                    "auto_start": self.provider.ollama.auto_start,
                },
                "local": {
                    "llm_model": self.provider.local.llm_model,
                    "embedding_model": self.provider.local.embedding_model,
                    "model_dir": self.provider.local.model_dir,
                    "n_ctx": self.provider.local.n_ctx,
                    "n_gpu_layers": self.provider.local.n_gpu_layers,
                },
            },
            "knowledge": {
                "path": self.knowledge.path,
                "rag": {
                    "enabled": self.knowledge.rag.enabled,
                    "top_k": self.knowledge.rag.top_k,
                    "cache_dir": self.knowledge.rag.cache_dir,
                    "embedding_model": self.knowledge.rag.embedding_model,
                },
            },
            "mcp": {
                "enabled": self.mcp.enabled,
                "servers": {
                    name: {
                        "command": server.command,
                        "args": server.args,
                        "env": server.env,
                    }
                    for name, server in self.mcp.servers.items()
                },
            },
            "ui": {
                "theme": self.ui.theme,
                "color": self.ui.color,
                "show_status": self.ui.show_status,
            },
            "logging": {
                "level": self.logging.level,
                "file": self.logging.file,
            },
            "chat": {
                "history_limit": self.chat.history_limit,
                "system_prompt": self.chat.system_prompt,
                "temperature": self.chat.temperature,
                "max_tokens": self.chat.max_tokens,
            },
        }


# ==================== 便捷函数 ====================


_default_config: MechForgeConfig | None = None


def get_config(config_path: str | None = None, force_reload: bool = False) -> MechForgeConfig:
    """获取配置（单例）"""
    global _default_config

    if _default_config is None or force_reload:
        # 先尝试从文件加载
        config = MechForgeConfig.from_file(config_path)
        # 然后用环境变量覆盖
        _default_config = config.from_env()

    return _default_config


def reload_config() -> MechForgeConfig:
    """重新加载配置"""
    return get_config(force_reload=True)


def save_config(config: MechForgeConfig, config_path: str | None = None):
    """保存配置到文件"""
    config_dir = _get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    if config_path:
        path = Path(config_path)
    else:
        path = config_dir / "config.yaml"

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            config.to_dict(),
            f,
            allow_unicode=True,
            default_flow_style=False,
        )


# ==================== 兼容旧代码 ====================


# 为保持向后兼容，提供旧的 KnowledgeConfig
class KnowledgeConfigCompat:
    """兼容旧的 KnowledgeConfig"""

    def __init__(self):
        config = get_config()
        self.knowledge_path = Path(config.knowledge.path)
        self.rag_cache_dir = Path(config.knowledge.rag.cache_dir)
        self.use_rag = config.knowledge.rag.enabled


def load_config() -> KnowledgeConfigCompat:
    """旧版加载函数兼容"""
    return KnowledgeConfigCompat()
