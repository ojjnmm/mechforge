"""
MechForge AI CLI

Entry point for the CLI.
"""

import os
import sys
from pathlib import Path

# Get script directory
script_dir = Path(__file__).parent.resolve()

# Add packages src directories to path
for pkg in ['core', 'theme', 'ai', 'knowledge']:
    src_path = script_dir / "packages" / pkg / "src"
    sys.path.insert(0, str(src_path))

# Set UTF-8 output
if sys.platform == "win32" and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    """Main entry point"""
    if "-k" in sys.argv or "--k" in sys.argv or "k" in sys.argv:
        # Knowledge mode
        from mechforge_knowledge.cli import main as knowledge_main
        knowledge_main()
    else:
        # Chat mode
        from mechforge_ai.terminal import MechForgeTerminal
        terminal = MechForgeTerminal()
        terminal.start()


if __name__ == "__main__":
    main()
