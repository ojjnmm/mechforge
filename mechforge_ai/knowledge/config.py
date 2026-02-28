"""
MechForge AI 知识库配置管理

支持 YAML 配置文件，位于 ~/.mechforge-ai/config.yaml

兼容新版 config.py 配置系统
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# 设置 UTF-8 输出（仅在需要时设置一次）
if sys.platform == "win32" and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        # 检查是否已经被包装
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass  # 忽略编码设置错误


def _get_app_dir() -> Path:
    """获取应用目录"""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent.parent


def _get_default_config_dir() -> Path:
    """获取默认配置目录"""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local"
    else:
        base = Path.home() / ".config"

    return base / "mechforge-ai"


@dataclass
class KnowledgeConfig:
    """知识库配置"""

    # 知识库目录
    knowledge_path: Path = field(default_factory=lambda: _get_default_config_dir().parent / "knowledge")

    # LLM 模型
    llm_model: str = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    embedding_model: str = "bge-m3-Q8_0.gguf"

    # 模型设置
    use_local: bool = True
    n_ctx: int = 2048
    n_gpu_layers: int = 0

    # RAG 设置
    use_rag: bool = True
    rag_top_k: int = 5
    rag_cache_dir: Path = field(default_factory=lambda: _get_default_config_dir() / "cache")

    # 内部字段
    config_file: Path = field(init=False, repr=False)

    def __post_init__(self):
        # 设置配置文件路径
        self.config_file = _get_default_config_dir() / "config.yaml"

        # 确保知识库目录是 Path 对象
        if isinstance(self.knowledge_path, str):
            self.knowledge_path = Path(self.knowledge_path)

        if isinstance(self.rag_cache_dir, str):
            self.rag_cache_dir = Path(self.rag_cache_dir)

    @property
    def llm_model_path(self) -> Optional[Path]:
        """获取 LLM 模型完整路径"""
        # 优先从当前目录查找
        model_dir = _get_app_dir()

        # 尝试多个位置
        search_paths = [
            model_dir / self.llm_model,
            Path.home() / "models" / self.llm_model,
            Path.cwd() / self.llm_model,
        ]

        for path in search_paths:
            if path.exists():
                return path

        return None

    @property
    def embedding_model_path(self) -> Optional[Path]:
        """获取嵌入模型完整路径"""
        model_dir = _get_app_dir()

        search_paths = [
            model_dir / self.embedding_model,
            Path.home() / "models" / self.embedding_model,
            Path.cwd() / self.embedding_model,
        ]

        for path in search_paths:
            if path.exists():
                return path

        return None

    @classmethod
    def from_file(cls, config_path: str) -> "KnowledgeConfig":
        """从 YAML 文件加载配置"""
        import yaml

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(
            knowledge_path=Path(data.get("knowledge_path", "")),
            llm_model=data.get("llm_model", "qwen2.5-1.5b-instruct-q4_k_m.gguf"),
            embedding_model=data.get("embedding_model", "bge-m3-Q8_0.gguf"),
            use_local=data.get("use_local", True),
            n_ctx=data.get("n_ctx", 2048),
            n_gpu_layers=data.get("n_gpu_layers", 0),
            use_rag=data.get("use_rag", True),
            rag_top_k=data.get("rag_top_k", 5),
            rag_cache_dir=Path(data.get("rag_cache_dir", "")),
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "knowledge_path": str(self.knowledge_path),
            "llm_model": self.llm_model,
            "embedding_model": self.embedding_model,
            "use_local": self.use_local,
            "n_ctx": self.n_ctx,
            "n_gpu_layers": self.n_gpu_layers,
            "use_rag": self.use_rag,
            "rag_top_k": self.rag_top_k,
            "rag_cache_dir": str(self.rag_cache_dir),
        }


def get_default_config() -> KnowledgeConfig:
    """获取默认配置"""
    # 尝试从新配置系统加载
    try:
        from .config import get_config

        cfg = get_config()
        return KnowledgeConfig(
            knowledge_path=Path(cfg.knowledge.path),
            use_rag=cfg.knowledge.rag.enabled,
            rag_top_k=cfg.knowledge.rag.top_k,
        )
    except Exception:
        pass

    # 默认知识库指向 cae-cli 的 knowledge 目录
    default_knowledge = Path(__file__).parent.parent.parent.parent / "knowledge"

    # 如果 cae-cli knowledge 不存在，使用默认
    if not default_knowledge.exists():
        default_knowledge = _get_default_config_dir().parent / "knowledge"

    return KnowledgeConfig(
        knowledge_path=default_knowledge,
    )


def load_config(config_path: Optional[Path] = None) -> KnowledgeConfig:
    """加载配置"""
    if config_path is None:
        config_path = _get_default_config_dir() / "config.yaml"

    if config_path.exists():
        return KnowledgeConfig.from_file(str(config_path))

    return get_default_config()


def save_config(config: KnowledgeConfig):
    """保存配置"""
    import yaml

    config_dir = _get_default_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "config.yaml"

    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(
            config.to_dict(),
            f,
            allow_unicode=True,
            default_flow_style=False,
        )
