"""
物种/分类群数据模型

定义 iNaturalist 物种相关的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RankLevel(Enum):
    """分类等级"""
    KINGDOM = 70
    PHYLUM = 60
    SUBPHYLUM = 57
    SUPERCLASS = 53
    CLASS = 50
    SUBCLASS = 47
    SUPERORDER = 43
    ORDER = 40
    SUBORDER = 37
    INFRAORDER = 35
    SUPERFAMILY = 33
    FAMILY = 30
    SUBFAMILY = 27
    TRIBE = 25
    SUBTRIBE = 24
    GENUS = 20
    SUBGENUS = 17
    SECTION = 15
    SUBSECTION = 14
    COMPLEX = 13
    SPECIES = 10
    SUBSPECIES = 5
    VARIETY = 5
    FORM = 5
    HYBRID = 5


class ConservationStatus(Enum):
    """保护状态 (IUCN)"""
    EXTINCT = "EX"
    EXTINCT_IN_WILD = "EW"
    CRITICALLY_ENDANGERED = "CR"
    ENDANGERED = "EN"
    VULNERABLE = "VU"
    NEAR_THREATENED = "NT"
    CONSERVATION_DEPENDENT = "CD"
    LEAST_CONCERN = "LC"
    DATA_DEFICIENT = "DD"
    NOT_EVALUATED = "NE"


class EstablishmentMeans(Enum):
    """建立方式 (物种在特定区域的分布状态)"""
    NATIVE = "native"
    ENDEMIC = "endemic"
    INTRODUCED = "introduced"
    NATURALISED = "naturalised"
    INVASIVE = "invasive"
    MANAGED = "managed"
    UNCERTAIN = "uncertain"


@dataclass
class TaxonPhoto:
    """物种照片"""
    id: int
    url: str
    attribution: str
    license_code: Optional[str] = None
    original_dimensions: Optional[Dict[str, int]] = None
    
    # 不同尺寸的图片 URL
    square_url: Optional[str] = None
    thumb_url: Optional[str] = None
    small_url: Optional[str] = None
    medium_url: Optional[str] = None
    large_url: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "TaxonPhoto":
        """从 API 响应创建对象"""
        return cls(
            id=data.get("id", 0),
            url=data.get("url", ""),
            attribution=data.get("attribution", ""),
            license_code=data.get("license_code"),
            original_dimensions=data.get("original_dimensions"),
            square_url=data.get("square_url"),
            thumb_url=data.get("thumb_url"),
            small_url=data.get("small_url"),
            medium_url=data.get("medium_url"),
            large_url=data.get("large_url")
        )


@dataclass
class TaxonName:
    """物种名称（不同语言）"""
    name: str
    locale: str
    lexicon: str
    is_valid: bool = True
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "TaxonName":
        return cls(
            name=data.get("name", ""),
            locale=data.get("locale", ""),
            lexicon=data.get("lexicon", ""),
            is_valid=data.get("is_valid", True)
        )


@dataclass
class ConservationStatusInfo:
    """保护状态详情"""
    status: str
    authority: Optional[str] = None
    place: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    url: Optional[str] = None
    geoprivacy: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ConservationStatusInfo":
        return cls(
            status=data.get("status", ""),
            authority=data.get("authority"),
            place=data.get("place"),
            description=data.get("description"),
            url=data.get("url"),
            geoprivacy=data.get("geoprivacy")
        )


@dataclass
class EstablishmentMeansInfo:
    """建立方式详情（特定区域的分布状态）"""
    establishment_means: str
    place: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "EstablishmentMeansInfo":
        return cls(
            establishment_means=data.get("establishment_means", ""),
            place=data.get("place")
        )


@dataclass
class Taxon:
    """
    物种/分类群完整信息
    
    这是 iNaturalist 中最核心的数据模型，包含了物种的分类学信息、
    图片、保护状态等。
    """
    id: int
    name: str  # 学名（拉丁名）
    rank: str  # 分类等级
    rank_level: int
    
    # 基本信息
    iconic_taxon_id: Optional[int] = None
    iconic_taxon_name: Optional[str] = None
    
    # 名称
    preferred_common_name: Optional[str] = None  # 首选俗名
    english_common_name: Optional[str] = None
    chinese_common_name: Optional[str] = None
    
    # 分类学信息
    parent_id: Optional[int] = None
    ancestor_ids: List[int] = field(default_factory=list)
    
    # 统计数据
    observations_count: int = 0
    
    # 媒体
    default_photo: Optional[TaxonPhoto] = None
    taxon_photos: List[TaxonPhoto] = field(default_factory=list)
    
    # 保护状态
    conservation_status: Optional[ConservationStatusInfo] = None
    conservation_status_name: Optional[str] = None
    
    # 建立方式
    establishment_means: Optional[EstablishmentMeansInfo] = None
    
    # 其他
    wikipedia_summary: Optional[str] = None
    wikipedia_url: Optional[str] = None
    
    # 原始数据
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Taxon":
        """从 API 响应创建 Taxon 对象"""
        
        # 处理照片
        default_photo = None
        if data.get("default_photo"):
            default_photo = TaxonPhoto.from_api(data["default_photo"])
        
        taxon_photos = []
        if data.get("taxon_photos"):
            taxon_photos = [TaxonPhoto.from_api(tp.get("photo", tp)) for tp in data["taxon_photos"]]
        
        # 处理保护状态
        conservation_status = None
        if data.get("conservation_status"):
            conservation_status = ConservationStatusInfo.from_api(data["conservation_status"])
        
        # 处理建立方式
        establishment_means = None
        if data.get("establishment_means"):
            establishment_means = EstablishmentMeansInfo.from_api(data["establishment_means"])
        
        # 提取不同语言的俗名
        chinese_name = None
        english_name = None
        if data.get("taxon_names"):
            for tn in data["taxon_names"]:
                if tn.get("lexicon") == "Chinese (Simplified)":
                    chinese_name = tn.get("name")
                elif tn.get("lexicon") == "English":
                    english_name = tn.get("name")
        
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            rank=data.get("rank", ""),
            rank_level=data.get("rank_level", 0),
            iconic_taxon_id=data.get("iconic_taxon_id"),
            iconic_taxon_name=data.get("iconic_taxon_name"),
            preferred_common_name=data.get("preferred_common_name"),
            english_common_name=english_name,
            chinese_common_name=chinese_name,
            parent_id=data.get("parent_id"),
            ancestor_ids=data.get("ancestor_ids", []),
            observations_count=data.get("observations_count", 0),
            default_photo=default_photo,
            taxon_photos=taxon_photos,
            conservation_status=conservation_status,
            conservation_status_name=data.get("conservation_status_name"),
            establishment_means=establishment_means,
            wikipedia_summary=data.get("wikipedia_summary"),
            wikipedia_url=data.get("wikipedia_url"),
            raw_data=data
        )
    
    @property
    def display_name(self) -> str:
        """获取显示名称（优先使用中文名，其次是英文名，最后是学名）"""
        if self.chinese_common_name:
            return f"{self.chinese_common_name} ({self.name})"
        elif self.english_common_name:
            return f"{self.english_common_name} ({self.name})"
        elif self.preferred_common_name:
            return f"{self.preferred_common_name} ({self.name})"
        return self.name
    
    @property
    def is_species_or_lower(self) -> bool:
        """检查是否为物种级别或更低（亚种等）"""
        return self.rank_level <= RankLevel.SPECIES.value
    
    @property
    def best_photo_url(self) -> Optional[str]:
        """获取最佳质量的图片 URL"""
        if self.default_photo:
            return self.default_photo.large_url or self.default_photo.medium_url or self.default_photo.url
        return None
    
    def get_photos_by_size(self, size: str = "medium") -> List[str]:
        """
        获取特定尺寸的所有图片 URL
        
        Args:
            size: 尺寸 (square, thumb, small, medium, large)
        """
        urls = []
        for photo in self.taxon_photos:
            url = getattr(photo, f"{size}_url", None) or photo.url
            if url:
                urls.append(url)
        return urls


@dataclass
class TaxonSummary:
    """物种统计摘要"""
    taxon: Taxon
    count: int
    observation_ids: Optional[List[int]] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "TaxonSummary":
        taxon_data = data.get("taxon", {})
        return cls(
            taxon=Taxon.from_api(taxon_data),
            count=data.get("count", 0),
            observation_ids=data.get("observation_ids")
        )
