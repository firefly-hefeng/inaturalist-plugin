"""
图片处理工具模块

提供图片下载、处理和缓存功能
"""

import os
import hashlib
import requests
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass
import time


@dataclass
class ImageInfo:
    """图片信息"""
    url: str
    local_path: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    
    @property
    def is_downloaded(self) -> bool:
        """检查图片是否已下载到本地"""
        return self.local_path is not None and os.path.exists(self.local_path)


class ImageDownloader:
    """
    图片下载器
    
    支持功能:
    - 图片下载
    - 本地缓存
    - 批量下载
    - 多种尺寸选择
    """
    
    def __init__(self, cache_dir: Optional[str] = None, timeout: int = 30):
        """
        初始化下载器
        
        Args:
            cache_dir: 缓存目录，默认为 ~/.inaturalist/cache/images
            timeout: 下载超时时间（秒）
        """
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.expanduser("~"),
                ".inaturalist",
                "cache",
                "images"
            )
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "iNaturalistPlugin/1.0 (Scientific Research)"
        })
    
    def _get_cache_path(self, url: str) -> Path:
        """
        根据 URL 生成缓存路径
        
        Args:
            url: 图片 URL
            
        Returns:
            缓存文件路径
        """
        # 使用 URL 的哈希作为文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # 从 URL 中提取扩展名
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1]
        if not ext:
            ext = ".jpg"  # 默认扩展名
        
        filename = f"{url_hash}{ext}"
        return self.cache_dir / filename
    
    def download(
        self,
        url: str,
        filename: Optional[str] = None,
        use_cache: bool = True,
        force_download: bool = False
    ) -> Optional[str]:
        """
        下载单张图片
        
        Args:
            url: 图片 URL
            filename: 可选，自定义文件名
            use_cache: 是否使用缓存
            force_download: 是否强制重新下载（忽略缓存）
            
        Returns:
            下载后的本地文件路径，失败返回 None
        """
        if not url:
            return None
        
        # 确定保存路径
        if filename:
            save_path = self.cache_dir / filename
        else:
            save_path = self._get_cache_path(url)
        
        # 检查缓存
        if use_cache and not force_download and save_path.exists():
            return str(save_path)
        
        try:
            # 下载图片
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # 保存到文件
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(save_path)
            
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
            return None
    
    def download_multiple(
        self,
        urls: List[str],
        use_cache: bool = True,
        delay: float = 0.5
    ) -> Dict[str, Optional[str]]:
        """
        批量下载图片
        
        Args:
            urls: 图片 URL 列表
            use_cache: 是否使用缓存
            delay: 下载间隔（秒），避免请求过快
            
        Returns:
            URL 到本地路径的映射字典
        """
        results = {}
        
        for url in urls:
            local_path = self.download(url, use_cache=use_cache)
            results[url] = local_path
            
            if delay > 0:
                time.sleep(delay)
        
        return results
    
    def get_image_info(self, url: str) -> Optional[ImageInfo]:
        """
        获取图片信息（不下载）
        
        Args:
            url: 图片 URL
            
        Returns:
            ImageInfo 对象
        """
        try:
            response = self.session.head(url, timeout=self.timeout)
            response.raise_for_status()
            
            return ImageInfo(
                url=url,
                size=int(response.headers.get("Content-Length", 0)),
                format=response.headers.get("Content-Type", "").split("/")[-1]
            )
        except Exception:
            return None
    
    def clear_cache(self, max_age_days: Optional[int] = None):
        """
        清理缓存
        
        Args:
            max_age_days: 可选，只删除超过指定天数的缓存文件
        """
        if not self.cache_dir.exists():
            return
        
        for file_path in self.cache_dir.iterdir():
            if not file_path.is_file():
                continue
            
            if max_age_days is not None:
                file_age = time.time() - file_path.stat().st_mtime
                if file_age < max_age_days * 86400:
                    continue
            
            file_path.unlink()


class ImageSizeHelper:
    """
    图片尺寸帮助类
    
    iNaturalist 提供以下尺寸的图片:
    - square: 75x75 像素
    - thumb: 100x100 像素  
    - small: 240x240 像素
    - medium: 500x500 像素
    - large: 1024x1024 像素 (原始尺寸)
    """
    
    SIZES = {
        "square": (75, 75),
        "thumb": (100, 100),
        "small": (240, 240),
        "medium": (500, 500),
        "large": (1024, 1024),
        "original": (None, None)
    }
    
    @classmethod
    def get_best_url(
        cls,
        photo_obj: Any,
        min_width: Optional[int] = None,
        preferred_size: str = "medium"
    ) -> Optional[str]:
        """
        获取最佳尺寸的图片 URL
        
        Args:
            photo_obj: 照片对象 (TaxonPhoto 或 ObservationPhoto)
            min_width: 最小宽度要求
            preferred_size: 首选尺寸
            
        Returns:
            图片 URL
        """
        if not photo_obj:
            return None
        
        # 按质量从高到低检查
        size_order = ["large", "medium", "small", "thumb", "square", "url"]
        
        if preferred_size in size_order:
            # 将首选尺寸移到最前面
            size_order.remove(preferred_size)
            size_order.insert(0, preferred_size)
        
        for size in size_order:
            url = getattr(photo_obj, f"{size}_url", None)
            if url:
                return url
        
        return getattr(photo_obj, "url", None)
    
    @classmethod
    def get_all_urls(cls, photo_obj: Any) -> Dict[str, Optional[str]]:
        """
        获取所有尺寸的图片 URL
        
        Args:
            photo_obj: 照片对象
            
        Returns:
            尺寸到 URL 的映射
        """
        return {
            "square": getattr(photo_obj, "square_url", None),
            "thumb": getattr(photo_obj, "thumb_url", None),
            "small": getattr(photo_obj, "small_url", None),
            "medium": getattr(photo_obj, "medium_url", None),
            "large": getattr(photo_obj, "large_url", None),
            "original": getattr(photo_obj, "url", None)
        }
    
    @classmethod
    def select_size_by_width(cls, width: int) -> str:
        """
        根据目标宽度选择最合适的尺寸
        
        Args:
            width: 目标宽度
            
        Returns:
            尺寸名称
        """
        if width <= 75:
            return "square"
        elif width <= 100:
            return "thumb"
        elif width <= 240:
            return "small"
        elif width <= 500:
            return "medium"
        else:
            return "large"


def download_species_photos(
    taxon,
    size: str = "medium",
    max_photos: int = 5,
    cache_dir: Optional[str] = None
) -> List[str]:
    """
    便捷函数：下载物种照片
    
    Args:
        taxon: Taxon 对象
        size: 照片尺寸
        max_photos: 最大下载数量
        cache_dir: 缓存目录
        
    Returns:
        下载成功的本地文件路径列表
    """
    downloader = ImageDownloader(cache_dir=cache_dir)
    urls = taxon.get_photos_by_size(size)[:max_photos]
    
    results = []
    for url in urls:
        local_path = downloader.download(url)
        if local_path:
            results.append(local_path)
    
    return results


def download_observation_photos(
    observation,
    size: str = "medium",
    cache_dir: Optional[str] = None
) -> List[str]:
    """
    便捷函数：下载观察记录照片
    
    Args:
        observation: Observation 对象
        size: 照片尺寸
        cache_dir: 缓存目录
        
    Returns:
        下载成功的本地文件路径列表
    """
    downloader = ImageDownloader(cache_dir=cache_dir)
    urls = observation.get_photo_urls(size)
    
    results = []
    for url in urls:
        local_path = downloader.download(url)
        if local_path:
            results.append(local_path)
    
    return results
