#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MechForge Work - Solver Engine Tests

测试 CalculiX 求解引擎功能
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class TestSolveResult:
    """测试 SolveResult 数据类"""

    def test_solve_result_creation(self):
        """测试 SolveResult 创建"""
        from mechforge_work.solver_engine import SolveResult, SolveMode
        
        result = SolveResult(
            success=True,
            solve_type="static",
            solve_mode=SolveMode.SIMULATION,
            max_disp=0.05,
            max_stress=150.0
        )
        
        assert result.success is True
        assert result.solve_type == "static"
        assert result.solve_mode == SolveMode.SIMULATION
        assert result.max_disp == 0.05
        assert result.max_stress == 150.0

    def test_solve_result_failure(self):
        """测试失败的 SolveResult"""
        from mechforge_work.solver_engine import SolveResult
        
        result = SolveResult(
            success=False,
            error="Connection timeout"
        )
        
        assert result.success is False
        assert result.error == "Connection timeout"


class TestBoundaryCondition:
    """测试 BoundaryCondition 数据类"""

    def test_boundary_condition_fixed(self):
        """测试固定边界条件"""
        from mechforge_work.solver_engine import BoundaryCondition
        
        bc = BoundaryCondition(
            name="fixed_face",
            bc_type="fixed",
            target="face_1",
            values={"x": 0, "y": 0, "z": 0}
        )
        
        assert bc.name == "fixed_face"
        assert bc.bc_type == "fixed"
        assert bc.values["x"] == 0

    def test_boundary_condition_force(self):
        """测试力边界条件"""
        from mechforge_work.solver_engine import BoundaryCondition
        
        bc = BoundaryCondition(
            name="applied_force",
            bc_type="force",
            target="face_2",
            values={"fx": 100, "fy": 0, "fz": -50}
        )
        
        assert bc.bc_type == "force"
        assert bc.values["fx"] == 100


class TestMaterial:
    """测试 Material 数据类"""

    def test_material_creation(self):
        """测试材料创建"""
        from mechforge_work.solver_engine import Material
        
        material = Material(
            name="Steel",
            youngs_modulus=210000,
            poisson_ratio=0.3,
            density=7850
        )
        
        assert material.name == "Steel"
        assert material.youngs_modulus == 210000
        assert material.poisson_ratio == 0.3

    def test_predefined_materials(self):
        """测试预定义材料"""
        from mechforge_work.solver_engine import MATERIALS
        
        assert "steel" in MATERIALS
        assert "aluminum" in MATERIALS
        assert "copper" in MATERIALS
        assert "titanium" in MATERIALS
        
        assert MATERIALS["steel"].youngs_modulus == 210000
        assert MATERIALS["aluminum"].youngs_modulus == 70000


class TestCalculiXEngine:
    """测试 CalculiXEngine 类"""

    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        from mechforge_work.solver_engine import CalculiXEngine, cleanup_solver
        cleanup_solver()
        yield CalculiXEngine()
        cleanup_solver()

    def test_engine_creation(self, engine):
        """测试引擎创建"""
        assert engine is not None
        assert hasattr(engine, 'solve')
        assert hasattr(engine, 'solve_via_api')
        assert hasattr(engine, 'is_available')

    def test_is_available(self, engine):
        """测试可用性检查"""
        result = engine.is_available()
        assert isinstance(result, bool)

    def test_set_api_endpoint(self, engine):
        """测试设置 API 端点"""
        engine.set_api_endpoint("http://localhost:8080")
        assert engine.api_endpoint == "http://localhost:8080"

    def test_set_material(self, engine):
        """测试设置材料"""
        from mechforge_work.solver_engine import Material
        
        material = Material(name="Custom", youngs_modulus=100000)
        engine.set_material(material)
        
        assert engine.material.name == "Custom"
        assert engine.material.youngs_modulus == 100000

    def test_set_material_by_name(self, engine):
        """测试按名称设置材料"""
        result = engine.set_material_by_name("aluminum")
        assert result is True
        assert engine.material.name == "Aluminum"

    def test_set_invalid_material(self, engine):
        """测试设置无效材料"""
        result = engine.set_material_by_name("invalid_material")
        assert result is False

    def test_add_boundary_condition(self, engine):
        """测试添加边界条件"""
        from mechforge_work.solver_engine import BoundaryCondition
        
        bc = BoundaryCondition(
            name="test_bc",
            bc_type="fixed",
            target="face_1"
        )
        
        engine.add_boundary_condition(bc)
        
        assert len(engine.boundary_conditions) == 1
        assert engine.boundary_conditions[0].name == "test_bc"

    def test_clear_boundary_conditions(self, engine):
        """测试清空边界条件"""
        from mechforge_work.solver_engine import BoundaryCondition
        
        bc = BoundaryCondition(name="bc1", bc_type="fixed", target="face_1")
        engine.add_boundary_condition(bc)
        
        engine.clear_boundary_conditions()
        
        assert len(engine.boundary_conditions) == 0

    def test_simulate_solve(self, engine):
        """测试模拟求解"""
        result = engine.solve(
            analysis_type="static",
            simulation_mode=True
        )
        
        assert result.success is True
        assert result.max_disp > 0
        assert result.max_stress > 0

    def test_generate_inp(self, engine, tmp_path):
        """测试生成 INP 文件"""
        inp_file = engine.generate_inp(
            analysis_type="static",
            output_path=tmp_path / "test.inp"
        )
        
        assert inp_file.exists()
        
        content = inp_file.read_text()
        assert "*HEADING" in content
        assert "*MATERIAL" in content

    def test_get_available_solvers(self, engine):
        """测试获取可用求解器"""
        solvers = engine.get_available_solvers()
        
        assert isinstance(solvers, dict)
        assert "local_ccx" in solvers
        assert "api" in solvers
        assert "simulation" in solvers
        assert solvers["simulation"] is True

    def test_solve_via_api_no_endpoint(self, engine):
        """测试无端点时的 API 求解"""
        engine.api_endpoint = ""
        result = engine.solve_via_api()
        
        assert result.success is False
        assert "未配置 API 端点" in result.error


class TestAPISolverFunctions:
    """测试 API 求解函数"""

    def test_check_api_status_no_endpoint(self):
        """测试无端点时的状态检查"""
        from mechforge_work.solver_engine import CalculiXEngine, cleanup_solver
        
        cleanup_solver()
        engine = CalculiXEngine()
        engine.api_endpoint = ""
        
        status = engine.check_api_status()
        
        assert status["available"] is False
        assert "未配置" in status["error"]
        
        cleanup_solver()

    @patch('urllib.request.urlopen')
    def test_check_api_status_success(self, mock_urlopen):
        """测试 API 状态检查成功"""
        from mechforge_work.solver_engine import CalculiXEngine, cleanup_solver
        import json
        
        # 模拟响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "running",
            "version": "1.0.0",
            "queue_size": 0
        }).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        cleanup_solver()
        engine = CalculiXEngine()
        engine.api_endpoint = "http://localhost:8080"
        
        status = engine.check_api_status()
        
        assert status["available"] is True
        assert status["status"] == "running"
        
        cleanup_solver()


class TestSolverFunctions:
    """测试求解器函数"""

    def test_get_solver_singleton(self):
        """测试求解器单例"""
        from mechforge_work.solver_engine import get_solver, cleanup_solver
        
        cleanup_solver()
        
        solver1 = get_solver()
        solver2 = get_solver()
        
        assert solver1 is solver2
        
        cleanup_solver()

    def test_get_solver_with_endpoint(self):
        """测试带端点获取求解器"""
        from mechforge_work.solver_engine import get_solver, cleanup_solver
        
        cleanup_solver()
        
        solver = get_solver("http://test:8080")
        
        assert solver.api_endpoint == "http://test:8080"
        
        cleanup_solver()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])