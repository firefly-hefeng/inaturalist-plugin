"""
观察记录服务模块

提供观察记录搜索、详情获取等功能的封装
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from inaturalist_plugin.core.client import INaturalistClient
from inaturalist_plugin.models.observation import Observation, ObservationStats


class ObservationService:
    """
    观察记录服务
    
    封装了与观察记录相关的所有 API 调用
    """
    
    def __init__(self, client: INaturalistClient):
        self.client = client
    
    def search(
        self,
        # 分类群筛选
        taxon_id: Optional[int] = None,
        taxon_name: Optional[str] = None,
        iconic_taxa: Optional[List[str]] = None,
        
        # 地点筛选
        place_id: Optional[int] = None,
        swlat: Optional[float] = None,
        swlng: Optional[float] = None,
        nelat: Optional[float] = None,
        nelng: Optional[float] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius: Optional[float] = None,  # 公里
        
        # 时间筛选
        observed_on: Optional[str] = None,  # YYYY-MM-DD
        observed_d1: Optional[str] = None,
        observed_d2: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        
        # 质量与状态
        quality_grade: Optional[str] = None,  # research, needs_id, casual
        geoprivacy: Optional[str] = None,  # open, obscured, private
        
        # 特征筛选
        has_photos: bool = False,
        has_sounds: bool = False,
        has_geo: bool = False,
        
        # 用户筛选
        user_id: Optional[int] = None,
        user_login: Optional[str] = None,
        
        # 项目
        project_id: Optional[int] = None,
        
        # 标识符
        identified: Optional[bool] = None,
        
        # 排序与分页
        order_by: Optional[str] = None,  # observed_on, created_at
        order: str = "desc",
        per_page: int = 30,
        page: int = 1,
        
        # 额外数据
        include_new_projects: bool = False,
        
        # 其他
        **kwargs
    ) -> List[Observation]:
        """
        搜索观察记录
        
        这是 iNaturalist API 中最强大的端点之一，支持丰富的筛选条件
        
        Args:
            taxon_id: 物种/分类群 ID
            taxon_name: 物种名称
            iconic_taxa: 标志性类群列表 [Plantae, Animalia, Fungi, ...]
            place_id: 地点 ID
            swlat, swlng, nelat, nelng: 边界框坐标
            lat, lng, radius: 圆形搜索
            observed_on: 观察日期 (YYYY-MM-DD)
            observed_d1, observed_d2: 日期范围
            year, month, day: 特定年月日
            quality_grade: 质量等级 (research, needs_id, casual)
            geoprivacy: 地理位置隐私
            has_photos: 是否有照片
            has_sounds: 是否有声音
            has_geo: 是否有地理坐标
            user_id: 用户 ID
            user_login: 用户名
            project_id: 项目 ID
            order_by: 排序字段
            order: 排序方向 (asc/desc)
            per_page: 每页数量 (1-200)
            page: 页码
            
        Returns:
            Observation 对象列表
            
        Example:
            >>> service.search(taxon_id=9083, quality_grade="research")
            >>> service.search(lat=39.9, lng=116.4, radius=10, has_photos=True)
            >>> service.search(iconic_taxa=["Aves"], quality_grade="research")
        """
        params = {
            "per_page": min(per_page, 200),
            "page": page,
            "order": order
        }
        
        # 分类群
        if taxon_id:
            params["taxon_id"] = taxon_id
        if taxon_name:
            params["taxon_name"] = taxon_name
        if iconic_taxa:
            params["iconic_taxa"] = ",".join(iconic_taxa)
        
        # 地点
        if place_id:
            params["place_id"] = place_id
        if swlat is not None:
            params["swlat"] = swlat
            params["swlng"] = swlng
            params["nelat"] = nelat
            params["nelng"] = nelng
        if lat is not None and lng is not None:
            params["lat"] = lat
            params["lng"] = lng
        if radius:
            params["radius"] = radius
        
        # 时间
        if observed_on:
            params["observed_on"] = observed_on
        if observed_d1:
            params["d1"] = observed_d1
        if observed_d2:
            params["d2"] = observed_d2
        if year:
            params["year"] = year
        if month:
            params["month"] = month
        if day:
            params["day"] = day
        
        # 质量与状态
        if quality_grade:
            params["quality_grade"] = quality_grade
        if geoprivacy:
            params["geoprivacy"] = geoprivacy
        
        # 特征
        if has_photos:
            params["photos"] = "true"
        if has_sounds:
            params["sounds"] = "true"
        if has_geo:
            params["geo"] = "true"
        
        # 用户
        if user_id:
            params["user_id"] = user_id
        if user_login:
            params["user_login"] = user_login
        
        # 项目
        if project_id:
            params["project_id"] = project_id
        
        # 标识状态
        if identified is not None:
            params["identified"] = "true" if identified else "false"
        
        # 排序
        if order_by:
            params["order_by"] = order_by
        
        # 额外参数
        params.update(kwargs)
        
        response = self.client.get("/observations", params)
        results = response.get("results", [])
        
        return [Observation.from_api(data) for data in results]
    
    def get_by_id(
        self,
        observation_id: int,
        include_new_projects: bool = False
    ) -> Optional[Observation]:
        """
        获取单个观察记录的详细信息
        
        Args:
            observation_id: 观察记录 ID
            include_new_projects: 是否包含新项目信息
            
        Returns:
            Observation 对象
        """
        params = {}
        if include_new_projects:
            params["include_new_projects"] = "true"
        
        try:
            response = self.client.get(f"/observations/{observation_id}", params)
            results = response.get("results", [])
            if results:
                return Observation.from_api(results[0])
            return None
        except Exception:
            return None
    
    def search_all(
        self,
        max_results: int = 1000,
        **kwargs
    ) -> List[Observation]:
        """
        搜索所有符合条件的观察记录（自动分页）
        
        Args:
            max_results: 最大结果数
            **kwargs: 其他搜索参数（同 search 方法）
            
        Returns:
            Observation 对象列表
        """
        all_observations = []
        page = 1
        per_page = min(kwargs.get("per_page", 200), 200)
        
        while len(all_observations) < max_results:
            kwargs["page"] = page
            kwargs["per_page"] = per_page
            
            observations = self.search(**kwargs)
            
            if not observations:
                break
            
            all_observations.extend(observations)
            
            if len(observations) < per_page:
                break
            
            page += 1
        
        return all_observations[:max_results]
    
    def count(
        self,
        taxon_id: Optional[int] = None,
        place_id: Optional[int] = None,
        user_id: Optional[int] = None,
        quality_grade: Optional[str] = None,
        **kwargs
    ) -> int:
        """
        获取符合条件的观察记录数量
        
        Args:
            taxon_id: 物种 ID
            place_id: 地点 ID
            user_id: 用户 ID
            quality_grade: 质量等级
            **kwargs: 其他筛选条件
            
        Returns:
            观察记录数量
        """
        params = {"per_page": 0}  # 不返回结果，只返回总数
        
        if taxon_id:
            params["taxon_id"] = taxon_id
        if place_id:
            params["place_id"] = place_id
        if user_id:
            params["user_id"] = user_id
        if quality_grade:
            params["quality_grade"] = quality_grade
        
        params.update(kwargs)
        
        response = self.client.get("/observations", params)
        return response.get("total_results", 0)
    
    def get_species_counts(
        self,
        place_id: Optional[int] = None,
        taxon_id: Optional[int] = None,
        user_id: Optional[int] = None,
        project_id: Optional[int] = None,
        observed_d1: Optional[str] = None,
        observed_d2: Optional[str] = None,
        hrank: Optional[str] = None,  # 最高等级
        lrank: Optional[str] = None,  # 最低等级
    ) -> List[Dict[str, Any]]:
        """
        获取物种统计
        
        返回符合条件的观察记录中，每个物种的观察次数
        
        Args:
            place_id: 地点 ID
            taxon_id: 分类群 ID
            user_id: 用户 ID
            project_id: 项目 ID
            observed_d1, observed_d2: 日期范围
            hrank: 最高分类等级
            lrank: 最低分类等级
            
        Returns:
            包含物种和计数的字典列表
            [{"count": 10, "taxon": {...}}, ...]
        """
        params = {}
        
        if place_id:
            params["place_id"] = place_id
        if taxon_id:
            params["taxon_id"] = taxon_id
        if user_id:
            params["user_id"] = user_id
        if project_id:
            params["project_id"] = project_id
        if observed_d1:
            params["d1"] = observed_d1
        if observed_d2:
            params["d2"] = observed_d2
        if hrank:
            params["hrank"] = hrank
        if lrank:
            params["lrank"] = lrank
        
        response = self.client.get("/observations/species_counts", params)
        return response.get("results", [])
    
    def get_identifiers(
        self,
        place_id: Optional[int] = None,
        taxon_id: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取鉴定者统计
        
        返回在指定条件下进行鉴定的用户统计
        
        Args:
            place_id: 地点 ID
            taxon_id: 分类群 ID
            
        Returns:
            鉴定者统计列表
        """
        params = {}
        
        if place_id:
            params["place_id"] = place_id
        if taxon_id:
            params["taxon_id"] = taxon_id
        
        params.update(kwargs)
        
        response = self.client.get("/observations/identifiers", params)
        return response.get("results", [])
    
    def get_observers(
        self,
        place_id: Optional[int] = None,
        taxon_id: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取观察者统计
        
        返回在指定条件下进行观察的用户统计
        
        Args:
            place_id: 地点 ID
            taxon_id: 分类群 ID
            
        Returns:
            观察者统计列表
        """
        params = {}
        
        if place_id:
            params["place_id"] = place_id
        if taxon_id:
            params["taxon_id"] = taxon_id
        
        params.update(kwargs)
        
        response = self.client.get("/observations/observers", params)
        return response.get("results", [])
    
    def get_histogram(
        self,
        interval: str = "month",
        taxon_id: Optional[int] = None,
        place_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取观察记录的时间分布直方图
        
        Args:
            interval: 时间间隔 (month, week, day, hour)
            taxon_id: 物种 ID
            place_id: 地点 ID
            
        Returns:
            时间分布数据
        """
        params = {"interval": interval}
        
        if taxon_id:
            params["taxon_id"] = taxon_id
        if place_id:
            params["place_id"] = place_id
        
        params.update(kwargs)
        
        return self.client.get("/observations/histogram", params)
    
    def get_popular(
        self,
        place_id: Optional[int] = None,
        taxon_id: Optional[int] = None,
        per_page: int = 10
    ) -> List[Observation]:
        """
        获取最受欢迎的观察记录
        
        根据点赞数、评论数等综合排序
        
        Args:
            place_id: 地点 ID
            taxon_id: 物种 ID
            per_page: 返回数量
            
        Returns:
            Observation 对象列表
        """
        return self.search(
            place_id=place_id,
            taxon_id=taxon_id,
            has_photos=True,
            order_by="votes",
            order="desc",
            per_page=per_page
        )
    
    def get_latest(
        self,
        taxon_id: Optional[int] = None,
        place_id: Optional[int] = None,
        quality_grade: str = "research",
        per_page: int = 30
    ) -> List[Observation]:
        """
        获取最新的观察记录
        
        Args:
            taxon_id: 物种 ID
            place_id: 地点 ID
            quality_grade: 质量等级
            per_page: 返回数量
            
        Returns:
            Observation 对象列表
        """
        return self.search(
            taxon_id=taxon_id,
            place_id=place_id,
            quality_grade=quality_grade,
            has_photos=True,
            order_by="observed_on",
            order="desc",
            per_page=per_page
        )


# 便捷函数
def search_observations(**kwargs) -> List[Observation]:
    """
    便捷函数：搜索观察记录
    
    Example:
        >>> search_observations(taxon_id=9083, quality_grade="research")
    """
    from inaturalist_plugin.core.client import create_client
    client = create_client()
    service = ObservationService(client)
    return service.search(**kwargs)


def get_observation(observation_id: int) -> Optional[Observation]:
    """
    便捷函数：获取观察记录详情
    
    Example:
        >>> get_observation(12345)
    """
    from inaturalist_plugin.core.client import create_client
    client = create_client()
    service = ObservationService(client)
    return service.get_by_id(observation_id)
