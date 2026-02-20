#!/usr/bin/env python3
"""
iNaturalist 自然物种查询门户 - Flask 后端

提供 API 接口和静态文件服务
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from inaturalist_plugin import INaturalistPlugin
from inaturalist_plugin.adapters.web_adapter import INaturalistWebAdapter

# 创建 Flask 应用
app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
CORS(app)

# 初始化插件
plugin = INaturalistPlugin()
adapter = INaturalistWebAdapter()

# ============= 页面路由 =============

@app.route("/")
def index():
    """首页"""
    return render_template("index.html")

@app.route("/search")
def search_page():
    """搜索页面"""
    query = request.args.get("q", "")
    return render_template("search.html", query=query)

@app.route("/species/<int:taxon_id>")
def species_detail_page(taxon_id):
    """物种详情页面"""
    return render_template("species_detail.html", taxon_id=taxon_id)

@app.route("/observations")
def observations_page():
    """观察记录页面"""
    taxon_id = request.args.get("taxon_id", type=int)
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    return render_template("observations.html", 
                         taxon_id=taxon_id, 
                         lat=lat, 
                         lng=lng)

@app.route("/map")
def map_page():
    """地图页面"""
    return render_template("map.html")

# ============= API 路由 =============

@app.route("/api/search")
def api_search():
    """搜索物种"""
    query = request.args.get("q", "")
    rank = request.args.get("rank")
    per_page = min(int(request.args.get("per_page", 30)), 200)
    
    if not query:
        return jsonify({"success": False, "error": "Query parameter required"})
    
    result = adapter.search_species(query, rank=rank, per_page=per_page)
    return jsonify(result)

@app.route("/api/species/<int:taxon_id>")
def api_species_detail(taxon_id):
    """获取物种详情"""
    result = adapter.get_species_detail(taxon_id)
    return jsonify(result)

@app.route("/api/species/<int:taxon_id>/images")
def api_species_images(taxon_id):
    """获取物种图片"""
    size = request.args.get("size", "medium")
    max_images = min(int(request.args.get("max", 20)), 50)
    
    result = adapter.get_species_images(taxon_id, size=size, max_images=max_images)
    return jsonify(result)

@app.route("/api/autocomplete")
def api_autocomplete():
    """自动补全建议"""
    query = request.args.get("q", "")
    per_page = min(int(request.args.get("per_page", 10)), 20)
    
    if not query or len(query) < 2:
        return jsonify({"success": True, "query": query, "suggestions": []})
    
    result = adapter.autocomplete_species(query, per_page=per_page)
    return jsonify(result)

@app.route("/api/observations")
def api_observations():
    """搜索观察记录"""
    taxon_id = request.args.get("taxon_id", type=int)
    place_id = request.args.get("place_id", type=int)
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", type=float, default=10)
    quality_grade = request.args.get("quality_grade", "research")
    per_page = min(int(request.args.get("per_page", 30)), 200)
    
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

@app.route("/api/observations/<int:observation_id>")
def api_observation_detail(observation_id):
    """获取观察记录详情"""
    result = adapter.get_observation_detail(observation_id)
    return jsonify(result)

@app.route("/api/location/species")
def api_location_species():
    """获取位置周围的物种"""
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", type=float, default=10)
    per_page = min(int(request.args.get("per_page", 30)), 100)
    
    if lat is None or lng is None:
        return jsonify({"success": False, "error": "lat and lng parameters required"})
    
    result = adapter.get_species_by_location(lat, lng, radius, per_page)
    return jsonify(result)

@app.route("/api/taxonomy/<int:taxon_id>/children")
def api_taxonomy_children(taxon_id):
    """获取子分类群"""
    rank = request.args.get("rank")
    
    from inaturalist_plugin.core.client import create_client
    from inaturalist_plugin.services.taxon_service import TaxonService
    
    client = create_client()
    service = TaxonService(client)
    children = service.get_children(taxon_id, rank=rank)
    
    return jsonify({
        "success": True,
        "parent_id": taxon_id,
        "total": len(children),
        "results": [
            {
                "id": t.id,
                "name": t.name,
                "rank": t.rank,
                "display_name": t.display_name,
                "observations_count": t.observations_count,
                "default_photo": t.default_photo.square_url if t.default_photo else None
            }
            for t in children
        ]
    })

@app.route("/api/taxonomy/<int:taxon_id>/ancestors")
def api_taxonomy_ancestors(taxon_id):
    """获取祖先分类群"""
    from inaturalist_plugin.core.client import create_client
    from inaturalist_plugin.services.taxon_service import TaxonService
    
    client = create_client()
    service = TaxonService(client)
    ancestors = service.get_ancestors(taxon_id)
    
    return jsonify({
        "success": True,
        "taxon_id": taxon_id,
        "total": len(ancestors),
        "results": [
            {
                "id": t.id,
                "name": t.name,
                "rank": t.rank,
                "display_name": t.display_name
            }
            for t in ancestors
        ]
    })

# ============= 错误处理 =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

# ============= 主程序 =============

if __name__ == "__main__":
    print("="*60)
    print("🌿 iNaturalist 自然物种查询门户")
    print("="*60)
    print("访问地址: http://localhost:5000")
    print("="*60)
    
    # 确保模板文件夹存在
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    
    app.run(debug=True, host="0.0.0.0", port=5000)
