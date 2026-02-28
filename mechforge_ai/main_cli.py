"""
MechForge AI CLI

简单命令行入口
"""

import os
import sys

# 设置 UTF-8 输出
if sys.platform == "win32" and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


if __name__ == "__main__":
    # 根据命令行参数判断启动模式
    # mechforge-ai - 聊天模式
    # mechforge-k - 知识库模式

    # 检查是否包含 -k 参数
    if "-k" in sys.argv or "--k" in sys.argv or "k" in sys.argv:
        # 知识库模式
        from mechforge_ai.knowledge_cli import main as knowledge_main
        knowledge_main()
    else:
        # 聊天模式
        from mechforge_ai.chat.terminal import MechForgeTerminal
        terminal = MechForgeTerminal()
        terminal.start()
