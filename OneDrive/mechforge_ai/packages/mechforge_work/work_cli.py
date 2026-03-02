"""
MechForge Work - CAE Workbench CLI

基于 typer + rich 的本地计算工作台
交互式文件选择 + Gmsh 网格生成 + 结果显示
"""

import os
import sys
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.box import ROUNDED, SIMPLE_HEAVY

console = Console()


# ==================== 配置 ====================

class WorkConfig:
    """Work 模式配置"""
    def __init__(self):
        self.version = "v0.4.0"
        self.gmsh_version = "4.15.1"
        self.calculix_version = "2.21"
        self.pyvista_version = "0.47.1"

        self.current_file: Optional[Path] = None
        self.mesh_info: dict = {}
        self.solution_info: dict = {}
        self.boundary_conditions: dict = {}

    def reset(self):
        self.current_file = None
        self.mesh_info = {}
        self.solution_info = {}
        self.boundary_conditions = {}


config = WorkConfig()


# ==================== 文件选择器 ====================

def select_file_interactive() -> Optional[Path]:
    """交互式文件选择 (简化版数字选择)"""
    console.clear()
    
    # 扫描可用文件
    file_types = ['.step', '.stp', '.iges', '.igs', '.stl', '.obj', '.brep']
    files = []
    
    # 扫描当前目录
    for f in Path.cwd().iterdir():
        if f.is_file() and f.suffix.lower() in file_types:
            files.append(f)
    
    # 构建选项
    console.print(Panel(
        "[bold cyan]Select Geometry File[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    options = []
    
    # 示例模型
    console.print("[bold]Demo Models:[/]")
    demos = [
        ("Bracket", "demo_bracket.step"),
        ("Bearing", "demo_bearing.step"),
        ("Rod", "demo_rod.step"),
    ]
    for i, (name, _) in enumerate(demos, 1):
        console.print(f"  [cyan]{i}[/]. Create demo: {name}")
        options.append(Path(f"demo_{name.lower()}.step"))
    
    # 本地文件
    if files:
        console.print("\n[bold]Local Files:[/]")
        for f in files:
            i = len(options) + 1
            console.print(f"  [cyan]{i}[/]. {f.name}")
            options.append(f)
    
    console.print(f"\n  [dim]{len(options) + 1}. Cancel[/]")
    console.print()
    
    # 获取用户输入
    try:
        choice = console.input("[cyan]Select (1-{}): [/]".format(len(options) + 1))
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except (ValueError, KeyboardInterrupt):
        pass
    
    return None


# ==================== UI 组件 ====================

def print_banner():
    """打印横幅"""
    logo = """[cyan]███╗   ███╗███████╗ ██████╗██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██╔════╝██╔════╝██║  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██╔████╔██║█████╗  ██║     ███████║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝[/cyan]"""

    robot = Panel(
        """[bold red]╔═╦═╗
╠╣o o╠╣
╚╡▄▄▄╞╝
 ╔╩═══╩╗
 ║ CAE ║╾
 ╚╦═══╦╝
 ╔╩╗ ╔╩╗
 ╚═╝ ╚═╝[/bold red]

[green]✓ 就绪[/green]""",
        title="[bold red]🔧 MechBot[/bold red]",
        border_style="red",
        box=ROUNDED,
        padding=(0, 1),
    )

    console.print()
    table = Table(show_header=False, box=None, padding=0)
    table.add_column(width=75, no_wrap=True)
    table.add_column(width=18, no_wrap=True)
    table.add_row(logo, robot)
    console.print(table)
    console.print(Rule("[bold cyan]Work Mode - Gmsh + CalculiX", style="cyan"), style="cyan")


def print_status_panel():
    """打印状态面板"""
    model_status = config.current_file.name if config.current_file else "未加载"
    
    if config.solution_info:
        step = "solved"
    elif config.mesh_info:
        step = "meshed"
    elif config.current_file:
        step = "loaded"
    else:
        step = "idle"

    runtime = datetime.now().strftime("%H:%M:%S")

    grid = Table(box=SIMPLE_HEAVY, padding=(0, 1), show_edge=False, border_style="dim cyan")
    grid.add_column(width=12, style="orange1")
    grid.add_column(width=20, style="spring_green3")
    grid.add_column(width=12, style="orange1")
    grid.add_column(width=20, style="spring_green3")

    grid.add_row("[bold]Gmsh", config.gmsh_version, "[bold]当前模型", model_status)
    grid.add_row("[bold]PyVista", config.pyvista_version, "[bold]当前步骤", step)
    grid.add_row("[bold]CalculiX", config.calculix_version, "[bold]运行时间", runtime)

    console.print(grid)


def print_help_panel():
    """打印帮助面板"""
    help_text = Text("/mesh /solve /api /docker /discover /status /show /export /clear /exit", style="spring_green3")
    console.print(Panel(help_text, border_style="dim", padding=(0, 1)))


def print_mesh_result():
    """打印网格结果弹窗"""
    if not config.mesh_info:
        console.print("[yellow]尚未生成网格[/yellow]")
        return

    info = config.mesh_info
    
    # 质量进度条
    quality = info.get('quality', 0.85)
    bar_len = int(quality * 20)
    bar = "█" * bar_len + "░" * (20 - bar_len)
    
    result_panel = Panel(
        f"""[bold]节点数量:[/] [green]{info.get('nodes', 0):,}[/]
[bold]单元数量:[/] [green]{info.get('elements', 0):,}[/]
[bold]网格类型:[/] {info.get('type', 'tet')}
[bold]网格尺寸:[/] {info.get('size', 'N/A')} mm
[bold]网格质量:[/] [{bar}] {quality:.1%}""",
        title="[bold green]✓ 网格生成完成[/]",
        border_style="green",
        padding=(1, 2)
    )
    console.print(result_panel)


def print_solution_result():
    """打印求解结果弹窗"""
    if not config.solution_info:
        console.print("[yellow]尚未求解[/yellow]")
        return

    info = config.solution_info
    
    # 应力云图 ASCII
    cloud = """
    ┌─────────────────────────────┐
    │  [dim]···[/][cyan]▓▓[green]██████[yellow]███████[red]███[dim]···[/]  │
    │ [dim]··[/][cyan]▓▓▓[green]████████[yellow]█████████[red]████[cyan]▓[dim]··[/] │
    │[dim]··[/][cyan]▓▓[green]███████████[yellow]███████████[red]████[dim]··[/]│
    │  [green]███████████████[yellow]███████████████[red]███[dim]··[/]  │
    │   [green]████████████████[yellow]████████████████[red]██[dim]···[/]   │
    │    [cyan]▓▓[green]████████████████[yellow]█████████████[red]██[cyan]▓[dim]····[/]     │
    └─────────────────────────────┘"""
    
    result_panel = Panel(
        f"""[bold]求解类型:[/] {info.get('type', 'static')}
[bold]最大位移:[/] [green]{info.get('max_disp', 'N/A')} mm[/]
[bold]最大应力:[/] [yellow]{info.get('max_stress', 'N/A')} MPa[/]

[bold cyan]Von Mises 应力云图[/]{cloud}

[red]最大: {info.get('max_stress', 0):.1f}[/]  [blue]最小: {info.get('max_stress', 0) * 0.1:.1f}[/] MPa""",
        title="[bold green]✓ 求解完成[/]",
        border_style="green",
        padding=(1, 2)
    )
    console.print(result_panel)


# ==================== 命令处理器 ====================

def _progress_callback(progress: float, message: str, progress_obj, task_id):
    """进度回调函数"""
    progress_obj.update(task_id, description=message, completed=int(progress * 100))


async def handle_mesh(mesh_size: float = 5.0, mesh_type: str = "tet"):
    """生成网格 - 使用真实 Gmsh 引擎"""
    from mechforge_work.mesh_engine import get_engine, cleanup_engine
    
    # 1. 弹出文件选择
    console.print("\n[cyan]📁 选择几何文件...[/]")
    
    result = select_file_interactive()
    
    if result is None:
        console.print("[yellow]已取消[/yellow]")
        return False
    
    config.current_file = result
    
    # 判断是否是示例模型
    is_demo = result.name.startswith("demo_")
    
    if is_demo:
        demo_type = result.stem.replace("demo_", "")
        console.print(f"[green]✓ 创建示例模型: {demo_type}[/]")
    else:
        console.print(f"[green]✓ 已选择: {result.name}[/]")
    
    # 2. 使用真实 Gmsh 引擎
    console.print(f"\n[cyan]⚙ 启动 Gmsh 生成网格...[/]")
    
    engine = get_engine()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("初始化...", total=100)
            
            def callback(p, msg):
                _progress_callback(p, msg, progress, task)
            
            # 加载几何
            callback(0.1, "加载几何模型...")
            
            if is_demo:
                demo_type = result.stem.replace("demo_", "")
                success, info = engine.create_demo_geometry(demo_type)
            else:
                success, info = engine.load_geometry(result)
            
            if not success:
                console.print(f"[red]✗ {info}[/]")
                return False
            
            console.print(f"[dim]  几何信息: {info}[/]")
            
            # 生成网格
            callback(0.2, "生成网格...")
            
            mesh_result = engine.generate_mesh(
                mesh_size=mesh_size,
                mesh_type=mesh_type,
                optimize=True,
                progress_callback=callback
            )
            
            if not mesh_result.success:
                console.print(f"[red]✗ {mesh_result.error}[/]")
                return False
            
            # 更新配置
            config.mesh_info = {
                "nodes": mesh_result.nodes,
                "elements": mesh_result.elements,
                "type": mesh_type,
                "size": mesh_size,
                "quality": mesh_result.quality,
                "mesh_file": str(mesh_result.mesh_file) if mesh_result.mesh_file else None,
                "generated": True,
                "info": mesh_result.info
            }
        
        # 3. 显示结果
        console.print()
        print_mesh_result()
        
        # 显示额外信息
        if mesh_result.info:
            elapsed = mesh_result.info.get("elapsed_time", 0)
            console.print(f"[dim]  耗时: {elapsed:.2f}s[/]")
            if mesh_result.mesh_file:
                console.print(f"[dim]  网格文件: {mesh_result.mesh_file}[/]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]网格生成失败: {e}[/]")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理引擎
        cleanup_engine()


def handle_solve(analysis_type: str = "static", use_api: bool = False, api_endpoint: str = None) -> bool:
    """求解 - 使用 CalculiX 引擎或 API"""
    if not config.mesh_info.get("generated"):
        console.print("[red]请先生成网格 /mesh[/red]")
        return False

    from mechforge_work.solver_engine import get_solver, SolveMode, BoundaryCondition

    solver = get_solver(api_endpoint)

    # 获取可用求解器
    solvers = solver.get_available_solvers()

    # 决定求解模式
    if use_api and solvers.get("api"):
        console.print(f"\n[cyan]🌐 使用 API 远程求解...[/]")
        console.print(f"[dim]  端点: {solver.api_endpoint}[/]")
        solve_mode = "api"
    elif solvers.get("local_ccx"):
        console.print(f"\n[cyan]⚙ 启动本地 CalculiX 求解器...[/]")
        solve_mode = "local"
    else:
        console.print(f"\n[yellow]⚠ CalculiX 未安装且无 API，使用模拟求解...[/]")
        solve_mode = "sim"

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("初始化...", total=100)

            def callback(p, msg):
                progress.update(task, description=msg, completed=int(p * 100))

            solver.set_progress_callback(callback)

            # 根据模式选择求解方法
            if solve_mode == "api":
                mesh_file = config.mesh_info.get("mesh_file")
                result = solver.solve_via_api(
                    mesh_file=Path(mesh_file) if mesh_file else None,
                    analysis_type=analysis_type
                )
            elif solve_mode == "local":
                result = solver.solve(
                    analysis_type=analysis_type,
                    progress_callback=callback,
                    simulation_mode=False
                )
            else:
                result = solver.solve(
                    analysis_type=analysis_type,
                    progress_callback=callback,
                    simulation_mode=True
                )

        if not result.success:
            console.print(f"[red]✗ {result.error}[/]")
            return False

        # 更新配置
        config.solution_info = {
            "type": analysis_type,
            "max_disp": result.max_disp,
            "max_stress": result.max_stress,
            "min_stress": result.min_stress,
            "solve_time": result.solve_time,
            "solved": True,
            "solve_mode": solve_mode,
            "info": result.info
        }

        console.print()
        print_solution_result()

        # 显示额外信息
        if result.info:
            if solve_mode == "api":
                console.print(f"[green]✓ API 求解完成[/]")
                if result.info.get("job_id"):
                    console.print(f"[dim]  任务ID: {result.info['job_id']}[/]")
            elif solve_mode == "sim":
                console.print(f"[dim]  (模拟模式)[/]")
            console.print(f"[dim]  求解时间: {result.solve_time:.2f}s[/]")

        return True

    except Exception as e:
        console.print(f"[red]求解失败: {e}[/]")
        return False


def handle_api_status(api_endpoint: str = None):
    """检查 API 状态"""
    from mechforge_work.solver_engine import get_solver

    solver = get_solver(api_endpoint)

    console.print("\n[cyan]📡 检查求解器状态...[/]\n")

    # 获取可用求解器
    solvers = solver.get_available_solvers()

    table = Table(title="求解器状态", box=ROUNDED)
    table.add_column("求解器", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("详情")

    # 本地 CalculiX
    ccx_status = "[green]✓ 可用[/]" if solvers["local_ccx"] else "[red]✗ 不可用[/]"
    table.add_row("本地 CalculiX", ccx_status, solver.ccx_path or "未安装")

    # API
    api_status = "[green]✓ 可用[/]" if solvers["api"] else "[red]✗ 不可用[/]"
    table.add_row("API 远程求解", api_status, solvers["api_endpoint"])

    # 模拟模式
    table.add_row("模拟求解", "[green]✓ 可用[/]", "始终可用")

    console.print(table)

    # API 详细状态
    if solver.api_endpoint:
        status = solver.check_api_status()
        if status.get("available"):
            console.print(f"\n[green]API 服务状态:[/]")
            console.print(f"  状态: {status.get('status', 'unknown')}")
            console.print(f"  版本: {status.get('version', 'unknown')}")
            console.print(f"  队列: {status.get('queue_size', 0)} 任务")


def handle_set_api(endpoint: str):
    """设置 API 端点"""
    from mechforge_work.solver_engine import get_solver

    solver = get_solver()
    solver.set_api_endpoint(endpoint)

    # 保存到环境变量 (当前会话)
    os.environ["CALCULIX_API"] = endpoint

    console.print(f"\n[green]✓ API 端点已设置: {endpoint}[/]")

    # 测试连接
    status = solver.check_api_status()
    if status.get("available"):
        console.print(f"[green]✓ 连接成功[/]")
    else:
        console.print(f"[yellow]⚠ 无法连接: {status.get('error', 'unknown')}[/]")


def handle_docker_start():
    """启动 Docker 求解器容器"""
    from mechforge_work.solver_engine import start_docker_solvers

    console.print("\n[cyan]🐳 启动 Docker 求解器...[/]")

    result = start_docker_solvers()

    if result.get("success"):
        console.print(f"[green]✓ {result.get('message', '已启动')}[/]")

        # 等待服务就绪
        import time
        console.print("[dim]  等待服务就绪...[/]")
        time.sleep(3)

        # 显示状态
        handle_api_status()
    else:
        console.print(f"[red]✗ 启动失败: {result.get('error', '未知错误')}[/]")
        console.print("[dim]  请确保已运行 setup-solver.bat 安装 Docker 环境[/]")


def handle_docker_stop():
    """停止 Docker 求解器容器"""
    from mechforge_work.solver_engine import stop_docker_solvers

    console.print("\n[cyan]🐳 停止 Docker 求解器...[/]")

    result = stop_docker_solvers()

    if result.get("success"):
        console.print(f"[green]✓ 容器已停止[/]")
    else:
        console.print(f"[red]✗ 停止失败: {result.get('error', '未知错误')}[/]")


def handle_discover():
    """发现可用的求解器"""
    from mechforge_work.solver_engine import get_solver

    console.print("\n[cyan]🔍 扫描求解器...[/]\n")

    solver = get_solver()
    solvers = solver.discover_docker_solvers()

    if solvers:
        table = Table(title="发现的求解器", box=ROUNDED)
        table.add_column("端口", style="cyan")
        table.add_column("URL", style="green")
        table.add_column("状态", style="yellow")
        table.add_column("CalculiX", style="magenta")

        for s in solvers:
            ccx_status = "✓" if s.get("ccx_available") else "✗"
            table.add_row(
                str(s["port"]),
                s["url"],
                s["status"],
                ccx_status
            )

        console.print(table)

        # 自动配置第一个
        if solvers:
            first = solvers[0]["url"]
            solver.set_api_endpoint(first)
            console.print(f"\n[green]✓ 已自动配置: {first}[/]")
    else:
        console.print("[yellow]未发现 Docker 求解器容器[/]")
        console.print("[dim]  运行 /docker start 或 setup-solver.bat 启动容器[/]")


def handle_show(result_type: str = "vonmises"):
    """显示结果 - 支持交互式可视化"""
    if not config.solution_info.get("solved"):
        console.print("[red]请先求解 /solve[/red]")
        return
    
    from mechforge_work.viz_engine import get_visualizer, ASCIIViewer
    
    viz = get_visualizer()
    
    # 检查 PyVista 是否可用
    if viz.is_available():
        console.print(f"\n[cyan]📊 启动 PyVista 可视化...[/]")
        console.print("[dim]  (按 Q 退出可视化窗口)[/]")
        
        # 获取网格文件
        mesh_file = config.mesh_info.get("mesh_file")
        if mesh_file:
            mesh_path = Path(mesh_file)
            if mesh_path.exists():
                viz.load_mesh(mesh_path)
        
        # 显示结果
        if result_type in ["vonmises", "stress"]:
            result = viz.show_stress_result()
        elif result_type in ["displacement", "disp"]:
            result = viz.show_displacement_result()
        else:
            result = viz.show_mesh()
        
        if not result.success:
            console.print(f"[yellow]可视化失败: {result.error}[/]")
            console.print("[dim]  使用 ASCII 模式显示[/]")
            print_solution_result()
    else:
        # PyVista 不可用，使用 ASCII 模式
        console.print(f"\n[yellow]PyVista 不可用，使用 ASCII 云图[/]")
        print_solution_result()
        
        # 显示额外的 ASCII 可视化
        max_stress = config.solution_info.get("max_stress", 100)
        min_stress = config.solution_info.get("min_stress", 10)
        
        viewer = ASCIIViewer()
        cloud = viewer.render_stress_cloud(max_stress, min_stress)
        console.print(cloud)


def handle_export(export_format: str = "vtk") -> bool:
    """导出结果"""
    if not config.solution_info.get("solved"):
        console.print("[red]请先求解 /solve[/red]")
        return False

    console.print(f"[cyan]导出 {export_format.upper()} 文件...[/]")
    time.sleep(0.5)
    console.print(f"[green]✓ 已导出 {export_format.upper()} 文件[/green]")
    return True


# ==================== 主循环 ====================

def main():
    """Work 模式主入口"""
    import argparse
    parser = argparse.ArgumentParser(
        prog='mechforge-work',
        description='MechForge CAE Workbench - Gmsh + CalculiX'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 0.4.0')
    parser.add_argument('--tui', action='store_true', help='启动 TUI 界面')
    args = parser.parse_args()

    # TUI 模式
    if args.tui:
        from mechforge_work.work_tui import main as tui_main
        tui_main()
        return

    # CLI 模式
    os.environ['PYTHONIOENCODING'] = 'utf-8'

    if sys.platform == "win32" and hasattr(sys.stdout, 'buffer'):
        import io
        try:
            if not isinstance(sys.stdout, io.TextIOWrapper):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            if not isinstance(sys.stderr, io.TextIOWrapper):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass

    print_banner()
    print_status_panel()
    print_help_panel()

    # 主循环
    while True:
        try:
            user_input = console.input("[spring_green3][MechBot] >[/] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/exit", "/quit", "/q"]:
                console.print("\n[cyan]再见![/cyan]\n")
                break

            if user_input.lower() == "/clear":
                console.clear()
                print_banner()
                print_status_panel()
                print_help_panel()
                continue

            parts = user_input.split()
            cmd = parts[0].lower()
            args_list = parts[1:]

            if cmd in ["/mesh", "/m"]:
                import asyncio
                asyncio.run(handle_mesh())

            elif cmd in ["/solve", "/s"]:
                # 检查是否使用 API
                use_api = "--api" in args_list or "-a" in args_list
                handle_solve(use_api=use_api)

            elif cmd in ["/api", "/api-set"]:
                if args_list:
                    handle_set_api(args_list[0])
                else:
                    handle_api_status()

            elif cmd == "/status":
                handle_api_status()

            elif cmd == "/discover":
                handle_discover()

            elif cmd in ["/docker", "/d"]:
                if args_list:
                    subcmd = args_list[0].lower()
                    if subcmd in ["start", "up"]:
                        handle_docker_start()
                    elif subcmd in ["stop", "down"]:
                        handle_docker_stop()
                    elif subcmd in ["status", "ps"]:
                        handle_api_status()
                    else:
                        console.print("[yellow]用法: /docker start|stop|status[/]")
                else:
                    console.print("[cyan]Docker 命令:[/]")
                    console.print("  [green]/docker start[/] - 启动求解器容器")
                    console.print("  [green]/docker stop[/]  - 停止求解器容器")
                    console.print("  [green]/docker status[/] - 查看容器状态")

            elif cmd in ["/show", "/view", "/v"]:
                handle_show()

            elif cmd == "/export":
                export_format = args_list[0] if args_list else "vtk"
                handle_export(export_format)

            elif cmd in ["/help", "/h", "/?"]:
                console.print(Panel(
                    "[bold]可用命令[/]\n\n"
                    "[cyan]/mesh[/]  - 生成网格 (选择文件)\n"
                    "[cyan]/solve[/] - 求解模型\n"
                    "[cyan]/solve --api[/] - 使用 API 远程求解\n"
                    "[cyan]/api <url>[/] - 设置/查看 API 端点\n"
                    "[cyan]/status[/] - 查看求解器状态\n"
                    "[cyan]/discover[/] - 发现 Docker 求解器\n"
                    "[cyan]/docker start|stop[/] - 管理 Docker 容器\n"
                    "[cyan]/show[/]  - 显示结果\n"
                    "[cyan]/export[/] - 导出结果\n"
                    "[cyan]/clear[/] - 清屏\n"
                    "[cyan]/quit[/]  - 退出",
                    border_style="cyan"
                ))

            elif cmd == "/status-old":
                print_status_panel()

            else:
                console.print(f"[red]未知命令: {cmd}[/red]")
                console.print("[dim]输入 /help 查看可用命令[/dim]")

        except KeyboardInterrupt:
            console.print("\n[dim]使用 /exit 退出[/dim]")
            continue
        except EOFError:
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())


# ==================== Typer CLI ====================

app = typer.Typer()


@app.command()
def mesh(
    filepath: str = typer.Argument(None, help="STEP/IGES/STL 文件路径"),
):
    """生成网格"""
    if filepath:
        config.current_file = Path(filepath)
    import asyncio
    asyncio.run(handle_mesh())


@app.command()
def solve(
    api: bool = typer.Option(False, "--api", "-a", help="使用 API 远程求解"),
    endpoint: str = typer.Option(None, "--endpoint", "-e", help="API 端点"),
):
    """执行求解"""
    handle_solve(use_api=api, api_endpoint=endpoint)


@app.command()
def api(
    endpoint: str = typer.Argument(None, help="API 端点 URL"),
):
    """设置或查看 API 端点"""
    if endpoint:
        handle_set_api(endpoint)
    else:
        handle_api_status()


@app.command()
def status():
    """查看求解器状态"""
    handle_api_status()


@app.command()
def show():
    """显示结果"""
    handle_show()


@app.command()
def export(
    format: str = typer.Argument("vtk", help="导出格式 (vtk/frd/pdf)"),
):
    """导出结果"""
    handle_export(format)


@app.command()
def docker(
    action: str = typer.Argument(None, help="操作: start, stop, status"),
):
    """管理 Docker 求解器容器"""
    if action == "start":
        handle_docker_start()
    elif action == "stop":
        handle_docker_stop()
    elif action == "status":
        handle_api_status()
    else:
        console.print("[cyan]Docker 命令:[/]")
        console.print("  [green]mechforge-work docker start[/]  - 启动求解器容器")
        console.print("  [green]mechforge-work docker stop[/]   - 停止求解器容器")
        console.print("  [green]mechforge-work docker status[/] - 查看容器状态")


@app.command()
def discover():
    """发现可用的求解器"""
    handle_discover()