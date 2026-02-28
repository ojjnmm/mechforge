"""
MechForge AI - Mechanical Engineering AI Assistant

This is a refactored version using monorepo structure.
"""

# Import from packages
from mechforge_core.config import get_config, MechForgeConfig
from mechforge_theme.components import UIRenderer
from mechforge_ai.terminal import MechForgeTerminal
from mechforge_knowledge.cli import main as knowledge_main

__version__ = "0.4.0"

__all__ = [
    "get_config",
    "MechForgeConfig",
    "UIRenderer",
    "MechForgeTerminal",
    "knowledge_main",
]
