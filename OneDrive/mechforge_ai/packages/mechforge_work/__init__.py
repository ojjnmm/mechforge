"""
MechForge Work - Local CAE Workbench

Gmsh + CalculiX 本地计算工作台
支持本地求解和 API 远程求解
"""

__version__ = "0.4.0"

# CLI 入口
def main():
    """CLI 主入口"""
    from mechforge_work.work_cli import main as cli_main
    cli_main()

# TUI 入口
def tui():
    """TUI 主入口"""
    from mechforge_work.work_tui import main as tui_main
    tui_main()

# 引擎入口
def get_mesh_engine():
    """获取网格引擎"""
    from mechforge_work.mesh_engine import get_engine
    return get_engine()

def get_solver_engine(api_endpoint: str = None):
    """
    获取求解引擎
    
    Args:
        api_endpoint: 可选的 API 端点
    """
    from mechforge_work.solver_engine import get_solver
    return get_solver(api_endpoint)

def get_viz_engine():
    """获取可视化引擎"""
    from mechforge_work.viz_engine import get_visualizer
    return get_visualizer()

# 便捷函数
def set_calculix_api(endpoint: str):
    """设置 CalculiX API 端点"""
    from mechforge_work.solver_engine import get_solver
    solver = get_solver()
    solver.set_api_endpoint(endpoint)
    return solver.check_api_status()

def check_solvers():
    """检查可用求解器"""
    from mechforge_work.solver_engine import get_solver
    solver = get_solver()
    return solver.get_available_solvers()

# 导出
__all__ = [
    "main", "tui",
    "get_mesh_engine", "get_solver_engine", "get_viz_engine",
    "set_calculix_api", "check_solvers",
]