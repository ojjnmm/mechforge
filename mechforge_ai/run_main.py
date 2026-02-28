#!/usr/bin/env python
import os
import sys

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 切换到 E 盘根目录 (Windows 路径)
try:
    os.chdir('E:\\')
except:
    pass

# 添加父目录到 sys.path
sys.path.insert(0, 'E:\\')

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

# 运行主程序
from mechforge_ai.chat.terminal import MechForgeTerminal
terminal = MechForgeTerminal()
terminal.start()
