# iNaturalist 数据插件

一个功能完整的 Python 插件，用于获取 [iNaturalist](https://www.inaturalist.org/) 平台的物种详细信息和图片数据。专为自然科学查询门户网站设计。

## 功能特性

- 🔍 **物种搜索**: 支持按名称、分类等级、标志性类群搜索
- 📸 **图片获取**: 多尺寸图片 URL 获取和本地缓存下载
- 📍 **位置查询**: 支持按坐标和半径搜索周围物种
- 🔬 **观察记录**: 获取研究级观察记录及详细信息
- 🌳 **分类树**: 获取完整分类路径和子分类群
- 🚀 **Web 集成**: 内置 Flask 和 FastAPI 适配器
- 💾 **数据缓存**: 智能图片缓存和速率限制

## 快速安装

```bash
# 克隆项目
git clone https://github.com/yourusername/inaturalist-plugin.git
cd inaturalist-plugin

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

```python
from inaturalist_plugin import INaturalistPlugin

# 创建插件实例
plugin = INaturalistPlugin()

# 搜索物种
results = plugin.search_species("喜鹊")
for taxon in results:
    print(f"{taxon.display_name} - {taxon.observations_count} 条观察记录")

# 获取详细信息 (以喜鹊属 Pica 为例，ID: 8318)
details = plugin.get_species_detail(8318)
print(f"学名: {details.name}")
print(f"Wikipedia: {details.wikipedia_summary}")

# 下载图片
images = plugin.download_species_images(8318, size="large", max_images=5)
print(f"已下载 {len(images)} 张图片")

# 搜索观察记录
observations = plugin.search_observations(
    taxon_id=8318,
    lat=39.9,
    lng=116.4,
    radius=10,
    per_page=10
)
```

## 项目结构

```
inaturalist/
├── inaturalist_plugin/      # 核心插件
│   ├── __init__.py          # 主插件类
│   ├── core/
│   │   └── client.py        # API 客户端
│   ├── models/              # 数据模型
│   │   ├── taxon.py         # 物种模型
│   │   └── observation.py   # 观察记录模型
│   ├── services/            # 服务接口
│   │   ├── taxon_service.py
│   │   └── observation_service.py
│   ├── utils/
│   │   └── image_utils.py   # 图片工具
│   └── adapters/
│       └── web_adapter.py   # Web 适配器
│
├── tests/                   # 测试套件
│   ├── test_core.py         # 核心测试
│   └── TEST_REPORT.md       # 测试报告
│
├── frontend/                # 独立前端应用
│   ├── app.py               # Flask 应用
│   ├── templates/           # HTML 模板
│   └── static/              # CSS/JS
│
├── examples/                # 使用示例
├── outputs/                 # 测试结果
└── docs/                    # 文档
```

## API 接口概览

### 物种接口

| 方法 | 说明 |
|------|------|
| `search_species(query)` | 搜索物种 |
| `get_species_detail(id)` | 获取物种详情 |
| `autocomplete_species(query)` | 自动补全建议 |
| `get_species_image_urls(id)` | 获取图片 URL |
| `download_species_images(id)` | 下载物种图片 |

### 观察记录接口

| 方法 | 说明 |
|------|------|
| `search_observations(**kwargs)` | 搜索观察记录 |
| `get_observation(id)` | 获取观察详情 |
| `get_species_by_location(lat, lng)` | 获取位置周围物种 |

### Web 适配器接口

| 方法 | 说明 |
|------|------|
| `search_species(query)` | 返回 JSON 格式结果 |
| `get_species_detail(id)` | 返回完整物种信息 |
| `get_species_images(id)` | 返回图片列表 |

## 完整文档

- [API 参考文档](API_REFERENCE.md) - 详细的接口说明
- [使用示例](EXAMPLES.md) - 丰富的代码示例
- [接口使用介绍](USAGE.md) - 数据接口和调用方式
- [测试报告](tests/TEST_REPORT.md) - 测试结果
- [前端说明](frontend/README.md) - Web 应用使用指南

## Web 集成示例

### Flask

```python
from flask import Flask
from inaturalist_plugin.adapters.web_adapter import (
    INaturalistWebAdapter, create_flask_routes
)

app = Flask(__name__)
adapter = INaturalistWebAdapter()
create_flask_routes(app, adapter)

if __name__ == "__main__":
    app.run(debug=True)
```

访问 `http://localhost:5000/api/inat/species/search?q=喜鹊`

### FastAPI

```python
from fastapi import FastAPI
from inaturalist_plugin.adapters.web_adapter import (
    INaturalistWebAdapter, create_fastapi_routes
)

app = FastAPI()
adapter = INaturalistWebAdapter()
router = create_fastapi_routes(adapter)
app.include_router(router)
```

## 测试

运行测试套件：

```bash
cd tests
python test_core.py
```

测试结果将保存到 `outputs/` 目录。

## 前端应用

项目包含一个完整的 Web 前端应用：

```bash
cd frontend
pip install flask flask-cors
python app.py
```

访问 http://localhost:5000 查看物种查询门户。

功能包括：
- 物种搜索与自动补全
- 物种详情展示
- 观察记录浏览
- 交互式地图

## 更新日志

### v1.0.0 (2026-02-20)
- ✅ 初始版本发布
- ✅ 完整 API 接口实现
- ✅ 测试套件（11 项测试全部通过）
- ✅ Web 前端应用
- ✅ 图片下载和缓存功能
- ✅ Flask/FastAPI 适配器

## 许可证

MIT License

## 致谢

- 数据来源: [iNaturalist](https://www.inaturalist.org/)
- API 文档: [iNaturalist API v1](https://api.inaturalist.org/v1/docs/)
- 感谢所有为 iNaturalist 贡献数据的自然观察者
