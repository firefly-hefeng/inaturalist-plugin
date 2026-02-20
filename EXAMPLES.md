# iNaturalist 插件使用示例

## 快速开始

### 安装与导入

```python
# 导入主插件类
from inaturalist_plugin import INaturalistPlugin

# 创建插件实例
plugin = INaturalistPlugin()
```

---

## 示例 1: 基础物种搜索

```python
from inaturalist_plugin import INaturalistPlugin

plugin = INaturalistPlugin()

# 搜索喜鹊
results = plugin.search_species("喜鹊")

for taxon in results:
    print(f"ID: {taxon.id}")
    print(f"学名: {taxon.name}")
    print(f"俗名: {taxon.display_name}")
    print(f"观察数: {taxon.observations_count}")
    print("-" * 40)
```

**输出：**
```
ID: 9083
学名: Pica pica
俗名: 喜鹊 (Pica pica)
观察数: 150000
----------------------------------------
```

---

## 示例 2: 获取物种详细信息

```python
from inaturalist_plugin import get_species

# 获取喜鹊详细信息
taxon = get_species(9083)

print(f"学名: {taxon.name}")
print(f"中文名: {taxon.chinese_common_name}")
print(f"英文名: {taxon.english_common_name}")
print(f"分类等级: {taxon.rank}")
print(f"观察记录数: {taxon.observations_count}")
print(f"保护状态: {taxon.conservation_status_name}")

# 获取祖先分类群
ancestors = taxon.ancestor_ids
print(f"\n分类路径: {' > '.join(str(a) for a in ancestors)}")

# Wikipedia 信息
if taxon.wikipedia_summary:
    print(f"\nWikipedia: {taxon.wikipedia_summary[:200]}...")
    print(f"Wikipedia 链接: {taxon.wikipedia_url}")
```

---

## 示例 3: 获取物种图片

```python
from inaturalist_plugin import INaturalistPlugin

plugin = INaturalistPlugin()

# 获取喜鹊的图片 URL
images = plugin.get_species_image_urls(
    taxon_id=9083,
    size="medium",
    max_images=5
)

for img in images:
    print(f"URL: {img['url']}")
    print(f"拍摄者: {img['attribution']}")
    print(f"许可证: {img['license']}")
    print(f"观察记录: https://www.inaturalist.org/observations/{img['observation_id']}")
    print("-" * 40)

# 下载图片到本地
local_paths = plugin.download_species_images(
    taxon_id=9083,
    size="large",
    max_images=5
)

print(f"已下载 {len(local_paths)} 张图片:")
for path in local_paths:
    print(f"  - {path}")
```

---

## 示例 4: 搜索观察记录

```python
from inaturalist_plugin import search_observations

# 搜索喜鹊的研究级观察记录
observations = search_observations(
    taxon_id=9083,
    quality_grade="research",
    has_photos=True,
    per_page=10
)

for obs in observations:
    print(f"观察 ID: {obs.id}")
    print(f"日期: {obs.observed_on}")
    print(f"地点: {obs.place_guess}")
    print(f"观察者: {obs.user_login}")
    print(f"照片数: {obs.photo_count}")
    
    # 获取照片 URL
    photo_urls = obs.get_photo_urls("medium")
    print(f"照片: {photo_urls}")
    print("-" * 40)
```

---

## 示例 5: 按位置搜索

```python
from inaturalist_plugin import INaturalistPlugin

plugin = INaturalistPlugin()

# 搜索北京市中心周围10公里内的鸟类观察
# 坐标: 天安门 (39.9042, 116.4074)
observations = plugin.search_observations(
    lat=39.9042,
    lng=116.4074,
    radius=10,  # 公里
    quality_grade="research",
    has_photos=True,
    per_page=20
)

print(f"找到 {len(observations)} 条观察记录")

for obs in observations:
    print(f"\n物种: {obs.display_name}")
    print(f"位置: {obs.place_guess}")
    print(f"坐标: ({obs.latitude}, {obs.longitude})")
    print(f"距离: 天安门附近")
    print(f"观察日期: {obs.observed_on}")
    
    if obs.best_photo:
        print(f"图片: {obs.best_photo.medium_url}")
```

---

## 示例 6: 获取地点物种统计

```python
from inaturalist_plugin import INaturalistPlugin

plugin = INaturalistPlugin()

# 获取北京周边的物种种类
species_list = plugin.get_species_by_location(
    lat=39.9042,
    lng=116.4074,
    radius=20
)

print(f"该区域共记录 {len(species_list)} 种物种")

# 按观察数量排序
species_list.sort(key=lambda x: x['count'], reverse=True)

print("\nTop 10 物种:")
for item in species_list[:10]:
    taxon = item['taxon']
    count = item['count']
    print(f"  {taxon.get('preferred_common_name', taxon['name'])}: {count} 次观察")
```

---

## 示例 7: 自动补全（搜索建议）

```python
from inaturalist_plugin.services.taxon_service import TaxonService
from inaturalist_plugin.core.client import create_client

client = create_client()
service = TaxonService(client)

# 用户输入时实时提示
query = "ma"
suggestions = service.autocomplete(query, per_page=10)

print(f"'{query}' 的搜索建议:")
for taxon in suggestions:
    print(f"  - {taxon.display_name}")
```

---

## 示例 8: 完整分类树获取

```python
from inaturalist_plugin import get_species
from inaturalist_plugin.core.client import create_client
from inaturalist_plugin.services.taxon_service import TaxonService

client = create_client()
service = TaxonService(client)

# 获取喜鹊的完整分类信息
taxon = get_species(9083)

print(f"目标物种: {taxon.display_name}")
print(f"学名: {taxon.name}")
print(f"\n完整分类路径:")

# 获取所有祖先
ancestors = service.get_ancestors(taxon.id)
for ancestor in ancestors:
    indent = "  " * (10 - ancestor.rank_level // 10)  # 根据等级缩进
    print(f"{indent}[{ancestor.rank}] {ancestor.display_name}")

print(f"{'  '}[{taxon.rank}] {taxon.display_name}")

# 获取同属的其他物种
if taxon.parent_id:
    siblings = service.get_children(taxon.parent_id, rank="species")
    print(f"\n同属其他物种 ({len(siblings)} 种):")
    for sibling in siblings[:10]:  # 只显示前10个
        marker = "👉 " if sibling.id == taxon.id else "   "
        print(f"{marker}{sibling.display_name}")
```

---

## 示例 9: 批量下载图片

```python
from inaturalist_plugin import INaturalistPlugin
from inaturalist_plugin.utils.image_utils import ImageDownloader

plugin = INaturalistPlugin()

# 批量下载多个物种的图片
species_ids = [9083, 11901, 14825]  # 喜鹊、麻雀、家燕

downloader = ImageDownloader(cache_dir="./species_images")

for taxon_id in species_ids:
    taxon = plugin.get_species_detail(taxon_id)
    print(f"\n下载 {taxon.display_name} 的图片...")
    
    paths = plugin.download_species_images(
        taxon_id=taxon_id,
        size="large",
        max_images=3
    )
    
    print(f"  成功下载 {len(paths)} 张图片")
    for path in paths:
        print(f"    - {path}")

# 清理一周前的缓存
downloader.clear_cache(max_age_days=7)
```

---

## 示例 10: Web 应用集成 (Flask)

```python
from flask import Flask, jsonify, request, render_template
from inaturalist_plugin.adapters.web_adapter import INaturalistWebAdapter, create_flask_routes

app = Flask(__name__)

# 创建适配器
adapter = INaturalistWebAdapter()

# 注册 API 路由
create_flask_routes(app, adapter)

# 自定义页面路由
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/species/<int:taxon_id>")
def species_page(taxon_id):
    """物种详情页面"""
    result = adapter.get_species_detail(taxon_id)
    
    if not result.get("success"):
        return "Species not found", 404
    
    return render_template("species.html", **result)

@app.route("/search")
def search_page():
    """搜索结果页面"""
    query = request.args.get("q", "")
    if not query:
        return render_template("search.html", query="", results=[])
    
    result = adapter.search_species(query, per_page=30)
    return render_template("search.html", query=query, **result)

if __name__ == "__main__":
    app.run(debug=True)
```

**配套的 HTML 模板示例：**

```html
<!-- templates/species.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ taxon.display_name }}</title>
</head>
<body>
    <h1>{{ taxon.display_name }}</h1>
    <p>学名: <i>{{ taxon.name }}</i></p>
    
    {% if taxon.default_photo.medium %}
    <img src="{{ taxon.default_photo.medium }}" alt="{{ taxon.name }}">
    {% endif %}
    
    <h2>分类信息</h2>
    <ul>
    {% for ancestor in ancestors %}
        <li>[{{ ancestor.rank }}] {{ ancestor.display_name }}</li>
    {% endfor %}
    </ul>
    
    <h2>统计数据</h2>
    <p>全球观察记录: {{ observation_count }} 条</p>
    
    {% if taxon.wikipedia.summary %}
    <h2>Wikipedia</h2>
    <p>{{ taxon.wikipedia.summary }}</p>
    <a href="{{ taxon.wikipedia.url }}" target="_blank">查看更多</a>
    {% endif %}
    
    <h2>最近观察记录</h2>
    <div class="observations">
    {% for obs in recent_observations %}
        <div class="observation">
            <a href="{{ obs.url }}">
                <img src="{{ obs.photos[0].medium if obs.photos else '' }}">
            </a>
            <p>{{ obs.observed_on }} by {{ obs.user.login }}</p>
        </div>
    {% endfor %}
    </div>
</body>
</html>
```

---

## 示例 11: Web 应用集成 (FastAPI)

```python
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from inaturalist_plugin.adapters.web_adapter import (
    INaturalistWebAdapter,
    create_fastapi_routes
)

app = FastAPI(title="自然物种查询门户")

# 创建适配器和路由
adapter = INaturalistWebAdapter()
inat_router = create_fastapi_routes(adapter)

# 注册路由
app.include_router(inat_router)

# 自定义端点
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head><title>自然物种查询门户</title></head>
        <body>
            <h1>欢迎使用自然物种查询门户</h1>
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="输入物种名称...">
                <button type="submit">搜索</button>
            </form>
        </body>
    </html>
    """

@app.get("/api/stats")
async def get_stats(taxon_id: int = Query(...)):
    """获取物种统计信息"""
    species_detail = adapter.get_species_detail(taxon_id)
    
    if not species_detail.get("success"):
        return {"error": "Species not found"}
    
    return {
        "taxon_id": taxon_id,
        "observation_count": species_detail["observation_count"],
        "ancestor_count": len(species_detail["ancestors"]),
        "child_count": len(species_detail["children"])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 示例 12: 数据导出

```python
import json
import csv
from inaturalist_plugin import INaturalistPlugin

plugin = INaturalistPlugin()

# 导出物种信息为 JSON
def export_species_json(taxon_id: int, filename: str):
    taxon = plugin.get_species_detail(taxon_id)
    
    data = {
        "id": taxon.id,
        "name": taxon.name,
        "display_name": taxon.display_name,
        "rank": taxon.rank,
        "observations_count": taxon.observations_count,
        "wikipedia_summary": taxon.wikipedia_summary,
        "photos": [
            {
                "url": p.large_url,
                "attribution": p.attribution,
                "license": p.license_code
            }
            for p in taxon.taxon_photos[:5]
        ]
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已导出到 {filename}")

# 导出观察记录为 CSV
def export_observations_csv(taxon_id: int, filename: str):
    observations = plugin.search_observations(
        taxon_id=taxon_id,
        quality_grade="research",
        has_photos=True,
        per_page=100
    )
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Date", "Location", "Latitude", "Longitude", 
                        "User", "Photo URL"])
        
        for obs in observations:
            photo_url = obs.best_photo.medium_url if obs.best_photo else ""
            writer.writerow([
                obs.id,
                obs.observed_on,
                obs.place_guess,
                obs.latitude,
                obs.longitude,
                obs.user_login,
                photo_url
            ])
    
    print(f"已导出 {len(observations)} 条记录到 {filename}")

# 使用示例
export_species_json(9083, "magpie.json")
export_observations_csv(9083, "magpie_observations.csv")
```

---

## 示例 13: 地图可视化（配合 folium）

```python
import folium
from inaturalist_plugin import INaturalistPlugin

plugin = INaturalistPlugin()

# 搜索喜鹊的观察记录
observations = plugin.search_observations(
    taxon_id=9083,
    lat=39.9,
    lng=116.4,
    radius=50,
    quality_grade="research",
    has_photos=True,
    per_page=50
)

# 创建地图
m = folium.Map(location=[39.9, 116.4], zoom_start=10)

# 添加标记
for obs in observations:
    if obs.latitude and obs.longitude:
        popup_html = f"""
        <b>{obs.display_name}</b><br>
        日期: {obs.observed_on}<br>
        观察者: {obs.user_login}<br>
        <a href="{obs.url}" target="_blank">查看详情</a><br>
        """
        
        if obs.best_photo:
            popup_html += f'<img src="{obs.best_photo.thumb_url}" width="100">'
        
        folium.Marker(
            location=[obs.latitude, obs.longitude],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=obs.display_name
        ).add_to(m)

# 保存地图
m.save("magpie_observations_map.html")
print("地图已保存到 magpie_observations_map.html")
```

---

## 更多示例

更多使用示例请参考：
- `examples/basic_usage.py` - 基础用法
- `examples/web_integration.py` - Web 集成
- `examples/batch_processing.py` - 批量处理
- `examples/data_analysis.py` - 数据分析
