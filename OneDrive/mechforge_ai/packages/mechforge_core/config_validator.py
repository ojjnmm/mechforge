#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MechForge Work - Configuration Validator

配置验证和管理模块
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)


class ConfigValidator:
    """配置验证器"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def reset(self):
        """重置验证状态"""
        self.errors = []
        self.warnings = []

    def validate_all(self) -> ValidationResult:
        """执行所有验证"""
        self.reset()

        # 验证 Python 版本
        self._validate_python_version()

        # 验证依赖
        self._validate_dependencies()

        # 验证环境变量
        self._validate_environment()

        # 验证路径
        self._validate_paths()

        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings
        )

    def _validate_python_version(self):
        """验证 Python 版本"""
        required_version = (3, 10)
        current_version = sys.version_info[:2]

        if current_version < required_version:
            self.errors.append(
                f"Python 版本过低: {current_version[0]}.{current_version[1]}，"
                f"需要 >= {required_version[0]}.{required_version[1]}"
            )

    def _validate_dependencies(self):
        """验证依赖包"""
        # 核心依赖
        core_deps = [
            ("rich", "Rich 终端输出库"),
            ("typer", "CLI 框架"),
            ("yaml", "YAML 配置解析"),
        ]

        # CAE 依赖
        cae_deps = [
            ("gmsh", "Gmsh 网格引擎"),
            ("pyvista", "PyVista 可视化"),
            ("trimesh", "Trimesh 几何处理"),
            ("textual", "Textual TUI 框架"),
        ]

        # 验证核心依赖
        for module, desc in core_deps:
            try:
                __import__(module)
            except ImportError:
                self.errors.append(f"缺少核心依赖: {module} ({desc})")

        # 验证 CAE 依赖 (警告)
        for module, desc in cae_deps:
            try:
                __import__(module)
            except ImportError:
                self.warnings.append(f"缺少 CAE 依赖: {module} ({desc})，部分功能不可用")

    def _validate_environment(self):
        """验证环境变量"""
        # 可选的环境变量
        optional_env = [
            ("OPENAI_API_KEY", "OpenAI API"),
            ("ANTHROPIC_API_KEY", "Anthropic API"),
            ("OLLAMA_URL", "Ollama 服务"),
            ("CALCULIX_API", "CalculiX API"),
        ]

        for env_var, desc in optional_env:
            value = os.environ.get(env_var)
            if value:
                # 检查是否是占位符
                if "your_" in value.lower() or "xxx" in value.lower():
                    self.warnings.append(f"{env_var} 可能是占位符值")

    def _validate_paths(self):
        """验证路径"""
        # 检查工作目录
        cwd = Path.cwd()
        if not cwd.exists():
            self.errors.append(f"工作目录不存在: {cwd}")

        # 检查临时目录
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        if not temp_dir.exists():
            self.warnings.append(f"临时目录不存在: {temp_dir}")


class SolverValidator:
    """求解器验证器"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_solvers(self) -> ValidationResult:
        """验证求解器可用性"""
        self.errors = []
        self.warnings = []

        info = {}

        # 检查本地 CalculiX
        ccx_available = self._check_calculix()
        info["local_ccx"] = ccx_available

        if not ccx_available:
            self.warnings.append("本地 CalculiX 未安装，将使用模拟模式或 API 求解")

        # 检查 API
        api_info = self._check_api()
        info["api"] = api_info

        return ValidationResult(
            valid=True,  # 至少有模拟模式可用
            errors=self.errors,
            warnings=self.warnings,
            info=info
        )

    def _check_calculix(self) -> bool:
        """检查本地 CalculiX"""
        import subprocess

        names = ["ccx", "ccx_2.21", "ccx_2.20", "calculix"]

        for name in names:
            try:
                result = subprocess.run(
                    ["where", name] if sys.platform == "win32" else ["which", name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return True
            except:
                pass

        return False

    def _check_api(self) -> Dict[str, Any]:
        """检查 API 可用性"""
        import urllib.request
        import json

        endpoints = [
            os.environ.get("CALCULIX_API", ""),
            "http://localhost:8080",
            "http://localhost:8081",
        ]

        info = {
            "available": False,
            "endpoints": []
        }

        for endpoint in endpoints:
            if not endpoint:
                continue

            try:
                url = f"{endpoint.rstrip('/')}/status"
                req = urllib.request.Request(url, method='GET')

                with urllib.request.urlopen(req, timeout=2) as response:
                    result = json.loads(response.read().decode('utf-8'))

                    info["endpoints"].append({
                        "url": endpoint,
                        "status": result.get("status", "unknown")
                    })
                    info["available"] = True

            except:
                pass

        return info


class MeshEngineValidator:
    """网格引擎验证器"""

    def validate_gmsh(self) -> ValidationResult:
        """验证 Gmsh"""
        errors = []
        warnings = []
        info = {}

        try:
            import gmsh
            
            # 获取版本
            gmsh.initialize()
            version = gmsh.option.getString("General.Version")
            gmsh.finalize()
            
            info["version"] = version
            info["available"] = True

            # 检查版本
            major, minor, _ = map(int, version.split('.')[:3])
            if (major, minor) < (4, 13):
                warnings.append(f"Gmsh 版本较低: {version}，建议 >= 4.13")

        except ImportError:
            errors.append("Gmsh 未安装，请运行: pip install gmsh")
            info["available"] = False
        except Exception as e:
            errors.append(f"Gmsh 初始化失败: {e}")
            info["available"] = False

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info
        )


def check_system_requirements() -> Dict[str, Any]:
    """
    检查系统要求

    Returns:
        检查结果字典
    """
    results = {
        "passed": True,
        "checks": {}
    }

    # Python 版本
    results["checks"]["python"] = {
        "required": ">=3.10",
        "current": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "passed": sys.version_info >= (3, 10)
    }

    # 操作系统
    results["checks"]["os"] = {
        "system": sys.platform,
        "passed": True
    }

    # 依赖检查
    validator = ConfigValidator()
    result = validator.validate_all()

    results["checks"]["dependencies"] = {
        "errors": result.errors,
        "warnings": result.warnings,
        "passed": result.valid
    }

    # Gmsh
    mesh_validator = MeshEngineValidator()
    gmsh_result = mesh_validator.validate_gmsh()

    results["checks"]["gmsh"] = {
        "available": gmsh_result.info.get("available", False),
        "version": gmsh_result.info.get("version", "N/A"),
        "passed": gmsh_result.valid
    }

    # CalculiX
    solver_validator = SolverValidator()
    solver_result = solver_validator.validate_solvers()

    results["checks"]["solver"] = {
        "local_ccx": solver_result.info.get("local_ccx", False),
        "api": solver_result.info.get("api", {}).get("available", False),
        "passed": True  # 至少有模拟模式
    }

    # 总体结果
    results["passed"] = all(
        check.get("passed", True)
        for check in results["checks"].values()
    )

    return results


def print_system_check():
    """打印系统检查结果"""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()

    results = check_system_requirements()

    # 标题
    status = "[green]✓ 通过[/]" if results["passed"] else "[red]✗ 未通过[/]"
    console.print(Panel(
        f"系统检查结果: {status}",
        title="MechForge AI 系统检查",
        border_style="cyan"
    ))

    # 详细结果
    table = Table(show_header=True, box=None)
    table.add_column("检查项", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("详情")

    checks = results["checks"]

    # Python
    py_check = checks["python"]
    status = "[green]✓[/]" if py_check["passed"] else "[red]✗[/]"
    table.add_row("Python", status, f"当前: {py_check['current']}, 需要: {py_check['required']}")

    # OS
    os_check = checks["os"]
    table.add_row("操作系统", "[green]✓[/]", os_check["system"])

    # Gmsh
    gmsh_check = checks["gmsh"]
    status = "[green]✓[/]" if gmsh_check["passed"] else "[yellow]![/]"
    table.add_row("Gmsh", status, f"版本: {gmsh_check['version']}")

    # Solver
    solver_check = checks["solver"]
    local = "[green]✓[/]" if solver_check["local_ccx"] else "[yellow]![/]"
    api = "[green]✓[/]" if solver_check["api"] else "[dim]-[/]"
    table.add_row("CalculiX (本地)", local, "已安装" if solver_check["local_ccx"] else "未安装")
    table.add_row("CalculiX (API)", api, "可用" if solver_check["api"] else "未配置")

    console.print(table)

    # 警告和错误
    dep_check = checks["dependencies"]
    if dep_check["warnings"]:
        console.print("\n[yellow]警告:[/]")
        for w in dep_check["warnings"]:
            console.print(f"  • {w}")

    if dep_check["errors"]:
        console.print("\n[red]错误:[/]")
        for e in dep_check["errors"]:
            console.print(f"  • {e}")

    return results["passed"]


if __name__ == "__main__":
    print_system_check()