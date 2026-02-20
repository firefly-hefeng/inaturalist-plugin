# iNaturalist 数据接口使用介绍

本文档详细介绍 iNaturalist 插件的数据接口和调用方式。

## 目录

1. [数据接口概述](#1-数据接口概述)
2. [核心接口详解](#2-核心接口详解)
3. [调用方式说明](#3-调用方式说明)
4. [返回数据格式](#4-返回数据格式)
5. [错误处理](#5-错误处理)

---

## 1. 数据接口概述

### 1.1 数据来源

本插件通过 iNaturalist 官方 API v1 获取数据：
- **API 地址**: `https://api.inaturalist.org/v1`
- **文档**: https://api.inaturalist.org/v1/docs/

### 1.2 接口分类

| 类别 | 主要接口 | 说明 |
|------|----------|------|
| **Taxa** | `/taxa`, `/taxa/{id}` | 物种/分类群信息 |
| **Observations** | `/observations`, `/observations/{id}` | 观察记录 |
| **Places** | `/places` | 地点信息 |
| **Users** | `/users/{id}` | 用户信息 |

### 1.3 接口特点

- **RESTful 设计**: 标准 HTTP 方法 (GET, POST)
- **JSON 格式**: 所有响应均为 JSON
- **分页支持**: 支持分页获取大量数据
- **速率限制**: 建议每秒 1 个请求

---

## 2. 核心接口详解

### 2.1 物种搜索接口

#### 端点: `GET /taxa`

**功能**: 搜索物种/分类群

**请求参数**:

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `q` | string | 否 | 搜索关键词 | `喜鹊`, `Pica pica` |
| `id` | integer | 否 | 物种 ID | `9083` |
| `parent_id` | integer | 否 | 父分类群 ID | `3` (雀形目) |
| `rank` | string | 否 | 分类等级 | `species`, `genus`, `family` |
| `min_rank` | string | 否 | 最小分类等级 | `genus` |
| `max_rank` | string | 否 | 最大分类等级 | `species` |
| `iconic_taxa` | string | 否 | 标志性类群 | `Aves,Plantae` |
| `is_active` | boolean | 否 | 是否活跃 | `true` |
| `per_page` | integer | 否 | 每页数量 (1-200) | `30` |
| `page` | integer | 否 | 页码 | `1` |

**代码调用**:

```python
from inaturalist_plugin.core.client import create_client

client = create_client()

# 基础搜索
response = client.get("/taxa", params={"q": "喜鹊", "per_page": 10})

# 按分类等级筛选
response = client.get("/taxa", params={
    "parent_id": 3,        # 雀形目
    "rank": "species",     # 物种级别
    "per_page": 200
})

# 标志性类群
response = client.get("/taxa", params={
    "iconic_taxa": "Aves",  # 鸟类
    "per_page": 50
})
```

**返回数据**:

```json
{
  "total_results": 150,
  "page": 1,
  "per_page": 10,
  "results": [
    {
      "id": 9083,
      "name": "Pica pica",
      "rank": "species",
      "rank_level": 10,
      "iconic_taxon_id": 3,
      "iconic_taxon_name": "Aves",
      "preferred_common_name": "Eurasian Magpie",
      "observations_count": 150000,
      "default_photo": {
        "id": 12345,
        "url": "https://static.inaturalist.org/photos/...",
        "square_url": "https://.../square.jpg",
        "medium_url": "https://.../medium.jpg",
        "large_url": "https://.../large.jpg",
        "attribution": "(c) John Doe, some rights reserved",
        "license_code": "CC-BY"
      },
      "taxon_photos": [...],
      "conservation_status": {
        "status": "LC",
        "authority": "IUCN"
      },
      "wikipedia_summary": "The Eurasian magpie or common magpie...",
      "wikipedia_url": "https://en.wikipedia.org/wiki/Eurasian_magpie",
      "ancestor_ids": [1, 2, 3, 67561, 4343, 4360, 15287],
      "parent_id": 15287
    }
  ]
}
```

---

### 2.2 物种详情接口

#### 端点: `GET /taxa/{id}`

**功能**: 获取特定物种的详细信息

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | integer | 是 | 物种 ID |

**代码调用**:

```python
# 获取喜鹊详情
response = client.get("/taxa/9083")
taxon = response["results"][0]

print(f"名称: {taxon['name']}")
print(f"俗名: {taxon.get('preferred_common_name')}")
print(f"观察数: {taxon['observations_count']}")
```

---

### 2.3 物种自动补全接口

#### 端点: `GET /taxa/autocomplete`

**功能**: 实时搜索建议

**请求参数**:

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `q` | string | 是 | 搜索关键词 | `ma` |
| `per_page` | integer | 否 | 返回数量 | `10` |
| `min_rank` | string | 否 | 最小等级 | `species` |
| `rank` | string | 否 | 特定等级 | `species` |

**代码调用**:

```python
# 用户输入自动补全
response = client.get("/taxa/autocomplete", params={
    "q": "ma",
    "per_page": 10,
    "rank": "species"
})

for taxon in response["results"]:
    print(f"{taxon['id']}: {taxon['name']}")
```

---

### 2.4 观察记录搜索接口

#### 端点: `GET /observations`

**功能**: 搜索观察记录（最强大的接口之一）

**请求参数 - 分类群筛选**:

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `taxon_id` | integer | 物种 ID | `9083` |
| `taxon_name` | string | 物种名称 | `Pica pica` |
| `iconic_taxa` | string | 标志性类群 | `Aves,Plantae` |

**请求参数 - 地点筛选**:

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `place_id` | integer | 地点 ID | ` anywhere` |
| `lat` | float | 纬度 | `39.9042` |
| `lng` | float | 经度 | `116.4074` |
| `radius` | float | 半径（公里） | `10` |
| `swlat`, `swlng` | float | 边界框西南角 | 用于矩形区域 |
| `nelat`, `nelng` | float | 边界框东北角 | 用于矩形区域 |

**请求参数 - 时间筛选**:

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `observed_on` | string | 观察日期 | `2024-01-01` |
| `d1` | string | 开始日期 | `2024-01-01` |
| `d2` | string | 结束日期 | `2024-12-31` |
| `year` | integer | 年份 | `2024` |
| `month` | integer | 月份 | `1-12` |
| `day` | integer | 日期 | `1-31` |

**请求参数 - 质量筛选**:

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `quality_grade` | string | 质量等级 | `research`, `needs_id`, `casual` |
| `geoprivacy` | string | 地理隐私 | `open`, `obscured`, `private` |

**请求参数 - 特征筛选**:

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `photos` | boolean | 有照片 | `true` |
| `sounds` | boolean | 有声音 | `true` |
| `geo` | boolean | 有地理坐标 | `true` |
| `identified` | boolean | 已鉴定 | `true` |

**代码调用**:

```python
# 基础搜索
response = client.get("/observations", params={
    "taxon_id": 9083,
    "quality_grade": "research",
    "photos": "true",
    "per_page": 30
})

# 位置搜索（圆形区域）
response = client.get("/observations", params={
    "lat": 39.9042,
    "lng": 116.4074,
    "radius": 10,
    "has[]": ["photos", "geo"],
    "per_page": 50
})

# 时间范围搜索
response = client.get("/observations", params={
    "taxon_id": 9083,
    "d1": "2024-01-01",
    "d2": "2024-12-31",
    "quality_grade": "research"
})

# 多条件组合搜索
response = client.get("/observations", params={
    "iconic_taxa": "Aves",           # 鸟类
    "place_id": anywhere,            # 北京
    "quality_grade": "research",     # 研究级
    "photos": "true",                # 有照片
    "year": 2024,                    # 2024年
    "order_by": "observed_on",       # 按日期排序
    "order": "desc",                 # 倒序
    "per_page": 100
})
```

**返回数据**:

```json
{
  "total_results": 10000,
  "page": 1,
  "per_page": 30,
  "results": [
    {
      "id": 12345678,
      "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "quality_grade": "research",
      "species_guess": "喜鹊",
      "taxon": {
        "id": 9083,
        "name": "Pica pica",
        "rank": "species"
      },
      "observed_on": "2024-01-15",
      "observed_on_string": "2024-01-15 10:30",
      "time_observed_at": "2024-01-15T10:30:00-05:00",
      "created_at": "2024-01-15T15:20:00-05:00",
      "location": "39.9042,116.4074",
      "latitude": 39.9042,
      "longitude": 116.4074,
      "positional_accuracy": 10,
      "place_guess": "北京市, 中国",
      "geoprivacy": "open",
      "coordinates_obscured": false,
      "photos": [
        {
          "id": 98765432,
          "url": "https://static.inaturalist.org/photos/...",
          "square_url": "https://.../square.jpg",
          "medium_url": "https://.../medium.jpg",
          "large_url": "https://.../large.jpg",
          "license_code": "CC-BY",
          "attribution": "(c) Zhang San, some rights reserved"
        }
      ],
      "user": {
        "id": 12345,
        "login": "zhangsan",
        "name": "张三",
        "icon_url": "https://..."
      },
      "identifications_count": 3,
      "comments_count": 2,
      "faves_count": 15,
      "uri": "https://www.inaturalist.org/observations/12345678"
    }
  ]
}
```

---

### 2.5 观察记录详情接口

#### 端点: `GET /observations/{id}`

**功能**: 获取单个观察记录的详细信息

**代码调用**:

```python
response = client.get("/observations/12345678")
observation = response["results"][0]

print(f"观察 ID: {observation['id']}")
print(f"物种: {observation['species_guess']}")
print(f"日期: {observation['observed_on']}")
print(f"地点: {observation['place_guess']}")
print(f"照片数: {len(observation['photos'])}")
```

---

### 2.6 物种统计接口

#### 端点: `GET /observations/species_counts`

**功能**: 获取特定条件下的物种种类和数量统计

**代码调用**:

```python
# 获取北京的物种种类统计
response = client.get("/observations/species_counts", params={
    "place_id": anywhere,
    "quality_grade": "research",
    "hrank": "species"  # 最高到物种级别
})

for item in response["results"]:
    taxon = item["taxon"]
    count = item["count"]
    print(f"{taxon['name']}: {count} 次观察")
```

---

## 3. 调用方式说明

### 3.1 直接调用（低级接口）

直接使用 `INaturalistClient` 进行 API 调用：

```python
from inaturalist_plugin.core.client import create_client

client = create_client()

# GET 请求
response = client.get("/taxa", params={"q": "喜鹊"})
results = response["results"]

# 分页获取
all_results = client.paginate(
    endpoint="/observations",
    params={"taxon_id": 9083, "quality_grade": "research"},
    per_page=200,
    max_pages=5
)

# 获取总数
total = client.get_total_count("/observations", params={"taxon_id": 9083})
print(f"总共 {total} 条观察记录")
```

### 3.2 服务层调用（推荐）

使用服务类提供更高级的封装：

```python
from inaturalist_plugin import INaturalistPlugin

plugin = INaturalistPlugin()

# 物种搜索
species = plugin.search_species("喜鹊", per_page=10)

# 获取详情
details = plugin.get_species_detail(9083)

# 搜索观察记录
observations = plugin.search_observations(
    taxon_id=9083,
    quality_grade="research",
    per_page=30
)

# 获取图片
images = plugin.get_species_image_urls(9083, size="large", max_images=5)
```

### 3.3 Web 适配器调用（Web 应用）

使用 Web 适配器快速集成到 Web 应用：

```python
from inaturalist_plugin.adapters.web_adapter import INaturalistWebAdapter

adapter = INaturalistWebAdapter()

# 返回标准化的 JSON 响应
result = adapter.search_species("喜鹊")
print(result)
# {
#   "success": True,
#   "query": "喜鹊",
#   "total": 5,
#   "results": [...]
# }
```

---

## 4. 返回数据格式

### 4.1 标准响应格式

所有 API 响应都遵循以下结构：

```json
{
  "total_results": 100,
  "page": 1,
  "per_page": 30,
  "results": [...]
}
```

### 4.2 图片尺寸说明

iNaturalist 提供以下尺寸的图片：

| 尺寸 | 像素 | 用途 |
|------|------|------|
| `square` | 75x75 | 缩略图、头像 |
| `thumb` | 100x100 | 小缩略图 |
| `small` | 240x240 | 列表展示 |
| `medium` | 500x500 | 详情页展示 |
| `large` | 1024x1024 | 大图查看 |
| `original` | 原始尺寸 | 原始图片 |

**获取不同尺寸**:

```python
# 在照片对象中
photo = observation["photos"][0]
square_url = photo["square_url"]
medium_url = photo["medium_url"]
large_url = photo["large_url"]
```

### 4.3 分类等级说明

| 等级 | 英文 | 等级值 |
|------|------|--------|
| 界 | kingdom | 70 |
| 门 | phylum | 60 |
| 纲 | class | 50 |
| 目 | order | 40 |
| 科 | family | 30 |
| 属 | genus | 20 |
| 种 | species | 10 |
| 亚种 | subspecies | 5 |

---

## 5. 错误处理

### 5.1 错误类型

```python
from inaturalist_plugin.core.client import (
    INaturalistAPIError,
    RateLimitError,
    AuthenticationError
)

try:
    result = client.get("/taxa/999999999")
except RateLimitError as e:
    # 429 Too Many Requests
    print(f"请求过于频繁，请等待后重试")
except AuthenticationError as e:
    # 401 Unauthorized
    print(f"认证失败: {e}")
except INaturalistAPIError as e:
    # 其他 API 错误
    print(f"API 错误 [{e.status_code}]: {e}")
```

### 5.2 HTTP 状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理 |
| 400 | 请求参数错误 | 检查参数格式 |
| 401 | 未授权 | 检查 API 密钥 |
| 404 | 资源不存在 | 检查 ID 是否正确 |
| 429 | 请求过多 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |

### 5.3 速率限制

```python
from inaturalist_plugin.core.client import APIConfig

# 配置速率限制（默认每秒1个请求）
config = APIConfig(rate_limit_per_second=0.5)  # 每2秒1个请求
client = INaturalistClient(config)

# 或使用自动重试
config = APIConfig(max_retries=5, retry_delay=2.0)
client = INaturalistClient(config)
```

---

## 附录：常用物种 ID 参考

| 物种 | 学名 | ID |
|------|------|-----|
| 喜鹊 | Pica pica | 9083 |
| 麻雀 | Passer montanus | 11901 |
| 家燕 | Hirundo rustica | 14825 |
| 珠颈斑鸠 | Spilopelia chinensis | 11515 |
| 白头鹎 | Pycnonotus sinensis | 13475 |

---

**更多示例请参考 [EXAMPLES.md](EXAMPLES.md)**
