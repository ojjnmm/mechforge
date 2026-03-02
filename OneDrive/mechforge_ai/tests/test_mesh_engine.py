#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MechForge Work - Mesh Engine Tests

测试 Gmsh 网格引擎功能
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class TestMeshEngine:
    """测试 GmshEngine 类"""

    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        from mechforge_work.mesh_engine import GmshEngine, cleanup_engine
        cleanup_engine()  # 清理之前的实例
        yield GmshEngine()
        cleanup_engine()  # 测试后清理

    def test_engine_creation(self, engine):
        """测试引擎创建"""
        assert engine is not None
        assert hasattr(engine, 'initialize')
        assert hasattr(engine, 'create_demo_geometry')
        assert hasattr(engine, 'generate_mesh')

    def test_initialize(self, engine):
        """测试初始化"""
        result = engine.initialize()
        assert isinstance(result, bool)
        engine.finalize()

    def test_create_demo_block(self, engine):
        """测试创建方块模型"""
        engine.initialize()
        success, info = engine.create_demo_geometry("block")
        assert success is True
        engine.finalize()

    def test_create_demo_bracket(self, engine):
        """测试创建支架模型"""
        engine.initialize()
        success, info = engine.create_demo_geometry("bracket")
        assert success is True
        engine.finalize()

    def test_create_demo_cylinder(self, engine):
        """测试创建圆柱模型"""
        engine.initialize()
        success, info = engine.create_demo_geometry("cylinder")
        assert success is True
        engine.finalize()

    def test_invalid_demo_model(self, engine):
        """测试无效模型名称"""
        engine.initialize()
        success, info = engine.create_demo_geometry("invalid_model")
        assert success is False
        engine.finalize()

    def test_mesh_generation(self, engine):
        """测试网格生成"""
        engine.initialize()
        engine.create_demo_geometry("block")
        
        result = engine.generate_mesh(mesh_size=10.0, mesh_type="tet")
        
        assert result.success is True
        assert result.nodes > 0
        assert result.elements > 0
        assert result.quality > 0
        
        engine.finalize()

    def test_mesh_export(self, engine, tmp_path):
        """测试网格导出"""
        engine.initialize()
        engine.create_demo_geometry("block")
        engine.generate_mesh(mesh_size=10.0)
        
        # 导出 MSH 格式
        output_file = tmp_path / "test_mesh.msh"
        result = engine.export_mesh(output_file, "msh")
        
        assert result is True
        assert output_file.exists()
        
        engine.finalize()

    def test_get_mesh_info(self, engine):
        """测试获取网格信息"""
        engine.initialize()
        engine.create_demo_geometry("block")
        engine.generate_mesh(mesh_size=10.0)
        
        info = engine.get_mesh_info()
        
        assert isinstance(info, dict)
        assert "nodes" in info
        assert "elements" in info
        
        engine.finalize()


class TestMeshResult:
    """测试 MeshResult 数据类"""

    def test_mesh_result_creation(self):
        """测试 MeshResult 创建"""
        from mechforge_work.mesh_engine import MeshResult
        
        result = MeshResult(
            success=True,
            nodes=1000,
            elements=5000,
            quality=0.85
        )
        
        assert result.success is True
        assert result.nodes == 1000
        assert result.elements == 5000
        assert result.quality == 0.85

    def test_mesh_result_failure(self):
        """测试失败的 MeshResult"""
        from mechforge_work.mesh_engine import MeshResult
        
        result = MeshResult(
            success=False,
            error="Test error"
        )
        
        assert result.success is False
        assert result.error == "Test error"


class TestGetEngine:
    """测试引擎获取函数"""

    def test_get_engine_singleton(self):
        """测试单例模式"""
        from mechforge_work.mesh_engine import get_engine, cleanup_engine
        
        cleanup_engine()
        
        engine1 = get_engine()
        engine2 = get_engine()
        
        assert engine1 is engine2
        
        cleanup_engine()

    def test_cleanup_engine(self):
        """测试清理引擎"""
        from mechforge_work.mesh_engine import get_engine, cleanup_engine
        
        engine = get_engine()
        cleanup_engine()
        
        # 清理后应该可以创建新实例
        new_engine = get_engine()
        assert new_engine is not None
        
        cleanup_engine()


# pytest 运行入口
if __name__ == "__main__":
    pytest.main([__file__, "-v"])