"""提示词模块"""

from pathlib import Path

# 读取机械设计系统提示词
PROMPTS_DIR = Path(__file__).parent
MECHANICAL_PROMPT_FILE = PROMPTS_DIR / "mechanical.md"


def get_system_prompt() -> str:
    """获取系统提示词"""
    try:
        with open(MECHANICAL_PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return DEFAULT_SYSTEM_PROMPT


# 默认提示词（备用）
DEFAULT_SYSTEM_PROMPT = """你是一个专为机械设计专业打造的 AI 助手（MechForge AI）。

你的专长包括：
1. 机械设计知识
2. GB/JB 标准引用
3. 经验公式应用
4. 失败案例分析
5. 工程计算

请用中文回答用户的问题。"""


__all__ = ["get_system_prompt", "DEFAULT_SYSTEM_PROMPT"]
