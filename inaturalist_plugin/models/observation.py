"""
观察记录数据模型

定义 iNaturalist 观察记录相关的数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class QualityGrade(Enum):
    """观察记录质量等级"""
    RESEARCH = "research"  # 研究级
    NEEDS_ID = "needs_id"  # 需要鉴定
    CASUAL = "casual"      # 休闲级


class Geoprivacy(Enum):
    """地理位置隐私设置"""
    OPEN = "open"           # 公开
    OBSCURED = "obscured"   # 模糊
    PRIVATE = "private"     # 私有


@dataclass
class Geojson:
    """GeoJSON 坐标"""
    type: str
    coordinates: List[float]
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Geojson":
        return cls(
            type=data.get("type", "Point"),
            coordinates=data.get("coordinates", [])
        )


@dataclass
class Location:
    """位置信息"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    geoprivacy: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Location":
        return cls(
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            accuracy=data.get("positional_accuracy"),
            altitude=data.get("altitude"),
            geoprivacy=data.get("geoprivacy")
        )


@dataclass
class ObservationPhoto:
    """观察记录照片"""
    id: int
    url: str
    observation_id: int
    photo_id: int
    position: Optional[int] = None
    
    # 不同尺寸
    square_url: Optional[str] = None
    thumb_url: Optional[str] = None
    small_url: Optional[str] = None
    medium_url: Optional[str] = None
    large_url: Optional[str] = None
    
    # 元数据
    license_code: Optional[str] = None
    attribution: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ObservationPhoto":
        photo_data = data.get("photo", data)
        return cls(
            id=data.get("id", 0),
            url=photo_data.get("url", ""),
            observation_id=data.get("observation_id", 0),
            photo_id=data.get("photo_id", 0),
            position=data.get("position"),
            square_url=photo_data.get("square_url"),
            thumb_url=photo_data.get("thumb_url"),
            small_url=photo_data.get("small_url"),
            medium_url=photo_data.get("medium_url"),
            large_url=photo_data.get("large_url"),
            license_code=photo_data.get("license_code"),
            attribution=photo_data.get("attribution")
        )


@dataclass
class Identification:
    """鉴定信息"""
    id: int
    observation_id: int
    taxon_id: int
    user_id: int
    body: Optional[str] = None
    current: bool = True
    category: Optional[str] = None  # improving, supporting, maverick, etc.
    created_at: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Identification":
        return cls(
            id=data.get("id", 0),
            observation_id=data.get("observation_id", 0),
            taxon_id=data.get("taxon_id", 0),
            user_id=data.get("user_id", 0),
            body=data.get("body"),
            current=data.get("current", True),
            category=data.get("category"),
            created_at=data.get("created_at")
        )


@dataclass
class User:
    """用户信息"""
    id: int
    login: str
    name: Optional[str] = None
    icon_url: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "User":
        return cls(
            id=data.get("id", 0),
            login=data.get("login", ""),
            name=data.get("name"),
            icon_url=data.get("icon_url")
        )


@dataclass
class Observation:
    """
    观察记录完整信息
    
    这是 iNaturalist 的核心数据，包含了一次观察的所有信息
    """
    id: int
    uuid: str
    
    # 观察信息
    quality_grade: str
    species_guess: Optional[str] = None
    description: Optional[str] = None
    
    # 分类群
    taxon_id: Optional[int] = None
    taxon_name: Optional[str] = None
    taxon_rank: Optional[str] = None
    iconic_taxon_name: Optional[str] = None
    
    # 时间
    observed_on: Optional[str] = None
    observed_on_string: Optional[str] = None
    time_observed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # 位置
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    positional_accuracy: Optional[float] = None
    place_guess: Optional[str] = None
    geoprivacy: Optional[str] = None
    coordinates_obscured: bool = False
    geojson: Optional[Geojson] = None
    location_string: Optional[str] = None  # "lat,lng"
    
    # 媒体
    photos: List[ObservationPhoto] = field(default_factory=list)
    photo_urls: List[str] = field(default_factory=list)
    sounds: List[Dict[str, Any]] = field(default_factory=list)
    
    # 社区
    identifications: List[Identification] = field(default_factory=list)
    identification_count: int = 0
    num_identification_agreements: int = 0
    num_identification_disagreements: int = 0
    comments_count: int = 0
    faves_count: int = 0
    
    # 用户
    user_id: Optional[int] = None
    user_login: Optional[str] = None
    user: Optional[User] = None
    
    # 项目
    project_ids: List[int] = field(default_factory=list)
    project_observations: List[Dict[str, Any]] = field(default_factory=list)
    
    # 标识符
    identifications_most_agree: bool = False
    identifications_some_agree: bool = False
    identifications_most_disagree: bool = False
    
    # 元数据
    license_code: Optional[str] = None
    url: Optional[str] = None
    uri: Optional[str] = None
    
    # 原始数据
    raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Observation":
        """从 API 响应创建 Observation 对象"""
        
        # 处理照片
        photos = []
        if data.get("photos"):
            photos = [ObservationPhoto.from_api(p) for p in data["photos"]]
        elif data.get("observation_photos"):
            photos = [ObservationPhoto.from_api(p) for p in data["observation_photos"]]
        
        # 处理鉴定
        identifications = []
        if data.get("identifications"):
            identifications = [Identification.from_api(i) for i in data["identifications"]]
        
        # 处理用户
        user = None
        if data.get("user"):
            user = User.from_api(data["user"])
        
        # 处理 GeoJSON
        geojson = None
        if data.get("geojson"):
            geojson = Geojson.from_api(data["geojson"])
        
        # 处理分类群信息
        taxon_data = data.get("taxon", {})
        taxon_id = data.get("taxon_id") or taxon_data.get("id")
        taxon_name = taxon_data.get("name") if taxon_data else None
        taxon_rank = taxon_data.get("rank") if taxon_data else None
        
        return cls(
            id=data.get("id", 0),
            uuid=data.get("uuid", ""),
            quality_grade=data.get("quality_grade", QualityGrade.CASUAL.value),
            species_guess=data.get("species_guess"),
            description=data.get("description"),
            taxon_id=taxon_id,
            taxon_name=taxon_name,
            taxon_rank=taxon_rank,
            iconic_taxon_name=data.get("iconic_taxon_name"),
            observed_on=data.get("observed_on"),
            observed_on_string=data.get("observed_on_string"),
            time_observed_at=data.get("time_observed_at"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            positional_accuracy=data.get("positional_accuracy"),
            place_guess=data.get("place_guess"),
            geoprivacy=data.get("geoprivacy"),
            coordinates_obscured=data.get("coordinates_obscured", False),
            geojson=geojson,
            location_string=data.get("location"),
            photos=photos,
            photo_urls=data.get("photo_urls", []),
            sounds=data.get("sounds", []),
            identifications=identifications,
            identification_count=data.get("identifications_count", 0),
            num_identification_agreements=data.get("num_identification_agreements", 0),
            num_identification_disagreements=data.get("num_identification_disagreements", 0),
            comments_count=data.get("comments_count", 0),
            faves_count=data.get("faves_count", 0),
            user_id=data.get("user_id"),
            user_login=data.get("user_login"),
            user=user,
            project_ids=data.get("project_ids", []),
            project_observations=data.get("project_observations", []),
            identifications_most_agree=data.get("identifications_most_agree", False),
            identifications_some_agree=data.get("identifications_some_agree", False),
            identifications_most_disagree=data.get("identifications_most_disagree", False),
            license_code=data.get("license_code"),
            url=data.get("url"),
            uri=data.get("uri"),
            raw_data=data
        )
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        if self.species_guess:
            return self.species_guess
        elif self.taxon_name:
            return self.taxon_name
        return f"Observation #{self.id}"
    
    @property
    def is_research_grade(self) -> bool:
        """检查是否为研究级观察"""
        return self.quality_grade == QualityGrade.RESEARCH.value
    
    @property
    def has_photos(self) -> bool:
        """检查是否有照片"""
        return len(self.photos) > 0
    
    @property
    def best_photo(self) -> Optional[ObservationPhoto]:
        """获取最佳照片"""
        if self.photos:
            return self.photos[0]
        return None
    
    @property
    def photo_count(self) -> int:
        """获取照片数量"""
        return len(self.photos)
    
    def get_photo_urls(self, size: str = "medium") -> List[str]:
        """
        获取特定尺寸的所有照片 URL
        
        Args:
            size: 尺寸 (square, thumb, small, medium, large)
        """
        urls = []
        for photo in self.photos:
            url = getattr(photo, f"{size}_url", None) or photo.url
            if url:
                urls.append(url)
        return urls
    
    def get_location(self) -> Optional[Location]:
        """获取位置信息对象"""
        if self.latitude is not None and self.longitude is not None:
            return Location(
                latitude=self.latitude,
                longitude=self.longitude,
                accuracy=self.positional_accuracy,
                geoprivacy=self.geoprivacy
            )
        return None


@dataclass
class ObservationStats:
    """观察统计信息"""
    total_observations: int
    species_counts: List[Dict[str, Any]]
    rank_counts: Dict[str, int]
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ObservationStats":
        return cls(
            total_observations=data.get("total", 0),
            species_counts=data.get("species_counts", []),
            rank_counts=data.get("rank_counts", {})
        )
