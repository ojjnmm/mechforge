"""
LLM 客户端模块 - 负责所有 AI 模型 API 调用
"""

import json
import time
from pathlib import Path
from typing import List, Optional

from mechforge_core.config import get_config
from mechforge_ai.prompts import get_system_prompt


class LLMClient:
    """LLM 客户端 - 统一接口"""

    def __init__(self, model: Optional[str] = None):
        self.config = get_config()
        self._model = model
        self.conversation_history: List[dict] = []

    @property
    def provider(self) -> str:
        return self.config.get_active_provider()

    def call(self, user_input: str, context: str = "") -> str:
        """统一调用入口"""
        provider = self.provider

        if provider == "openai":
            return self.call_openai(user_input, context)
        elif provider == "anthropic":
            return self.call_anthropic(user_input, context)
        elif provider == "local":
            return self.call_local(user_input, context)
        else:
            return self.call_ollama_stream(user_input, context)

    def call_openai(self, message: str, context: str = "") -> str:
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

    def call_anthropic(self, message: str, context: str = "") -> str:
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

    def call_ollama(self, message: str, context: str = "") -> str:
        """调用 Ollama API - 非流式版本"""
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

    def call_ollama_stream(self, message: str, context: str = "") -> str:
        """调用 Ollama API - 流式版本"""
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

    def call_local(self, message: str, context: str = "") -> str:
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
        from rich.console import Console
        console = Console()
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
        messages.extend(self.conversation_history[-10:])
        messages.append({"role": "user", "content": user_content})

        # 调用模型
        output = llm.create_chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        return output["choices"][0]["message"]["content"]

    def get_current_model_name(self) -> str:
        """获取当前模型名称"""
        provider = self.provider
        provider_cfg = self.config.get_provider_config(provider)

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

        if provider == "openai":
            return provider_cfg.model

        if provider == "anthropic":
            return provider_cfg.model

        if provider == "local":
            return provider_cfg.llm_model

        return "未配置"

    def get_api_type(self) -> str:
        """获取 API 类型名称"""
        provider = self.provider
        provider_names = {
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "ollama": "Ollama",
            "local": "Local GGUF",
        }
        return provider_names.get(provider, "Ollama")
