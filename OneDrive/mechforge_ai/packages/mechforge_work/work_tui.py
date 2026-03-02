#!/usr/bin/env python
"""
MechForge Work TUI - 可交互式 CAE 工作台

交互流程：
1. /mesh → 文件选择弹窗 → 选择文件
2. 弹窗消失 → 显示 Gmsh 处理进度
3. 完成 → 结果显示弹窗
"""

import asyncio
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Input, ProgressBar, Static


class FileSelectModal(ModalScreen):
    """文件选择弹窗"""

    CSS = """
    FileSelectModal { align: center middle; }
    .modal-box {
        width: 60; height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    .title { text-align: center; text-style: bold; color: $primary; padding: 1; }
    .file-list { height: 10; border: solid $primary; margin: 1; }
    .file-item { padding: 0 1; }
    .file-item.selected { background: $primary; color: $background; }
    .btn-row { align: center middle; }
    """

    BINDINGS = [("escape", "cancel", "取消"), ("enter", "select", "选择"),
                ("up", "up", "上"), ("down", "down", "下")]

    selected = reactive(0)

    def __init__(self):
        super().__init__()
        self.files = [
            Path("✨ 创建示例模型 (支架)"),
            Path("✨ 创建示例模型 (轴承座)"),
            Path("✨ 创建示例模型 (连杆)"),
        ]
        # 扫描当前目录
        for f in Path.cwd().glob("*"):
            if f.suffix.lower() in ['.step', '.stp', '.stl', '.iges', '.obj']:
                self.files.append(f)

    def compose(self) -> ComposeResult:
        with Container(classes="modal-box"):
            yield Static("📁 选择几何文件", classes="title")
            with VerticalScroll(classes="file-list"):
                for i, f in enumerate(self.files):
                    item = Static(f"  {f.name}", classes=f"file-item{' selected' if i==0 else ''}")
                    item.id = f"f{i}"
                    yield item
            with Horizontal(classes="btn-row"):
                yield Button("✓ 选择", id="ok", variant="primary")
                yield Button("✗ 取消", id="cancel", variant="error")

    def _refresh(self):
        for i, item in enumerate(self.query(".file-item")):
            item.set_class(i == self.selected, "selected")

    def action_up(self): self.selected = max(0, self.selected - 1); self._refresh()
    def action_down(self): self.selected = min(len(self.files)-1, self.selected + 1); self._refresh()
    def action_cancel(self): self.dismiss(None)
    def action_select(self): self._confirm()

    def _confirm(self):
        if 0 <= self.selected < len(self.files):
            self.dismiss(self.files[self.selected])

    @on(Button.Pressed, "#ok")
    def on_ok(self): self._confirm()
    @on(Button.Pressed, "#cancel")
    def on_cancel(self): self.dismiss(None)


class ProgressScreen(Screen):
    """处理进度全屏"""

    CSS = """
    ProgressScreen { align: center middle; background: $surface; }
    .prog-box {
        width: 65; height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }
    .title { text-align: center; text-style: bold; color: $primary; padding: 1; }
    .msg { text-align: center; color: $text-muted; padding: 1; }
    .steps { margin: 1; padding: 1; }
    .step { padding: 0 1; }
    .step.done { color: $success; }
    .step.current { color: $warning; text-style: bold; }
    .step.pending { color: $text-muted; }
    """

    def __init__(self, title: str, steps: list):
        super().__init__()
        self.title_text = title
        self.steps = steps

    def compose(self) -> ComposeResult:
        with Container(classes="prog-box"):
            yield Static(f"⚙ {self.title_text}", classes="title")
            yield Static("", id="msg", classes="msg")
            yield ProgressBar(total=100, show_percentage=True)
            with Vertical(classes="steps"):
                for i, s in enumerate(self.steps):
                    yield Static(f"  ○ {s}", classes=f"step{' current' if i==0 else ' pending'}", id=f"s{i}")

    def update(self, step: int, progress: float, message: str = ""):
        for i, item in enumerate(self.query(".step")):
            item.remove_class("done", "current", "pending")
            if i < step:
                item.add_class("done")
                item.update(f"  ✓ {self.steps[i]}")
            elif i == step:
                item.add_class("current")
                item.update(f"  ◉ {self.steps[i]}")
            else:
                item.add_class("pending")
        self.query_one(ProgressBar).update(progress=int(progress * 100))
        self.query_one("#msg", Static).update(message)


class ResultModal(ModalScreen):
    """结果显示弹窗"""

    CSS = """
    ResultModal { align: center middle; }
    .result-box {
        width: 65; height: auto;
        border: thick $success;
        background: $surface;
        padding: 1 2;
    }
    .title { text-align: center; text-style: bold; color: $success; padding: 1; }
    .section { border: solid $primary; margin: 1; padding: 1; }
    .section-title { color: $primary; text-style: bold; margin-bottom: 1; }
    .cloud { border: solid $primary; margin: 1; padding: 1; background: $panel; }
    """

    BINDINGS = [("escape", "close", "关闭"), ("enter", "close", "确定")]

    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        with Container(classes="result-box"):
            yield Static(f"✓ {self.data.get('type', '').upper()} 完成", classes="title")

            if self.data.get('type') == 'mesh':
                yield from self._mesh_content()
            else:
                yield from self._solve_content()

            with Horizontal(classes="btn-row"):
                yield Button("✓ 确定", id="ok", variant="primary")

    def _mesh_content(self):
        with Container(classes="section"):
            yield Static("📊 网格统计", classes="section-title")
            yield Static(f"  节点: [green]{self.data.get('nodes', 0):,}[/]")
            yield Static(f"  单元: [green]{self.data.get('elements', 0):,}[/]")
            yield Static(f"  类型: {self.data.get('mesh_type', 'tet')}")
            yield Static(f"  质量: {self.data.get('quality', 0):.1%}")

    def _solve_content(self):
        with Container(classes="section"):
            yield Static("📊 求解结果", classes="section-title")
            yield Static(f"  类型: {self.data.get('solve_type', 'static')}")
            yield Static(f"  最大位移: [green]{self.data.get('max_disp', 0):.4f} mm[/]")
            yield Static(f"  最大应力: [yellow]{self.data.get('max_stress', 0):.2f} MPa[/]")

        with Container(classes="cloud"):
            yield Static("🌡️ Von Mises 应力云图", classes="section-title")
            yield Static(self._cloud())

    def _cloud(self):
        return """    ┌─────────────────────────────┐
    │  [dim]···[/][cyan]▓▓[green]██████[yellow]███████[red]███[dim]···[/]  │
    │ [dim]··[/][cyan]▓▓▓[green]████████[yellow]█████████[red]████[cyan]▓[dim]··[/] │
    │[dim]··[/][cyan]▓▓[green]███████████[yellow]███████████[red]████[dim]··[/]│
    │  [green]███████████████[yellow]███████████████[red]███[dim]··[/]  │
    │   [green]████████████████[yellow]████████████████[red]██[dim]···[/]   │
    │    [cyan]▓▓[green]████████████████[yellow]█████████████[red]██[cyan]▓[dim]····[/]     │
    └─────────────────────────────┘
  [red]最大: {:.1f}[/]  [blue]最小: {:.1f}[/] MPa""".format(self.data.get('max_stress', 100), self.data.get('max_stress', 100) * 0.1)

    def action_close(self): self.dismiss(True)
    @on(Button.Pressed, "#ok")
    def on_ok(self): self.dismiss(True)


class MainScreen(Screen):
    """主界面"""

    CSS = """
    .banner { text-align: center; padding: 1; background: $primary 10%; }
    .robot { color: $error; }
    .status { dock: top; height: 1; background: $primary; color: $background; padding: 0 2; }
    .cmd-bar { dock: bottom; height: 3; background: $surface; padding: 1; }
    .main { padding: 1; }
    """

    def compose(self) -> ComposeResult:
        with Container(classes="status"):
            yield Static("MechForge Work | CAE 工作台 | 就绪", id="status")

        with Container(classes="main"):
            with Center():
                yield Static("""
[bold red]    ╔═╦═╗
    ╠╣o o╠╣
    ╚╡▄▄▄╞╝
     ╔╩═══╩╗
     ║ CAE ║╾
     ╚╦═══╦╝
     ╔╩╗ ╔╩╗
     ╚═╝ ╚═╝[/]
""", classes="robot")
            with Center():
                yield Static("""
[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]
  [bold]MechForge Work CAE 工作台[/]
  Gmsh 4.15.1 | PyVista 0.47.1
[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]

  [cyan]/mesh[/]  生成网格 (选择文件)
  [cyan]/solve[/] 求解模型
  [cyan]/help[/]  显示帮助
  [cyan]/quit[/]  退出程序
""")

        with Container(classes="cmd-bar"):
            yield Input(placeholder="输入命令...", id="cmd")


class WorkTUI(App):
    """主应用"""

    SCREENS = {"main": MainScreen}

    def on_mount(self):
        self.push_screen("main")
        self.mesh_data = {}

    @on(Input.Submitted)
    async def on_cmd(self, event: Input.Submitted):
        cmd = event.value.strip().lower()
        event.value = ""
        if cmd in ["/mesh", "/m"]: await self.do_mesh()
        elif cmd in ["/solve", "/s"]: await self.do_solve()
        elif cmd in ["/help", "/h"]: self.update_status("命令: /mesh /solve /help /quit")
        elif cmd in ["/quit", "/q"]: self.exit()

    def update_status(self, msg: str):
        self.query_one("#status", Static).update(msg)

    async def do_mesh(self):
        # 1. 文件选择弹窗
        result = await self.push_screen_wait(FileSelectModal())
        if result is None:
            self.update_status("已取消")
            return

        # 2. 进度屏幕
        prog = ProgressScreen("网格生成", ["加载几何", "清理模型", "面网格", "体网格", "优化", "完成"])
        self.push_screen(prog)

        # 3. 模拟 Gmsh 处理
        try:
            steps = [(0, 0.1, f"加载 {result.name}..."), (1, 0.25, "分析拓扑..."),
                     (2, 0.45, "生成面网格..."), (3, 0.7, "生成体网格..."), (4, 0.9, "优化...")]
            for s, p, m in steps:
                prog.update(s, p, m)
                await asyncio.sleep(0.3 + random.random() * 0.2)

            nodes = random.randint(10000, 20000)
            elements = random.randint(50000, 100000)
            prog.update(5, 1.0, "完成!")
            await asyncio.sleep(0.2)

            self.mesh_data = {"type": "mesh", "nodes": nodes, "elements": elements,
                              "mesh_type": "tet", "quality": random.uniform(0.75, 0.95)}

            self.pop_screen()  # 关闭进度
            await self.push_screen_wait(ResultModal(self.mesh_data))  # 结果弹窗
            self.update_status(f"网格完成 | 节点: {nodes:,} | 单元: {elements:,}")
        except Exception as e:
            self.pop_screen()
            self.update_status(f"错误: {e}")

    async def do_solve(self):
        if not self.mesh_data:
            self.update_status("请先执行 /mesh")
            return

        prog = ProgressScreen("有限元求解", ["边界条件", "刚度矩阵", "求解", "应力计算", "后处理", "完成"])
        self.push_screen(prog)

        try:
            steps = [(0, 0.1, "检查边界..."), (1, 0.3, "组装矩阵..."),
                     (2, 0.55, "求解方程..."), (3, 0.75, "计算应力..."), (4, 0.9, "生成云图...")]
            for s, p, m in steps:
                prog.update(s, p, m)
                await asyncio.sleep(0.4 + random.random() * 0.2)

            prog.update(5, 1.0, "完成!")
            await asyncio.sleep(0.2)

            self.solve_data = {"type": "solve", "solve_type": "static",
                               "max_disp": random.uniform(0.01, 0.1),
                               "max_stress": random.uniform(80, 200)}

            self.pop_screen()
            await self.push_screen_wait(ResultModal(self.solve_data))
            self.update_status(f"求解完成 | 最大应力: {self.solve_data['max_stress']:.1f} MPa")
        except Exception as e:
            self.pop_screen()
            self.update_status(f"错误: {e}")


def main():
    WorkTUI().run()


if __name__ == "__main__":
    main()
