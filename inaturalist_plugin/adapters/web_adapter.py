"""
Web 适配器模块

用于将 iNaturalist 插件集成到自然科学查询门户网站
支持 Flask, FastAPI, Django 等主流 Web 框架
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import asdict
import json

from inaturalist_plugin.core.client import INaturalistClient, create_client
from inaturalist_plugin.services.taxon_service import TaxonService
from inaturalist_plugin.services.observation_service import ObservationService
from inaturalist_plugin.utils.image_utils import ImageDownloader, ImageSizeHelper


class JSONEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，支持 dataclass"""
    def default(self, obj):
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        return super().default(obj)


class INaturalistWebAdapter:
    """
    iNaturalist Web 适配器
    
    为门户网站提供统一的 API 接口
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = create_client(api_key=api_key)
        self.taxon_service = TaxonService(self.client)
        self.observation_service = ObservationService(self.client)
        self.image_downloader = ImageDownloader()
    
    # ==================== 物种查询接口 ====================
    
    def search_species(
        self,
        query: str,
        rank: Optional[str] = None,
        iconic_taxa: Optional[List[str]] = None,
        per_page: int = 30
    ) -> Dict[str, Any]:
        """
        搜索物种
        
        Returns:
            {
                "success": True,
                "total": 100,
                "results": [Taxon, ...]
            }
        """
        try:
            results = self.taxon_service.search(
                q=query,
                rank=rank,
                iconic_taxa=iconic_taxa,
                per_page=per_page
            )
            
            return {
                "success": True,
                "query": query,
                "total": len(results),
                "results": [self._serialize_taxon(t) for t in results]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_species_detail(self, taxon_id: int) -> Dict[str, Any]:
        """
        获取物种详细信息
        
        Returns:
            {
                "success": True,
                "taxon": Taxon,
                "observation_count": 100,
                "ancestors": [Taxon, ...],
                "children": [Taxon, ...]
            }
        """
        try:
            taxon = self.taxon_service.get_by_id(taxon_id)
            
            if not taxon:
                return {
                    "success": False,
                    "error": f"Species not found: {taxon_id}"
                }
            
            # 获取额外信息
            observation_count = self.taxon_service.get_observation_count(taxon_id)
            ancestors = self.taxon_service.get_ancestors(taxon_id)
            children = self.taxon_service.get_children(taxon_id)
            
            # 获取最近的观察记录
            recent_observations = self.observation_service.search(
                taxon_id=taxon_id,
                quality_grade="research",
                has_photos=True,
                per_page=6
            )
            
            return {
                "success": True,
                "taxon": self._serialize_taxon(taxon),
                "observation_count": observation_count,
                "ancestors": [self._serialize_taxon(t) for t in ancestors],
                "children": [self._serialize_taxon(t) for t in children],
                "recent_observations": [self._serialize_observation(o) for o in recent_observations]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def autocomplete_species(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """
        物种自动补全
        
        Returns:
            {
                "success": True,
                "suggestions": [Taxon, ...]
            }
        """
        try:
            results = self.taxon_service.autocomplete(q=query, per_page=per_page)
            
            return {
                "success": True,
                "query": query,
                "suggestions": [self._serialize_taxon(t) for t in results]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== 观察记录接口 ====================
    
    def search_observations(
        self,
        taxon_id: Optional[int] = None,
        place_id: Optional[int] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius: Optional[float] = None,
        quality_grade: Optional[str] = "research",
        has_photos: bool = True,
        per_page: int = 30,
        **kwargs
    ) -> Dict[str, Any]:
        """
        搜索观察记录
        
        Returns:
            {
                "success": True,
                "total": 100,
                "results": [Observation, ...]
            }
        """
        try:
            results = self.observation_service.search(
                taxon_id=taxon_id,
                place_id=place_id,
                lat=lat,
                lng=lng,
                radius=radius,
                quality_grade=quality_grade,
                has_photos=has_photos,
                per_page=per_page,
                **kwargs
            )
            
            return {
                "success": True,
                "total": len(results),
                "results": [self._serialize_observation(o) for o in results]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_observation_detail(self, observation_id: int) -> Dict[str, Any]:
        """
        获取观察记录详情
        
        Returns:
            {
                "success": True,
                "observation": Observation
            }
        """
        try:
            observation = self.observation_service.get_by_id(observation_id)
            
            if not observation:
                return {
                    "success": False,
                    "error": f"Observation not found: {observation_id}"
                }
            
            return {
                "success": True,
                "observation": self._serialize_observation(observation)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_species_by_location(
        self,
        lat: float,
        lng: float,
        radius: float = 10,
        per_page: int = 30
    ) -> Dict[str, Any]:
        """
        获取特定位置周围的物种列表
        
        Returns:
            {
                "success": True,
                "location": {"lat": ..., "lng": ..., "radius": ...},
                "species": [TaxonSummary, ...]
            }
        """
        try:
            species_counts = self.observation_service.get_species_counts(
                lat=lat,
                lng=lng,
                radius=radius
            )
            
            # 限制数量
            species_counts = species_counts[:per_page]
            
            return {
                "success": True,
                "location": {
                    "lat": lat,
                    "lng": lng,
                    "radius": radius
                },
                "species": [
                    {
                        "count": sc["count"],
                        "taxon": self._serialize_taxon_simple(sc["taxon"])
                    }
                    for sc in species_counts
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== 图片接口 ====================
    
    def get_species_images(
        self,
        taxon_id: int,
        size: str = "medium",
        max_images: int = 10
    ) -> Dict[str, Any]:
        """
        获取物种图片
        
        Returns:
            {
                "success": True,
                "taxon_id": 123,
                "images": [
                    {
                        "url": "...",
                        "attribution": "...",
                        "license": "CC-BY"
                    },
                    ...
                ]
            }
        """
        try:
            # 获取研究级观察记录的图片
            observations = self.observation_service.search(
                taxon_id=taxon_id,
                quality_grade="research",
                has_photos=True,
                per_page=max_images
            )
            
            images = []
            for obs in observations:
                for photo in obs.photos[:3]:  # 每个观察最多取3张
                    if len(images) >= max_images:
                        break
                    
                    url = getattr(photo, f"{size}_url", None) or photo.url
                    images.append({
                        "url": url,
                        "observation_id": obs.id,
                        "attribution": photo.attribution,
                        "license": photo.license_code,
                        "square": photo.square_url,
                        "medium": photo.medium_url,
                        "large": photo.large_url
                    })
                
                if len(images) >= max_images:
                    break
            
            return {
                "success": True,
                "taxon_id": taxon_id,
                "size": size,
                "total": len(images),
                "images": images
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== 工具方法 ====================
    
    def _serialize_taxon(self, taxon) -> Dict[str, Any]:
        """序列化 Taxon 对象为字典"""
        return {
            "id": taxon.id,
            "name": taxon.name,
            "rank": taxon.rank,
            "display_name": taxon.display_name,
            "common_names": {
                "english": taxon.english_common_name,
                "chinese": taxon.chinese_common_name,
                "preferred": taxon.preferred_common_name
            },
            "iconic_taxon": taxon.iconic_taxon_name,
            "observations_count": taxon.observations_count,
            "conservation_status": taxon.conservation_status_name,
            "photos": [
                {
                    "square": p.square_url,
                    "medium": p.medium_url,
                    "large": p.large_url,
                    "attribution": p.attribution,
                    "license": p.license_code
                }
                for p in taxon.taxon_photos[:5]  # 最多5张
            ] if taxon.taxon_photos else [],
            "default_photo": {
                "square": taxon.default_photo.square_url if taxon.default_photo else None,
                "medium": taxon.default_photo.medium_url if taxon.default_photo else None,
                "large": taxon.default_photo.large_url if taxon.default_photo else None
            },
            "wikipedia": {
                "summary": taxon.wikipedia_summary,
                "url": taxon.wikipedia_url
            }
        }
    
    def _serialize_taxon_simple(self, taxon_data: Dict) -> Dict[str, Any]:
        """简化版 Taxon 序列化"""
        return {
            "id": taxon_data.get("id"),
            "name": taxon_data.get("name"),
            "rank": taxon_data.get("rank"),
            "preferred_common_name": taxon_data.get("preferred_common_name"),
            "iconic_taxon_name": taxon_data.get("iconic_taxon_name"),
            "default_photo_url": taxon_data.get("default_photo", {}).get("square_url") if taxon_data.get("default_photo") else None
        }
    
    def _serialize_observation(self, observation) -> Dict[str, Any]:
        """序列化 Observation 对象为字典"""
        return {
            "id": observation.id,
            "uuid": observation.uuid,
            "quality_grade": observation.quality_grade,
            "species_guess": observation.species_guess,
            "taxon": {
                "id": observation.taxon_id,
                "name": observation.taxon_name,
                "rank": observation.taxon_rank
            } if observation.taxon_id else None,
            "observed_on": observation.observed_on,
            "location": {
                "latitude": observation.latitude,
                "longitude": observation.longitude,
                "place_guess": observation.place_guess,
                "accuracy": observation.positional_accuracy
            },
            "photos": [
                {
                    "id": p.id,
                    "square": p.square_url,
                    "medium": p.medium_url,
                    "large": p.large_url,
                    "attribution": p.attribution
                }
                for p in observation.photos
            ],
            "user": {
                "id": observation.user_id,
                "login": observation.user_login,
                "name": observation.user.name if observation.user else None
            } if observation.user else None,
            "url": observation.url,
            "description": observation.description
        }


# ==================== Flask 集成示例 ====================

def create_flask_routes(app, adapter: INaturalistWebAdapter):
    """
    为 Flask 应用创建路由
    
    Example:
        from flask import Flask
        app = Flask(__name__)
        adapter = INaturalistWebAdapter()
        create_flask_routes(app, adapter)
    """
    from flask import request, jsonify
    
    @app.route("/api/inat/species/search")
    def api_search_species():
        query = request.args.get("q", "")
        rank = request.args.get("rank")
        iconic_taxa = request.args.getlist("iconic_taxa")
        per_page = int(request.args.get("per_page", 30))
        
        result = adapter.search_species(
            query=query,
            rank=rank,
            iconica_taxa=iconic_taxa or None,
            per_page=per_page
        )
        return jsonify(result)
    
    @app.route("/api/inat/species/<int:taxon_id>")
    def api_get_species(taxon_id):
        result = adapter.get_species_detail(taxon_id)
        return jsonify(result)
    
    @app.route("/api/inat/species/autocomplete")
    def api_autocomplete_species():
        query = request.args.get("q", "")
        per_page = int(request.args.get("per_page", 10))
        result = adapter.autocomplete_species(query, per_page)
        return jsonify(result)
    
    @app.route("/api/inat/species/<int:taxon_id>/images")
    def api_get_species_images(taxon_id):
        size = request.args.get("size", "medium")
        max_images = int(request.args.get("max", 10))
        result = adapter.get_species_images(taxon_id, size, max_images)
        return jsonify(result)
    
    @app.route("/api/inat/observations")
    def api_search_observations():
        taxon_id = request.args.get("taxon_id", type=int)
        place_id = request.args.get("place_id", type=int)
        lat = request.args.get("lat", type=float)
        lng = request.args.get("lng", type=float)
        radius = request.args.get("radius", type=float)
        quality_grade = request.args.get("quality_grade", "research")
        per_page = int(request.args.get("per_page", 30))
        
        result = adapter.search_observations(
            taxon_id=taxon_id,
            place_id=place_id,
            lat=lat,
            lng=lng,
            radius=radius,
            quality_grade=quality_grade,
            per_page=per_page
        )
        return jsonify(result)
    
    @app.route("/api/inat/observations/<int:observation_id>")
    def api_get_observation(observation_id):
        result = adapter.get_observation_detail(observation_id)
        return jsonify(result)
    
    @app.route("/api/inat/location/species")
    def api_get_species_by_location():
        lat = float(request.args.get("lat", 0))
        lng = float(request.args.get("lng", 0))
        radius = float(request.args.get("radius", 10))
        per_page = int(request.args.get("per_page", 30))
        
        result = adapter.get_species_by_location(lat, lng, radius, per_page)
        return jsonify(result)


# ==================== FastAPI 集成示例 ====================

def create_fastapi_routes(adapter: INaturalistWebAdapter):
    """
    为 FastAPI 应用创建路由
    
    Example:
        from fastapi import FastAPI
        app = FastAPI()
        adapter = INaturalistWebAdapter()
        create_fastapi_routes(adapter)
    """
    try:
        from fastapi import APIRouter, Query
        from typing import List
        
        router = APIRouter(prefix="/api/inat", tags=["iNaturalist"])
        
        @router.get("/species/search")
        async def search_species(
            q: str = Query(..., description="Search query"),
            rank: Optional[str] = None,
            iconic_taxa: Optional[List[str]] = Query(None),
            per_page: int = 30
        ):
            return adapter.search_species(q, rank, iconic_taxa, per_page)
        
        @router.get("/species/{taxon_id}")
        async def get_species(taxon_id: int):
            return adapter.get_species_detail(taxon_id)
        
        @router.get("/species/autocomplete")
        async def autocomplete_species(
            q: str = Query(..., min_length=2),
            per_page: int = 10
        ):
            return adapter.autocomplete_species(q, per_page)
        
        @router.get("/species/{taxon_id}/images")
        async def get_species_images(
            taxon_id: int,
            size: str = "medium",
            max_images: int = 10
        ):
            return adapter.get_species_images(taxon_id, size, max_images)
        
        @router.get("/observations")
        async def search_observations(
            taxon_id: Optional[int] = None,
            place_id: Optional[int] = None,
            lat: Optional[float] = None,
            lng: Optional[float] = None,
            radius: Optional[float] = None,
            quality_grade: str = "research",
            per_page: int = 30
        ):
            return adapter.search_observations(
                taxon_id, place_id, lat, lng, radius, quality_grade, True, per_page
            )
        
        @router.get("/observations/{observation_id}")
        async def get_observation(observation_id: int):
            return adapter.get_observation_detail(observation_id)
        
        @router.get("/location/species")
        async def get_species_by_location(
            lat: float,
            lng: float,
            radius: float = 10,
            per_page: int = 30
        ):
            return adapter.get_species_by_location(lat, lng, radius, per_page)
        
        return router
    except ImportError:
        print("FastAPI not installed")
        return None
