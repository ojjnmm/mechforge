"""
RAG 引擎模块 - 负责知识库检索
"""

from pathlib import Path
from typing import List, Optional


class RAGEngine:
    """RAG 搜索引擎"""

    def __init__(self, knowledge_path: Optional[Path] = None, top_k: int = 5):
        self.knowledge_path = knowledge_path
        self.top_k = top_k
        self._find_knowledge_path()

    def _find_knowledge_path(self) -> Optional[Path]:
        """查找知识库路径"""
        if self.knowledge_path and self.knowledge_path.exists():
            return self.knowledge_path

        # 搜索路径
        search_paths = [
            Path(__file__).parent.parent.parent / "knowledge",
            Path.home() / "knowledge",
            Path.cwd() / "knowledge",
        ]

        for path in search_paths:
            if path.exists() and list(path.glob("*.md")):
                self.knowledge_path = path
                return path
        return None

    @property
    def is_available(self) -> bool:
        """检查知识库是否可用"""
        return self.knowledge_path is not None

    @property
    def doc_count(self) -> int:
        """获取文档数量"""
        if not self.knowledge_path:
            return 0
        return len(list(self.knowledge_path.glob("*.md")))

    def check_trigger(self, user_input: str) -> bool:
        """检查是否触发 RAG"""
        triggers = [
            "知识库", "数据库", "搜索", "查一下", "帮我查",
            "请问", "根据", "参照", "按照", "rag", "手册",
            "标准", "规范", "材料", "螺栓", "轴承",
        ]
        return any(t in user_input.lower() for t in triggers)

    def search(self, query: str) -> str:
        """执行 RAG 搜索"""
        if not self.knowledge_path:
            return ""

        # 尝试向量搜索
        try:
            from ..knowledge.rag import search_with_chroma
            results = search_with_chroma(
                self.knowledge_path,
                query,
                top_k=self.top_k,
            )
            if results:
                self._print_results(results)
                return self._build_context(results)
        except Exception:
            pass

        # 回退到关键词搜索
        try:
            from ..knowledge.lookup import search_by_keyword
            results = search_by_keyword(self.knowledge_path, query, limit=3)
            if results:
                self._print_results_keyword(results)
                return self._build_context_keyword(results)
        except Exception as e:
            print(f"   知识库检索失败: {e}")

        return ""

    def _print_results(self, results: List[dict]):
        """打印搜索结果"""
        print(f"   找到 {len(results)} 条相关知识:")
        for i, r in enumerate(results, 1):
            score = r.get("score", 0)
            filled = int(score * 5)
            bar = "#" * filled + "-" * (5 - filled)
            title = r.get("title", "未知")[:28]
            print(f"   {i}. {title:<28} [{bar}]")

    def _print_results_keyword(self, results: List[dict]):
        """打印关键词搜索结果"""
        print(f"   找到 {len(results)} 条相关知识:")
        for i, r in enumerate(results, 1):
            score = r.get("score", 0)
            filled = min(int(score / 20), 5)
            bar = "#" * filled + "-" * (5 - filled)
            title = r.get("title", "未知")[:28]
            print(f"   {i}. {title:<28} [{bar}]")

    def _build_context(self, results: List[dict]) -> str:
        """构建上下文"""
        context = "\n\n【参考知识库】\n"
        for r in results:
            title = r.get("title", "未知")
            content = r.get("content", "")[:500]
            context += f"\n--- {title} ---\n{content}...\n"
        return context

    def _build_context_keyword(self, results: List[dict]) -> str:
        """构建关键词搜索上下文"""
        context = "\n\n【参考知识库】\n"
        for r in results:
            title = r.get("title", "未知")
            content = r.get("content_preview", "")[:500]
            context += f"\n--- {title} ---\n{content}...\n"
        return context
