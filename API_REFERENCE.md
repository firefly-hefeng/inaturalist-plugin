# iNaturalist 插件 API 参考文档

## 概述

本文档详细说明 iNaturalist 数据插件的所有公开接口和调用方式。

## 核心数据接口

### 1. 客户端接口 (`inaturalist_plugin.core.client`)

#### `INaturalistClient`

核心 API 客户端类，提供 HTTP 请求和错误处理。

```python
from inaturalist_plugin.core.client import INaturalistClient, APIConfig

# 创建默认客户端
client = INaturalistClient()

# 自定义配置
config = APIConfig(
    base_url="https://api.inaturalist.org/v1",
    timeout=30,
    max_retries=3,
    rate_limit_per_second=1.0
)
client = INaturalistClient(config)
```

**主要方法：**

| 方法 | 说明 | 参数 |
|------|------|------|
| `get(endpoint, params)` | GET 请求 | endpoint: API 路径, params: 查询参数 |
| `post(endpoint, data)` | POST 请求 | endpoint: API 路径, data: 请求体 |
| `paginate(endpoint, params, per_page, max_pages)` | 分页获取 | 自动处理分页逻辑 |
| `get_total_count(endpoint, params)` | 获取总数 | 返回符合条件的总数量 |

---

### 2. 物种服务接口 (`inaturalist_plugin.services.taxon_service`)

#### `TaxonService`

提供物种/分类群的搜索和查询功能。

```python
from inaturalist_plugin.services.taxon_service import TaxonService

service = TaxonService(client)
```

#### 2.1 搜索物种

```python
def search(
    self,
    q: Optional[str] = None,              # 搜索关键词
    taxon_id: Optional[int] = None,       # 特定物种 ID
    parent_id: Optional[int] = None,      # 父分类群 ID
    rank: Optional[str] = None,           # 分类等级 (species, genus, family...)
    min_rank: Optional[str] = None,       # 最小分类等级
    max_rank: Optional[str] = None,       # 最大分类等级
    iconic_taxa: Optional[List[str]] = None,  # 标志性类群
    is_active: Optional[bool] = None,     # 是否活跃
    per_page: int = 30,                   # 每页数量 (1-200)
    page: int = 1                         # 页码
) -> List[Taxon]
```

**调用示例：**

```python
# 搜索喜鹊
results = service.search(q="喜鹊", rank="species")

# 获取雀形目下的所有物种
results = service.search(parent_id=3, rank="species", per_page=200)

# 搜索所有鸟类
results = service.search(iconic_taxa=["Aves"], per_page=50)

# 按学名搜索
results = service.search(q="Pica pica")
```

#### 2.2 自动补全

```python
def autocomplete(
    self,
    q: str,                              # 搜索关键词（至少2字符）
    per_page: int = 10,                  # 返回数量
    min_rank: Optional[str] = None,      # 最小分类等级
    rank: Optional[str] = None           # 特定分类等级
) -> List[Taxon]
```

**调用示例：**

```python
# 输入时自动提示
suggestions = service.autocomplete("ma")
suggestions = service.autocomplete("ma", rank="species")
```

#### 2.3 获取物种详情

```python
def get_by_id(self, taxon_id: int) -> Optional[Taxon]
def get_by_name(self, scientific_name: str) -> Optional[Taxon]
```

**调用示例：**

```python
# 通过 ID 获取
taxon = service.get_by_id(8318)

# 通过学名获取
taxon = service.get_by_name("Pica pica")
```

#### 2.4 获取子分类群

```python
def get_children(
    self,
    parent_id: int,
    rank: Optional[str] = None
) -> List[Taxon]
```

**调用示例：**

```python
# 获取鸦属下的所有物种
children = service.get_children(parent_id=15287, rank="species")
```

#### 2.5 获取祖先分类群

```python
def get_ancestors(self, taxon_id: int) -> List[Taxon]
```

**调用示例：**

```python
# 获取喜鹊的完整分类路径
ancestors = service.get_ancestors(8318)
# 返回: [Animalia, Chordata, Aves, Passeriformes, Corvidae, Pica]
```

---

### 3. 观察记录服务接口 (`inaturalist_plugin.services.observation_service`)

#### `ObservationService`

提供观察记录的搜索和查询功能。

```python
from inaturalist_plugin.services.observation_service import ObservationService

service = ObservationService(client)
```

#### 3.1 搜索观察记录

```python
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
    radius: Optional[float] = None,
    
    # 时间筛选
    observed_on: Optional[str] = None,
    observed_d1: Optional[str] = None,
    observed_d2: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    
    # 质量与状态
    quality_grade: Optional[str] = None,
    geoprivacy: Optional[str] = None,
    
    # 特征筛选
    has_photos: bool = False,
    has_sounds: bool = False,
    has_geo: bool = False,
    
    # 用户筛选
    user_id: Optional[int] = None,
    user_login: Optional[str] = None,
    
    # 项目
    project_id: Optional[int] = None,
    
    # 排序与分页
    order_by: Optional[str] = None,
    order: str = "desc",
    per_page: int = 30,
    page: int = 1,
    **kwargs
) -> List[Observation]
```

**调用示例：**

```python
# 搜索特定物种的研究级观察
observations = service.search(
    taxon_id=8318,
    quality_grade="research",
    has_photos=True,
    per_page=50
)

# 搜索特定位置周围的观察（10公里半径）
observations = service.search(
    lat=39.9042,
    lng=116.4074,
    radius=10,
    has_photos=True
)

# 搜索特定日期的观察
observations = service.search(
    observed_on="2024-01-01",
    has_photos=True
)

# 搜索特定地点的鸟类
observations = service.search(
    place_id= anywhere,
    iconic_taxa=["Aves"],
    quality_grade="research"
)

# 按时间范围搜索
observations = service.search(
    observed_d1="2024-01-01",
    observed_d2="2024-12-31",
    taxon_id=8318
)
```

#### 3.2 获取观察记录详情

```python
def get_by_id(
    self,
    observation_id: int,
    include_new_projects: bool = False
) -> Optional[Observation]
```

**调用示例：**

```python
observation = service.get_by_id(12345678)
```

#### 3.3 获取观察记录数量

```python
def count(
    self,
    taxon_id: Optional[int] = None,
    place_id: Optional[int] = None,
    user_id: Optional[int] = None,
    quality_grade: Optional[str] = None,
    **kwargs
) -> int
```

**调用示例：**

```python
# 统计北京的喜鹊观察数量
count = service.count(
    taxon_id=8318,
    place_id= anywhere,
    quality_grade="research"
)
```

#### 3.4 获取物种统计

```python
def get_species_counts(
    self,
    place_id: Optional[int] = None,
    taxon_id: Optional[int] = None,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    observed_d1: Optional[str] = None,
    observed_d2: Optional[str] = None,
    hrank: Optional[str] = None,
    lrank: Optional[str] = None,
) -> List[Dict[str, Any]]
```

**调用示例：**

```python
# 获取某地的物种种类统计
species_counts = service.get_species_counts(
    place_id=anywhere,
    hrank="species"  # 只统计到物种级别
)

for item in species_counts:
    print(f"{item['taxon']['name']}: {item['count']} observations")
```

#### 3.5 获取热门观察

```python
def get_popular(
    self,
    place_id: Optional[int] = None,
    taxon_id: Optional[int] = None,
    per_page: int = 10
) -> List[Observation]
```

**调用示例：**

```python
popular = service.get_popular(taxon_id=8318, per_page=10)
```

---

### 4. 图片工具接口 (`inaturalist_plugin.utils.image_utils`)

#### `ImageDownloader`

```python
from inaturalist_plugin.utils.image_utils import ImageDownloader

downloader = ImageDownloader(cache_dir="./cache/images")
```

#### 4.1 下载单张图片

```python
def download(
    self,
    url: str,
    filename: Optional[str] = None,
    use_cache: bool = True,
    force_download: bool = False
) -> Optional[str]
```

**调用示例：**

```python
local_path = downloader.download(
    url="https://.../image.jpg",
    use_cache=True
)
```

#### 4.2 批量下载

```python
def download_multiple(
    self,
    urls: List[str],
    use_cache: bool = True,
    delay: float = 0.5
) -> Dict[str, Optional[str]]
```

**调用示例：**

```python
results = downloader.download_multiple(urls, delay=0.5)
```

#### 4.3 清除缓存

```python
def clear_cache(self, max_age_days: Optional[int] = None)
```

**调用示例：**

```python
# 清除所有缓存
downloader.clear_cache()

# 清除30天前的缓存
downloader.clear_cache(max_age_days=30)
```

---

### 5. Web 适配器接口 (`inaturalist_plugin.adapters.web_adapter`)

#### `INaturalistWebAdapter`

为 Web 应用提供统一的 API 封装。

```python
from inaturalist_plugin.adapters.web_adapter import INaturalistWebAdapter

adapter = INaturalistWebAdapter()
```

#### 5.1 物种搜索

```python
def search_species(
    self,
    query: str,
    rank: Optional[str] = None,
    iconic_taxa: Optional[List[str]] = None,
    per_page: int = 30
) -> Dict[str, Any]
```

**返回格式：**

```json
{
    "success": true,
    "query": "喜鹊",
    "total": 5,
    "results": [
        {
            "id": 8318,
            "name": "Pica pica",
            "rank": "species",
            "display_name": "喜鹊 (Pica pica)",
            "common_names": {
                "english": "Eurasian Magpie",
                "chinese": "喜鹊",
                "preferred": "Eurasian Magpie"
            },
            "iconic_taxon": "Aves",
            "observations_count": 150000,
            "conservation_status": "least_concern",
            "photos": [...],
            "default_photo": {...},
            "wikipedia": {
                "summary": "The Eurasian magpie or common magpie...",
                "url": "https://en.wikipedia.org/wiki/Eurasian_magpie"
            }
        }
    ]
}
```

#### 5.2 物种详情

```python
def get_species_detail(self, taxon_id: int) -> Dict[str, Any]
```

**返回格式：**

```json
{
    "success": true,
    "taxon": {...},
    "observation_count": 150000,
    "ancestors": [...],
    "children": [...],
    "recent_observations": [...]
}
```

#### 5.3 获取物种图片

```python
def get_species_images(
    self,
    taxon_id: int,
    size: str = "medium",
    max_images: int = 10
) -> Dict[str, Any]
```

**返回格式：**

```json
{
    "success": true,
    "taxon_id": 8318,
    "size": "medium",
    "total": 10,
    "images": [
        {
            "url": "https://...",
            "observation_id": 12345678,
            "attribution": "(c) John Doe, some rights reserved",
            "license": "CC-BY",
            "square": "https://.../square.jpg",
            "medium": "https://.../medium.jpg",
            "large": "https://.../large.jpg"
        }
    ]
}
```

---

## 数据模型

### Taxon (物种/分类群)

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | int | 物种唯一标识 |
| `name` | str | 学名（拉丁名） |
| `rank` | str | 分类等级 |
| `display_name` | str | 显示名称（包含俗名） |
| `preferred_common_name` | str | 首选俗名 |
| `chinese_common_name` | str | 中文名 |
| `iconic_taxon_name` | str | 标志性类群 |
| `observations_count` | int | 观察记录数量 |
| `default_photo` | TaxonPhoto | 默认照片 |
| `taxon_photos` | List[TaxonPhoto] | 所有照片 |
| `conservation_status_name` | str | 保护状态 |
| `wikipedia_summary` | str | Wikipedia 摘要 |
| `wikipedia_url` | str | Wikipedia 链接 |

### Observation (观察记录)

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | int | 观察记录 ID |
| `quality_grade` | str | 质量等级 |
| `species_guess` | str | 观察者猜测的物种 |
| `taxon_id` | int | 分类群 ID |
| `taxon_name` | str | 分类群名称 |
| `observed_on` | str | 观察日期 |
| `latitude` | float | 纬度 |
| `longitude` | float | 经度 |
| `place_guess` | str | 地点描述 |
| `photos` | List[ObservationPhoto] | 照片列表 |
| `identifications` | List[Identification] | 鉴定列表 |
| `user` | User | 观察者信息 |
| `description` | str | 描述 |

---

## 错误处理

所有接口可能抛出以下异常：

```python
from inaturalist_plugin.core.client import (
    INaturalistAPIError,
    RateLimitError,
    AuthenticationError
)

try:
    result = service.get_by_id(12345)
except RateLimitError:
    print("请求过于频繁，请稍后重试")
except AuthenticationError:
    print("认证失败，请检查 API 密钥")
except INaturalistAPIError as e:
    print(f"API 错误: {e.status_code} - {e}")
```

---

## 速率限制

iNaturalist API 的默认速率限制为每秒 1 个请求。插件会自动处理速率限制，但在大量请求时可能需要等待。

```python
from inaturalist_plugin.core.client import APIConfig

# 调整速率限制
config = APIConfig(rate_limit_per_second=0.5)  # 每2秒1个请求
client = INaturalistClient(config)
```

---

## 缓存策略

图片下载器支持本地缓存：

```python
downloader = ImageDownloader(cache_dir="./cache")

# 自动使用缓存
downloader.download(url, use_cache=True)

# 强制重新下载
downloader.download(url, force_download=True)

# 清理旧缓存
downloader.clear_cache(max_age_days=30)
```
