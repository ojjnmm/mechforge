"""
MechForge AI 终端聊天界面

机械设计专业 AI 垂直助手
"""

import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.rule import Rule
from rich.live import Live
from rich.status import Status
from rich import box

console = Console()

from ..config import get_config
from .prompts import get_system_prompt

# 趣味动画帧
_GEAR_FRAMES = ["⚙️ ", "⚙️ ", "⚙️ "]
_THINKING_FRAMES = ["[■□□□□□□□□□]", "[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]",
                    "[■■■■■□□□□□]", "[■■■■■■□□□□□]", "[■■■■■■■□□□□]", "[■■■■■■■■■□□□]",
                    "[■■■■■■■■■■□□□]", "[■■■■■■■■■■■□□]", "[■■■■■■■■■■■■□□]", "[■■■■■■■■■■■■■□]",
                    "[■■■■■■■■■■■■■■□□]", "[■■■■■■■■■■■■■□□]", "[■■■■■■■□□□□□]", "[■■■□□□□□□□□]",
                    "[■■□□□□□□□□□]", "[■□□□□□□□□□□]"]

# 有趣的欢迎语
_WELCOME_MESSAGES = [
    "机械之美，AI 来造 ~",
    "螺栓螺母已就位，等你提问~",
    "CAD/CAE 随问随答~",
    "材料力学老博士，在线答疑~",
    "有限元分析小能手，听候差遣~",
    "公差配合小专家，为你服务~",
    "机械设计好帮手，上线啦~",
]


class _AnimatedPrint:
    """动画打印工具"""

    @staticmethod
    def gear_spin(text: str = "系统初始化", duration: float = 1.0):
        """齿轮转动动画"""
        frames = ["[○○○] ", "[◐○○] ", "[◑○○] ", "[◒○○] ", "[◓○○] ",
                  "[●●○] ", "[○●○] ", "[○○●] "]
        end_time = time.time() + duration
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                print(f"\r{frame}{text}...", end="", flush=True)
                time.sleep(0.1)
        print(f"\r    {text}... ✓")

    @staticmethod
    def thinking():
        """思考动画生成器"""
        for i, frame in enumerate(_THINKING_FRAMES):
            yield frame, i == len(_THINKING_FRAMES) - 1


def typewriter_print(text: str, delay: float = 0.015):
    """逐字打印效果 - 科幻终端风格"""
    import sys
    # 清理异常的换行符（单个字符间的换行）
    import re
    text = re.sub(r'(?<=[^\n])\n(?=[^\n])', '', text)
    # 清理连续换行
    text = text.replace('\n\n', '\n')
    # 逐字打印
    for char in text:
        if char == '\n':
            sys.stdout.write('\n')
        else:
            sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# 随机选择一个欢迎语
import random
_RANDOM_WELCOME = random.choice(_WELCOME_MESSAGES)


class MechForgeTerminal:
    """MechForge AI 终端聊天界面"""

    def __init__(self, model: Optional[str] = None):
        # 加载统一配置
        self.config = get_config()

        self.running = False
        self.conversation_history: List[dict] = []
        self.command_history: List[str] = []
        self._last_history_input: str = ""  # 上一次的输入（用于去重）

        # API 配置
        self._api_type = self.config.get_active_provider()
        self._model = model or self.config.provider.ollama.model

        # RAG 模式
        self._rag_enabled = self.config.knowledge.rag.enabled
        self._knowledge_path = self._find_knowledge_path()

        # 加载对话历史
        self._load_conversation_history()

    def _find_knowledge_path(self) -> Optional[Path]:
        """查找知识库路径"""
        # 优先使用配置中的路径
        config_path = Path(self.config.knowledge.path)
        if config_path.exists() and list(config_path.glob("*.md")):
            return config_path

        # 备选搜索路径
        search_paths = [
            Path(__file__).parent.parent.parent.parent / "knowledge",
            Path.home() / "knowledge",
            Path.cwd() / "knowledge",
        ]

        for path in search_paths:
            if path.exists() and list(path.glob("*.md")):
                return path
        return None

    def _print_dashboard(self):
        """打印系统状态面板"""
        # 检测 API 类型
        api_type = self._detect_api_type()

        # 获取当前模型
        model_name = self._get_current_model()

        # 获取知识库状态
        kb_status = "未配置"
        kb_count = 0
        if self._knowledge_path:
            kb_count = len(list(self._knowledge_path.glob("*.md")))
            kb_status = f"{self._knowledge_path.name} ({kb_count} 篇)"

        # RAG 状态
        rag_status = "ON " if self._rag_enabled else "OFF"
        rag_mode = "智能" if self._rag_enabled else "基础"
        rag_color = "bold orange1" if self._rag_enabled else "red"

        # 对话数
        msg_count = len(self.conversation_history)

        # 系统时间
        now = datetime.now().strftime("%H:%M:%S")

        # 创建状态表格 - 仪表盘风格，真·控制面板
        # 使用 SIMPLE_HEAVY 样式显示垂直分割线
        # 颜色主题：工业科幻风
        # 主色调: orange1 | 强调色: cyan | 弱化色: dim | 状态值: spring_green3
        from rich.table import Table as RichTable

        grid = RichTable(
            box=box.SIMPLE_HEAVY,
            padding=(0, 1),
            show_edge=False,
            border_style="dim cyan"
        )
        grid.add_column(width=10, style="orange1")
        grid.add_column(width=18, style="spring_green3")
        grid.add_column(width=10, style="orange1")
        grid.add_column(width=18, style="spring_green3")

        grid.add_row("[bold]API", f"{api_type}", "[bold]RAG", f"[{rag_color}]{rag_status}[/{rag_color}] ({rag_mode})")
        grid.add_row("[bold]模型", f"{model_name}", "[bold]消息", f"{msg_count} 条")
        grid.add_row("[bold]知识库", f"[dim]{kb_status}[/dim]", "[bold]TopK", f"{self.config.knowledge.rag.top_k}")
        grid.add_row("[bold]版本", f"v0.3.0", "[bold]运行", f"[dim]{now}[/dim]")

        console.print(grid)

    def _get_current_model(self) -> str:
        """获取当前使用的模型名称"""
        # 使用统一配置
        provider = self.config.get_active_provider()
        provider_cfg = self.config.get_provider_config(provider)

        # Ollama - 尝试获取可用模型
        if provider == "ollama":
            try:
                import requests
                resp = requests.get(f"{self.config.provider.ollama.url}/api/tags", timeout=5)
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    if models:
                        return models[0].get("name", provider_cfg.model)
            except Exception:
                pass
            return self._model or provider_cfg.model

        # OpenAI
        if provider == "openai":
            return provider_cfg.model

        # Anthropic
        if provider == "anthropic":
            return provider_cfg.model

        # Local GGUF
        if provider == "local":
            return provider_cfg.llm_model

        return "未配置"

    def _detect_api_type(self) -> str:
        """检测当前使用的 API 类型"""
        provider = self.config.get_active_provider()
        provider_names = {
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "ollama": "Ollama",
            "local": "Local GGUF",
        }
        return provider_names.get(provider, "Ollama")

    def _print_banner(self):
        """打印横幅 - 纯净版 Logo + Rule 分隔线"""
        # 纯净版 ASCII Art Logo - MECHFORGE
        logo_lines = [
            "  [cyan]███╗   ███╗███████╗ ██████╗██╗  ██╗██████╗ ███████╗███████╗  MECHFORGE[/cyan]",
            "  [cyan]████╗ ████║██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝██╔════╝[/cyan]",
            "  [cyan]██╔████╔██║█████╗  ██║     ███████║██║  ██║█████╗  ███████╗[/cyan]",
            "  [cyan]██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██║  ██║██╔══╝  ╚════██║[/cyan]",
            "  [cyan]██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██████╔╝███████╗███████║[/cyan]",
            "  [cyan]╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝[/cyan]",
        ]
        for line in logo_lines:
            console.print(line)

        # 使用 Rich Rule 添加分隔线
        console.print(Rule("[bold cyan]MechForge System Initialized", style="cyan"), style="cyan")

        # 打印 Dashboard
        self._print_dashboard()

    def start(self):
        """启动终端"""
        self.running = True

        # 尝试加载命令历史
        self._load_command_history()

        # 启动动画
        print()
        _AnimatedPrint.gear_spin("系统启动中", 0.8)
        self._print_banner()

        # 打印命令帮助框
        help_text = Text(
            "/status /info /rag /history /clear /reload /model /exit",
            style="spring_green3"
        )
        console.print(Panel(help_text, border_style="dim", padding=(0, 1)))

        # 分隔线
        console.rule(style="dim")

        # 有趣的欢迎语
        console.print(f"  [spring_green3]{_RANDOM_WELCOME}[/spring_green3]")
        console.print(f"  [dim]对话历史:[/dim] [spring_green3]{len(self.conversation_history)} 条[/spring_green3]\n")

        # 主循环
        history_index = -1  # 命令历史索引

        while self.running:
            try:
                # 使用带历史的输入
                user_input = self._input_with_history(history_index)
                print()

                if not user_input:
                    continue

                # 更新历史索引
                if user_input != self._last_history_input:
                    self.command_history.append(user_input)
                    self._last_history_input = user_input

                history_index = -1  # 重置历史索引
                self._handle_input(user_input)

                # 保存命令历史
                self._save_command_history()

            except (EOFError, ValueError):
                break
            except KeyboardInterrupt:
                print("\n\n使用 /exit 退出")
                continue

        # 退出时保存
        self._save_conversation_history()
        print("\n再见! 期待下次相遇~\n")

    def _input_with_history(self, history_index: int = -1) -> str:
        """带命令历史的输入"""
        try:
            import readline
            # 使用 readline 的历史功能
            if history_index < 0:
                # 新输入
                return console.input("[spring_green3]⚙ ❯[/spring_green3] ").strip()
            else:
                # 导航历史
                if history_index < len(self.command_history):
                    return self.command_history[-(history_index + 1)]
                return ""
        except ImportError:
            # readline 不可用，回退到普通输入
            return console.input("[spring_green3]⚙ ❯[/spring_green3] ").strip()

    def _load_command_history(self):
        """加载命令历史"""
        try:
            import readline
            history_file = Path.home() / ".mechforge-ai" / "history"
            if history_file.exists():
                with open(history_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            readline.add_history(line)
                            self.command_history.append(line)
        except Exception:
            pass

    def _save_command_history(self):
        """保存命令历史"""
        try:
            history_file = Path.home() / ".mechforge-ai" / "history"
            history_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存最近的 100 条
            with open(history_file, "w", encoding="utf-8") as f:
                for cmd in self.command_history[-100:]:
                    f.write(f"{cmd}\n")
        except Exception:
            pass

    def _load_conversation_history(self):
        """加载对话历史"""
        try:
            import json
            conv_file = Path.home() / ".mechforge-ai" / "conversation.json"
            if conv_file.exists():
                with open(conv_file, "r", encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
        except Exception:
            pass

    def _save_conversation_history(self):
        """保存对话历史"""
        try:
            import json
            conv_file = Path.home() / ".mechforge-ai" / "conversation.json"
            conv_file.parent.mkdir(parents=True, exist_ok=True)

            # 保存最近的 50 条
            with open(conv_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _handle_rag_command(self):
        """处理 RAG 命令 - toggle 切换"""
        if not self._knowledge_path:
            print("✗ 未找到知识库")
            return

        # Toggle 切换
        self._rag_enabled = not self._rag_enabled
        if self._rag_enabled:
            print(f"✓ RAG 已启用，知识库: {self._knowledge_path}")
        else:
            print("✓ RAG 已禁用")

    def configure_model(self):
        """配置 AI 模型"""
        print("""
+================================================================+
|           MechForge AI - 模型配置                           |
+================================================================+
|  1. OpenAI (GPT-4o, GPT-4o-mini, etc.)                   |
|  2. Anthropic (Claude-3.5, Claude-3, etc.)               |
|  3. Ollama (本地模型)                                     |
|  4. 本地 GGUF 模型                                        |
|  5. 设为默认 Provider                                     |
|  6. 查看当前配置                                           |
|  7. 测试连接                                               |
|  0. 退出                                                   |
+================================================================+
""")

        choice = console.input("[spring_green3]选择 [0-7]:[/spring_green3] ").strip()

        if choice == "0":
            return
        elif choice == "3":
            self._config_ollama()
        elif choice == "4":
            self._config_local()
        elif choice == "1":
            self._config_openai()
        elif choice == "2":
            self._config_anthropic()
        elif choice == "5":
            self._set_default_provider()
        elif choice == "6":
            self._show_config()
        elif choice == "7":
            self._test_connection()

    def _config_ollama(self):
        """配置 Ollama"""
        print("\n[Ollama 本地模型配置]")
        print(f"默认地址: {self.config.provider.ollama.url}\n")

        url = console.input("[spring_green3]输入 Ollama 地址 [默认]:[/spring_green3] ").strip()
        if url:
            self.config.provider.ollama.url = url

        print("测试连接中...")
        import requests
        try:
            resp = requests.get(f"{self.config.provider.ollama.url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    self._save_config("ollama", url or self.config.provider.ollama.url)
                    print(f"\n✓ Ollama 连接成功!")
                    print(f"  可用模型: {len(models)} 个")
                    for m in models[:5]:
                        print(f"    - {m.get('name', 'unknown')}")
                else:
                    print("\n✗ 未找到任何模型，请先下载模型")
                    print("  命令: ollama pull qwen2.5:1.5b")
            else:
                print(f"\n✗ 连接失败: {resp.status_code}")
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            print("\n请确保 Ollama 已启动: ollama serve")

    def _config_local(self):
        """配置本地 GGUF 模型"""
        print("\n[本地 GGUF 模型配置]")
        cfg = self.config.provider.local

        print(f"模型目录: {cfg.model_dir}")
        print(f"LLM 模型: {cfg.llm_model}")
        print(f"嵌入模型: {cfg.embedding_model}")
        print(f"上下文长度: {cfg.n_ctx}")
        print(f"GPU 层数: {cfg.n_gpu_layers}\n")

        print("1. 修改 LLM 模型文件名")
        print("2. 修改模型目录")
        print("3. 修改上下文长度")
        print("4. 修改 GPU 层数")
        print("0. 返回\n")

        choice = console.input("[spring_green3]选择 [0-4]:[/spring_green3] ").strip()

        if choice == "1":
            model = console.input(f"[spring_green3]输入 GGUF 模型文件名 [{cfg.llm_model}]:[/spring_green3] ").strip()
            if model:
                cfg.llm_model = model
                self._save_config("local", "llm_model", model)
                print(f"\n✓ LLM 模型已设置为: {model}")
        elif choice == "2":
            model_dir = console.input(f"[spring_green3]输入模型目录 [{cfg.model_dir}]:[/spring_green3] ").strip()
            if model_dir:
                cfg.model_dir = model_dir
                self._save_config("local", "model_dir", model_dir)
                print(f"\n✓ 模型目录已设置为: {model_dir}")
        elif choice == "3":
            n_ctx = console.input(f"[spring_green3]输入上下文长度 [{cfg.n_ctx}]:[/spring_green3] ").strip()
            if n_ctx and n_ctx.isdigit():
                cfg.n_ctx = int(n_ctx)
                self._save_config("local", "n_ctx", int(n_ctx))
                print(f"\n✓ 上下文长度已设置为: {n_ctx}")
        elif choice == "4":
            n_gpu = console.input(f"[spring_green3]输入 GPU 层数 (0=CPU) [{cfg.n_gpu_layers}]:[/spring_green3] ").strip()
            if n_gpu and n_gpu.isdigit():
                cfg.n_gpu_layers = int(n_gpu)
                self._save_config("local", "n_gpu_layers", int(n_gpu))
                print(f"\n✓ GPU 层数已设置为: {n_gpu}")

    def _set_default_provider(self):
        """设置默认 Provider"""
        print("\n[设置默认 Provider]")
        print("当前默认:", self.config.provider.default)
        print("可选: openai, anthropic, ollama, local\n")

        provider = console.input("[spring_green3]输入默认 Provider [ollama]:[/spring_green3] ").strip() or "ollama"
        if provider in ["openai", "anthropic", "ollama", "local"]:
            self._save_config("default", provider)
            print(f"\n✓ 默认 Provider 已设置为: {provider}")
        else:
            print("\n✗ 无效的 Provider")

    def _config_openai(self):
        """配置 OpenAI"""
        api_key = console.input("[spring_green3]输入 OpenAI API Key:[/spring_green3] ").strip()
        if not api_key:
            print("取消")
            return

        print("测试连接中...")
        import requests
        try:
            resp = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                self._save_config("openai", api_key)
                self._api_type = "openai"
                print("\n✓ OpenAI 配置成功!")
            else:
                print(f"\n✗ 连接失败: {resp.status_code}")
        except Exception as e:
            print(f"\n✗ 错误: {e}")

    def _config_anthropic(self):
        """配置 Anthropic"""
        api_key = console.input("[spring_green3]输入 Anthropic API Key:[/spring_green3] ").strip()
        if not api_key:
            print("取消")
            return

        print("测试连接中...")
        import requests
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={"model": "claude-3-haiku-20240307", "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]},
                timeout=10,
            )
            if resp.status_code == 200:
                self._save_config("anthropic", api_key)
                self._api_type = "anthropic"
                print("\n✓ Anthropic 配置成功!")
            else:
                print(f"\n✗ 连接失败: {resp.status_code}")
        except Exception as e:
            print(f"\n✗ 错误: {e}")

    def _show_config(self):
        """显示配置"""
        print("\n当前配置:")
        cfg = self.config.provider

        # OpenAI
        if cfg.openai.api_key:
            key = cfg.openai.api_key
            print(f"  OpenAI: {key[:8]}...{key[-4:]} (模型: {cfg.openai.model})")

        # Anthropic
        if cfg.anthropic.api_key:
            key = cfg.anthropic.api_key
            print(f"  Anthropic: {key[:8]}...{key[-4:]} (模型: {cfg.anthropic.model})")

        # Ollama
        print(f"  Ollama: {cfg.ollama.url} (默认模型: {cfg.ollama.model})")

        # Local GGUF
        print(f"  Local GGUF: {cfg.local.llm_model}")

        # 默认 Provider
        print(f"\n  默认 Provider: {cfg.default}")
        print(f"  当前激活: {self.config.get_active_provider()}")
        print()

    def _test_connection(self):
        """测试连接"""
        import requests
        cfg = self.config.provider

        # OpenAI
        if cfg.openai.api_key:
            try:
                resp = requests.get(
                    f"{cfg.openai.base_url}/models",
                    headers={"Authorization": f"Bearer {cfg.openai.api_key}"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    print("✓ OpenAI 连接正常")
            except Exception as e:
                print(f"✗ OpenAI 连接错误: {e}")

        # Anthropic
        if cfg.anthropic.api_key:
            try:
                resp = requests.post(
                    f"{cfg.anthropic.base_url}/v1/messages",
                    headers={
                        "x-api-key": cfg.anthropic.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={"model": cfg.anthropic.model, "max_tokens": 10, "messages": [{"role": "user", "content": "hi"}]},
                    timeout=10,
                )
                if resp.status_code == 200:
                    print("✓ Anthropic 连接正常")
            except Exception as e:
                print(f"✗ Anthropic 连接错误: {e}")

        # Ollama
        try:
            resp = requests.get(f"{cfg.ollama.url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                print(f"✓ Ollama 连接正常 ({len(models)} 个模型)")
        except Exception as e:
            print(f"✗ Ollama 连接错误: {e}")

    def _save_config(self, provider: str, value: str, field: str = None):
        """保存配置到统一配置系统"""
        from ..config import save_config, reload_config

        if provider == "openai":
            self.config.provider.openai.api_key = value
            os.environ["OPENAI_API_KEY"] = value
        elif provider == "anthropic":
            self.config.provider.anthropic.api_key = value
            os.environ["ANTHROPIC_API_KEY"] = value
        elif provider == "ollama":
            self.config.provider.ollama.url = value
        elif provider == "default":
            self.config.provider.default = value
        elif provider == "local":
            # 保存 local 模型的不同字段
            if field == "llm_model":
                self.config.provider.local.llm_model = value
            elif field == "model_dir":
                self.config.provider.local.model_dir = value
            elif field == "n_ctx":
                self.config.provider.local.n_ctx = value
            elif field == "n_gpu_layers":
                self.config.provider.local.n_gpu_layers = value

        # 保存到文件
        save_config(self.config)
        # 重新加载
        self.config = reload_config()

    def _handle_input(self, user_input: str):
        """处理用户输入"""
        if user_input.startswith("/"):
            self._handle_command(user_input)
            return

        self.conversation_history.append({"role": "user", "content": user_input})
        self._call_api(user_input)

    def _handle_command(self, command: str):
        """处理命令"""
        cmd = command.lower()

        if cmd.startswith("/rag"):
            self._handle_rag_command()
            return

        if cmd in ["/help", "/h"]:
            help_text = Text("""
/status    查看系统状态
/info      显示会话信息
/rag       开关 RAG 知识库检索
/history   查看对话历史
/clear     清除对话历史
/reload    重新加载配置
/model     配置 AI 模型
/exit      退出
""", style="spring_green3")
            console.print(Panel(help_text, title="[bold orange1]MechForge AI - 可用命令[/bold orange1]", border_style="orange1", padding=(0, 2)))
        elif cmd == "/status":
            self._print_dashboard()
        elif cmd == "/info":
            self._show_session_info()
        elif cmd == "/history":
            self._show_conversation_history()
        elif cmd == "/reload":
            self._reload_config()
        elif cmd == "/clear":
            self.conversation_history.clear()
            print("✓ 对话历史已清除")
        elif cmd == "/model":
            self.configure_model()
        elif cmd in ["/exit", "/quit", "/q"]:
            self.running = False
        else:
            print(f"未知命令: {command}")

    def _show_session_info(self):
        """显示会话信息"""
        print("""
+================================================================+
|                    会话信息                                |
+================================================================+
""")
        print(f"  对话轮数: {len(self.conversation_history) // 2}")
        print(f"  消息数:  {len(self.conversation_history)}")
        print(f"  命令历史: {len(self.command_history)}")
        print(f"  RAG:     {'启用' if self._rag_enabled else '禁用'}")
        print(f"  Provider: {self.config.get_active_provider()}")
        print(f"  知识库:  {self._knowledge_path or '未配置'}")
        print()

    def _show_conversation_history(self):
        """显示对话历史"""
        if not self.conversation_history:
            print("对话历史为空")
            return

        print("""
+================================================================+
|                    对话历史                                |
+================================================================+
""")
        for i, msg in enumerate(self.conversation_history[-10:]):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:80]
            if role == "user":
                print(f"[你]: {content}")
            else:
                print(f"[AI]: {content}...")
            print()
        print(f"(显示最近 10 条，共 {len(self.conversation_history)} 条)\n")

    def _reload_config(self):
        """重新加载配置"""
        from ..config import reload_config
        self.config = reload_config()
        # 更新状态
        self._rag_enabled = self.config.knowledge.rag.enabled
        self._knowledge_path = self._find_knowledge_path()
        print("✓ 配置已重新加载")
        self._print_dashboard()

    def _check_rag_trigger(self, user_input: str) -> bool:
        """检查是否触发 RAG"""
        triggers = [
            "知识库", "数据库", "搜索", "查一下", "帮我查",
            "请问", "根据", "参照", "按照", "rag", "手册",
            "标准", "规范", "材料", "螺栓", "轴承",
        ]
        return any(t in user_input.lower() for t in triggers)

    def _search_rag(self, query: str) -> str:
        """RAG 搜索 - 增强版"""
        if not self._knowledge_path:
            return ""

        # 尝试使用向量搜索
        try:
            from ..knowledge.rag import search_with_chroma
            results = search_with_chroma(
                self._knowledge_path,
                query,
                top_k=self.config.knowledge.rag.top_k,
            )
            if results:
                # 显示搜索结果摘要
                print(f"   找到 {len(results)} 条相关知识:")
                for i, r in enumerate(results, 1):
                    score = r.get("score", 0)
                    # 使用简单字符避免编码问题
                    filled = int(score * 5)
                    bar = "#" * filled + "-" * (5 - filled)
                    title = r.get("title", "未知")[:28]
                    print(f"   {i}. {title:<28} [{bar}]")

                # 构建上下文
                context = "\n\n【参考知识库】\n"
                for r in results:
                    title = r.get("title", "未知")
                    content = r.get("content", "")[:500]
                    context += f"\n--- {title} ---\n{content}...\n"
                return context
        except Exception as e:
            # 回退到关键词搜索
            pass

        # 回退：关键词搜索
        try:
            from ..knowledge.lookup import search_by_keyword
            results = search_by_keyword(self._knowledge_path, query, limit=3)
            if results:
                print(f"   找到 {len(results)} 条相关知识:")
                for i, r in enumerate(results, 1):
                    score = r.get("score", 0)
                    filled = min(int(score / 20), 5)
                    bar = "#" * filled + "-" * (5 - filled)
                    title = r.get("title", "未知")[:28]
                    print(f"   {i}. {title:<28} [{bar}]")

                context = "\n\n【参考知识库】\n"
                for r in results:
                    title = r.get("title", "未知")
                    content = r.get("content_preview", "")[:500]
                    context += f"\n--- {title} ---\n{content}...\n"
                return context
        except Exception as e:
            print(f"   知识库检索失败: {e}")

        return ""

    def _call_api(self, user_input: str):
        """调用 AI API"""
        # 使用统一配置
        provider = self.config.get_active_provider()

        # 检查是否需要 RAG
        context = ""
        use_rag = self._rag_enabled or (self._knowledge_path and self._check_rag_trigger(user_input))

        if use_rag and self._knowledge_path:
            print("📚 正在检索知识库...")

            # 使用增强的 RAG 搜索
            context = self._search_rag(user_input)

        # 有趣的思考提示（根据是否使用 RAG 调整）
        if context:
            _thinking_msgs = [
                "⚙️  结合知识库思考中...",
                "📐  分析结构中...",
                "🔧  查找机械手册...",
                "📊  计算中...",
                "🧠  思考中...",
                "📚  学习ing...",
            ]
        else:
            _thinking_msgs = [
                "⚙️  齿轮转动中...",
                "📐  分析结构中...",
                "🔧  查找机械手册...",
                "📊  计算中...",
                "🧠  思考中...",
            ]
        think_msg = random.choice(_thinking_msgs)

        # 使用 Rich Status 动画
        try:
            with Status(think_msg, console=console, spinner="dots12") as status:
                if provider == "openai":
                    response = self._call_openai(user_input, context)
                elif provider == "anthropic":
                    response = self._call_anthropic(user_input, context)
                elif provider == "local":
                    response = self._call_local(user_input, context)
                else:
                    response = self._call_ollama_stream(user_input, context)

                # 流式输出 - 直接打印
                print()
                console.print(response, style="cyan")
                self.conversation_history.append({"role": "assistant", "content": response})

        except Exception as e:
            error_msg = str(e)
            # 提供友好的错误提示
            if "connection" in error_msg.lower():
                print("\n\n[错误] 无法连接到 AI 服务")
                print("请检查:")
                print("  1. 网络连接是否正常")
                print("  2. Ollama 是否已启动 (ollama serve)")
                print("  3. 或使用 /model 配置其他 AI 提供商")
            elif "timeout" in error_msg.lower():
                print("\n\n[错误] 请求超时")
                print("请尝试:")
                print("  1. 使用更小的模型")
                print("  2. 检查网络连接")
            elif "api" in error_msg.lower():
                print(f"\n\n[错误] API 调用失败: {error_msg[:50]}")
                print("请检查 API Key 是否正确，或尝试 /model 重新配置")
            else:
                print(f"\n\n[错误] {error_msg[:100]}")
                print("请尝试 /model 重新配置或检查网络连接")

    def _call_openai(self, message: str, context: str = "") -> str:
        """调用 OpenAI API"""
        import requests

        cfg = self.config.provider.openai
        user_content = message + context if context else message

        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.extend(self.conversation_history[-10:])
        messages.append({"role": "user", "content": user_content})

        resp = requests.post(
            f"{cfg.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"},
            json={"model": cfg.model, "messages": messages, "temperature": self.config.chat.temperature},
            timeout=120,
        )

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        raise Exception(f"API 错误 {resp.status_code}: {resp.text}")

    def _call_anthropic(self, message: str, context: str = "") -> str:
        """调用 Anthropic API"""
        import requests

        cfg = self.config.provider.anthropic

        history = "\n".join(f"{h['role'].title()}: {h['content']}" for h in self.conversation_history[-10:])
        user_content = message + context if context else message
        full_prompt = f"{get_system_prompt()}\n\n历史:\n{history}\n\n用户: {user_content}"

        resp = requests.post(
            f"{cfg.base_url}/v1/messages",
            headers={
                "x-api-key": cfg.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={"model": cfg.model, "max_tokens": self.config.chat.max_tokens, "messages": [{"role": "user", "content": full_prompt}]},
            timeout=120,
        )

        if resp.status_code == 200:
            return resp.json()["content"][0]["text"]
        raise Exception(f"API 错误 {resp.status_code}: {resp.text}")

    def _call_ollama(self, message: str, context: str = "") -> str:
        """调用 Ollama API"""
        import requests

        cfg = self.config.provider.ollama
        model = self._model or cfg.model

        # 获取可用模型
        try:
            resp = requests.get(f"{cfg.url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    model = models[0].get("name", model)
        except:
            pass

        user_content = message + context if context else message

        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.extend(self.conversation_history[-10:])
        messages.append({"role": "user", "content": user_content})

        resp = requests.post(
            f"{cfg.url}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=120,
        )

        if resp.status_code == 200:
            return resp.json().get("message", {}).get("content", "")
        raise Exception(f"API 错误 {resp.status_code}: {resp.text}")

    def _call_ollama_stream(self, message: str, context: str = "") -> str:
        """调用 Ollama API - 流式版本"""
        import requests
        import json

        cfg = self.config.provider.ollama
        model = self._model or cfg.model

        # 获取可用模型
        try:
            resp = requests.get(f"{cfg.url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    model = models[0].get("name", model)
        except:
            pass

        user_content = message + context if context else message

        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.extend(self.conversation_history[-10:])
        messages.append({"role": "user", "content": user_content})

        # 流式请求
        response = requests.post(
            f"{cfg.url}/api/chat",
            json={"model": model, "messages": messages, "stream": True},
            timeout=120,
            stream=True,
        )

        if response.status_code != 200:
            raise Exception(f"API 错误 {response.status_code}: {response.text}")

        # 收集流式响应
        full_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    full_content += content
                except:
                    pass
        return full_content

    def _call_local(self, message: str, context: str = "") -> str:
        """调用本地 GGUF 模型"""
        try:
            from llama_cpp import Llama
        except ImportError:
            raise Exception("请安装 llama-cpp-python: pip install llama-cpp-python")

        cfg = self.config.provider.local
        model_path = Path(cfg.model_dir) / cfg.llm_model

        if not model_path.exists():
            raise Exception(f"模型文件不存在: {model_path}")

        # 加载模型
        console.print("[spring_green3]加载本地模型中...[/spring_green3]")
        llm = Llama(
            model_path=str(model_path),
            n_ctx=cfg.n_ctx,
            n_gpu_layers=cfg.n_gpu_layers,
            verbose=False,
        )

        # 构建消息
        user_content = message + "\n\n" + context if context else message

        system_prompt = get_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        # 添加对话历史
        messages.extend(self.conversation_history[-10:])
        messages.append({"role": "user", "content": user_content})

        # 调用模型
        output = llm.create_chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        return output["choices"][0]["message"]["content"]
