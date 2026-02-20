"""
物种/分类群服务模块

提供物种搜索、详情获取等功能的封装
"""

from typing import List, Optional, Dict, Any, Union
from inaturalist_plugin.core.client import INaturalistClient
from inaturalist_plugin.models.taxon import Taxon, TaxonSummary


class TaxonService:
    """
    物种/分类群服务
    
    封装了与物种相关的所有 API 调用
    """
    
    def __init__(self, client: INaturalistClient):
        self.client = client
    
    def search(
        self,
        q: Optional[str] = None,
        taxon_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        rank: Optional[str] = None,
        min_rank: Optional[str] = None,
        max_rank: Optional[str] = None,
        iconic_taxa: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        per_page: int = 30,
        page: int = 1
    ) -> List[Taxon]:
        """
        搜索物种/分类群
        
        Args:
            q: 搜索关键词（支持学名或俗名）
            taxon_id: 特定物种 ID
            parent_id: 父分类群 ID（获取该分类群下的所有子类群）
            rank: 分类等级 (species, genus, family 等)
            min_rank: 最小分类等级
            max_rank: 最大分类等级
            iconic_taxa: 标志性类群列表 [Plantae, Animalia, Fungi 等]
            is_active: 是否只返回活跃的分类群
            per_page: 每页数量 (1-200)
            page: 页码
            
        Returns:
            Taxon 对象列表
            
        Example:
            >>> service.search(q="红嘴相思鸟")
            >>> service.search(q="Pica pica", rank="species")
            >>> service.search(parent_id=3, rank="species")  # 获取鸟类下的所有物种
        """
        params = {
            "per_page": min(per_page, 200),
            "page": page
        }
        
        if q:
            params["q"] = q
        if taxon_id:
            params["id"] = taxon_id
        if parent_id:
            params["parent_id"] = parent_id
        if rank:
            params["rank"] = rank
        if min_rank:
            params["min_rank"] = min_rank
        if max_rank:
            params["max_rank"] = max_rank
        if iconic_taxa:
            params["iconic_taxa"] = ",".join(iconic_taxa)
        if is_active is not None:
            params["is_active"] = "true" if is_active else "false"
        
        response = self.client.get("/taxa", params)
        results = response.get("results", [])
        
        return [Taxon.from_api(data) for data in results]
    
    def autocomplete(
        self,
        q: str,
        per_page: int = 10,
        min_rank: Optional[str] = None,
        rank: Optional[str] = None
    ) -> List[Taxon]:
        """
        自动补全搜索
        
        用于搜索建议功能，返回与查询最匹配的物种
        
        Args:
            q: 搜索关键词（至少输入2个字符）
            per_page: 返回结果数量
            min_rank: 最小分类等级
            rank: 特定分类等级
            
        Returns:
            Taxon 对象列表
            
        Example:
            >>> service.autocomplete("ma")
            >>> service.autocomplete("ma", rank="species")
        """
        params = {
            "q": q,
            "per_page": min(per_page, 200)
        }
        
        if min_rank:
            params["min_rank"] = min_rank
        if rank:
            params["rank"] = rank
        
        response = self.client.get("/taxa/autocomplete", params)
        results = response.get("results", [])
        
        return [Taxon.from_api(data) for data in results]
    
    def get_by_id(self, taxon_id: int) -> Optional[Taxon]:
        """
        获取特定物种的详细信息
        
        Args:
            taxon_id: 物种 ID
            
        Returns:
            Taxon 对象，如果不存在则返回 None
            
        Example:
            >>> service.get_by_id(9083)  # 获取喜鹊的详细信息
        """
        try:
            response = self.client.get(f"/taxa/{taxon_id}")
            results = response.get("results", [])
            if results:
                return Taxon.from_api(results[0])
            return None
        except Exception:
            return None
    
    def get_by_name(self, scientific_name: str) -> Optional[Taxon]:
        """
        通过学名获取物种
        
        Args:
            scientific_name: 学名（拉丁名）
            
        Returns:
            Taxon 对象，如果不存在则返回 None
        """
        results = self.search(q=scientific_name, per_page=5)
        for taxon in results:
            if taxon.name.lower() == scientific_name.lower():
                return taxon
        return results[0] if results else None
    
    def get_children(self, parent_id: int, rank: Optional[str] = None) -> List[Taxon]:
        """
        获取子分类群
        
        Args:
            parent_id: 父分类群 ID
            rank: 可选，筛选特定等级
            
        Returns:
            Taxon 对象列表
        """
        return self.search(parent_id=parent_id, rank=rank, per_page=200)
    
    def get_ancestors(self, taxon_id: int) -> List[Taxon]:
        """
        获取物种的祖先分类群
        
        Args:
            taxon_id: 物种 ID
            
        Returns:
            从界到该物种的所有祖先分类群列表
        """
        taxon = self.get_by_id(taxon_id)
        if not taxon or not taxon.ancestor_ids:
            return []
        
        ancestors = []
        for ancestor_id in taxon.ancestor_ids:
            ancestor = self.get_by_id(ancestor_id)
            if ancestor:
                ancestors.append(ancestor)
        
        return ancestors
    
    def get_observation_count(
        self,
        taxon_id: int,
        place_id: Optional[int] = None,
        quality_grade: Optional[str] = None
    ) -> int:
        """
        获取物种的观察记录数量
        
        Args:
            taxon_id: 物种 ID
            place_id: 可选，特定地点
            quality_grade: 可选，质量等级 (research, needs_id, casual)
            
        Returns:
            观察记录数量
        """
        from inaturalist_plugin.services.observation_service import ObservationService
        obs_service = ObservationService(self.client)
        return obs_service.count(taxon_id=taxon_id, place_id=place_id, quality_grade=quality_grade)
    
    def get_observations(
        self,
        taxon_id: int,
        quality_grade: Optional[str] = None,
        photos_only: bool = True,
        per_page: int = 200,
        max_results: Optional[int] = None
    ) -> List[Any]:  # 返回 Observation 列表，但避免循环导入
        """
        获取物种的观察记录
        
        Args:
            taxon_id: 物种 ID
            quality_grade: 质量等级筛选
            photos_only: 是否只返回有照片的观察
            per_page: 每页数量
            max_results: 最大结果数
            
        Returns:
            Observation 对象列表
        """
        from inaturalist_plugin.services.observation_service import ObservationService
        obs_service = ObservationService(self.client)
        
        params = {"taxon_id": taxon_id}
        if quality_grade:
            params["quality_grade"] = quality_grade
        if photos_only:
            params["photos"] = "true"
        
        return obs_service.search(**params, per_page=per_page, max_results=max_results)
    
    def get_iconic_taxa(self) -> List[Taxon]:
        """
        获取标志性分类群列表
        
        包括: Animalia, Plantae, Fungi, 等
        
        Returns:
            Taxon 对象列表
        """
        response = self.client.get("/taxa", params={"rank": "kingdom", "per_page": 50})
        results = response.get("results", [])
        return [Taxon.from_api(data) for data in results]


# 便捷函数
def search_species(query: str, per_page: int = 30) -> List[Taxon]:
    """
    便捷函数：搜索物种
    
    Args:
        query: 搜索关键词
        per_page: 返回数量
        
    Returns:
        Taxon 对象列表
    """
    from inaturalist_plugin.core.client import create_client
    client = create_client()
    service = TaxonService(client)
    return service.search(q=query, per_page=per_page)


def get_species(taxon_id: int) -> Optional[Taxon]:
    """
    便捷函数：获取物种详情
    
    Args:
        taxon_id: 物种 ID
        
    Returns:
        Taxon 对象
    """
    from inaturalist_plugin.core.client import create_client
    client = create_client()
    service = TaxonService(client)
    return service.get_by_id(taxon_id)
