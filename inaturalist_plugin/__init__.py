"""
iNaturalist 数据插件

一个用于获取 iNaturalist 物种详细信息和图片的 Python 插件
适配自然科学查询门户网站

主要功能:
- 物种搜索和详细信息获取
- 观察记录查询
- 图片下载和处理
- Web 框架集成

示例:
    >>> from inaturalist_plugin import INaturalistPlugin
    >>> plugin = INaturalistPlugin()
    >>> species = plugin.search_species("喜鹊")
    >>> details = plugin.get_species_detail(8318)  # 喜鹊属 Pica
"""

__version__ = "1.0.0"
__author__ = "Nature Portal"

# 导入 typing 类型
from typing import List, Optional, Dict, Any

from inaturalist_plugin.core.client import (
    INaturalistClient,
    APIConfig,
    create_client,
    INaturalistAPIError
)

from inaturalist_plugin.models.taxon import (
    Taxon,
    TaxonPhoto,
    TaxonName,
    ConservationStatusInfo,
    EstablishmentMeansInfo,
    TaxonSummary
)

from inaturalist_plugin.models.observation import (
    Observation,
    ObservationPhoto,
    Identification,
    User,
    QualityGrade,
    Geoprivacy
)

from inaturalist_plugin.services.taxon_service import (
    TaxonService,
    search_species,
    get_species
)

from inaturalist_plugin.services.observation_service import (
    ObservationService,
    search_observations,
    get_observation
)

from inaturalist_plugin.utils.image_utils import (
    ImageDownloader,
    ImageSizeHelper,
    download_species_photos,
    download_observation_photos
)

from inaturalist_plugin.adapters.web_adapter import (
    INaturalistWebAdapter,
    create_flask_routes,
    create_fastapi_routes
)


class INaturalistPlugin:
    """
    iNaturalist 插件主类
    
    提供简洁的 API 接口，方便集成到各种应用中
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化插件
        
        Args:
            api_key: 可选的 API 密钥（用于需要认证的接口）
        """
        from inaturalist_plugin.core.client import create_client
        
        self.client = create_client(api_key=api_key)
        self.taxon_service = TaxonService(self.client)
        self.observation_service = ObservationService(self.client)
        self.image_downloader = ImageDownloader()
    
    # ============= 物种接口 =============
    
    def search_species(
        self,
        query: str,
        rank: Optional[str] = None,
        per_page: int = 30
    ) -> List[Taxon]:
        """
        搜索物种
        
        Args:
            query: 搜索关键词（支持中文、英文、学名）
            rank: 分类等级筛选 (species, genus, family 等)
            per_page: 返回数量
            
        Returns:
            Taxon 对象列表
        """
        return self.taxon_service.search(q=query, rank=rank, per_page=per_page)
    
    def get_species_detail(self, taxon_id: int) -> Optional[Taxon]:
        """
        获取物种详细信息
        
        Args:
            taxon_id: 物种 ID
            
        Returns:
            Taxon 对象
        """
        return self.taxon_service.get_by_id(taxon_id)
    
    def autocomplete_species(self, query: str, per_page: int = 10) -> List[Taxon]:
        """
        物种自动补全
        
        Args:
            query: 搜索关键词（至少2个字符）
            per_page: 返回数量
            
        Returns:
            Taxon 对象列表
        """
        return self.taxon_service.autocomplete(q=query, per_page=per_page)
    
    # ============= 观察记录接口 =============
    
    def search_observations(
        self,
        taxon_id: Optional[int] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius: Optional[float] = None,
        quality_grade: str = "research",
        has_photos: bool = True,
        per_page: int = 30
    ) -> List[Observation]:
        """
        搜索观察记录
        
        Args:
            taxon_id: 物种 ID
            lat, lng: 中心坐标
            radius: 搜索半径（公里）
            quality_grade: 质量等级
            has_photos: 是否只返回有照片的
            per_page: 返回数量
            
        Returns:
            Observation 对象列表
        """
        return self.observation_service.search(
            taxon_id=taxon_id,
            lat=lat,
            lng=lng,
            radius=radius,
            quality_grade=quality_grade,
            has_photos=has_photos,
            per_page=per_page
        )
    
    def get_observation(self, observation_id: int) -> Optional[Observation]:
        """
        获取观察记录详情
        
        Args:
            observation_id: 观察记录 ID
            
        Returns:
            Observation 对象
        """
        return self.observation_service.get_by_id(observation_id)
    
    # ============= 图片接口 =============
    
    def download_species_images(
        self,
        taxon_id: int,
        size: str = "medium",
        max_images: int = 10
    ) -> List[str]:
        """
        下载物种图片
        
        Args:
            taxon_id: 物种 ID
            size: 图片尺寸 (square, thumb, small, medium, large)
            max_images: 最大下载数量
            
        Returns:
            下载成功的本地文件路径列表
        """
        # 先获取观察记录
        observations = self.observation_service.search(
            taxon_id=taxon_id,
            quality_grade="research",
            has_photos=True,
            per_page=max_images
        )
        
        downloaded = []
        for obs in observations:
            urls = obs.get_photo_urls(size)
            for url in urls:
                if len(downloaded) >= max_images:
                    break
                local_path = self.image_downloader.download(url)
                if local_path:
                    downloaded.append(local_path)
        
        return downloaded
    
    def get_species_image_urls(
        self,
        taxon_id: int,
        size: str = "medium",
        max_images: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取物种图片 URL 列表（不下载）
        
        Args:
            taxon_id: 物种 ID
            size: 图片尺寸
            max_images: 最大数量
            
        Returns:
            图片信息字典列表
        """
        observations = self.observation_service.search(
            taxon_id=taxon_id,
            quality_grade="research",
            has_photos=True,
            per_page=max_images
        )
        
        images = []
        for obs in observations:
            for photo in obs.photos:
                if len(images) >= max_images:
                    break
                
                url = getattr(photo, f"{size}_url", None) or photo.url
                images.append({
                    "url": url,
                    "observation_id": obs.id,
                    "attribution": photo.attribution,
                    "license": photo.license_code,
                    "sizes": {
                        "square": photo.square_url,
                        "thumb": photo.thumb_url,
                        "small": photo.small_url,
                        "medium": photo.medium_url,
                        "large": photo.large_url
                    }
                })
        
        return images
    
    # ============= 统计接口 =============
    
    def get_species_observation_count(
        self,
        taxon_id: int,
        place_id: Optional[int] = None
    ) -> int:
        """
        获取物种观察记录数量
        
        Args:
            taxon_id: 物种 ID
            place_id: 可选，特定地点
            
        Returns:
            观察记录数量
        """
        return self.taxon_service.get_observation_count(taxon_id, place_id)
    
    def get_species_by_location(
        self,
        lat: float,
        lng: float,
        radius: float = 10
    ) -> List[Dict[str, Any]]:
        """
        获取特定位置周围的物种列表
        
        Args:
            lat: 纬度
            lng: 经度
            radius: 搜索半径（公里）
            
        Returns:
            物种统计列表
        """
        return self.observation_service.get_species_counts(
            lat=lat,
            lng=lng,
            radius=radius
        )


