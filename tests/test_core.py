#!/usr/bin/env python3
"""
iNaturalist 插件 - 核心功能测试
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inaturalist_plugin.core.client import create_client, INaturalistClient
from inaturalist_plugin.services.taxon_service import TaxonService
from inaturalist_plugin.services.observation_service import ObservationService
from inaturalist_plugin import INaturalistPlugin


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def run_test(self, test_name, test_func):
        """运行单个测试"""
        print(f"\n{'='*60}")
        print(f"🧪 测试: {test_name}")
        print(f"{'='*60}")
        
        self.start_time = time.time()
        try:
            test_func()
            elapsed = time.time() - self.start_time
            self.results.append({
                "name": test_name,
                "status": "PASSED",
                "elapsed": round(elapsed, 2),
                "error": None
            })
            print(f"✅ 通过 ({elapsed:.2f}s)")
            return True
        except Exception as e:
            elapsed = time.time() - self.start_time
            self.results.append({
                "name": test_name,
                "status": "FAILED",
                "elapsed": round(elapsed, 2),
                "error": str(e)
            })
            print(f"❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """打印测试摘要"""
        print(f"\n{'='*60}")
        print("📊 测试摘要")
        print(f"{'='*60}")
        
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        
        for r in self.results:
            icon = "✅" if r["status"] == "PASSED" else "❌"
            print(f"{icon} {r['name']}: {r['status']} ({r['elapsed']}s)")
        
        print(f"\n总计: {len(self.results)} | 通过: {passed} | 失败: {failed}")
        
        return self.results


def test_client_creation():
    """测试客户端创建"""
    client = create_client()
    assert client is not None
    assert isinstance(client, INaturalistClient)
    print("  ✓ 客户端创建成功")


def test_api_connection():
    """测试 API 连接"""
    client = create_client()
    
    # 简单的 API 调用测试
    response = client.get("/taxa", params={"q": "Pica pica", "per_page": 1})
    
    assert "results" in response
    assert isinstance(response["results"], list)
    print(f"  ✓ API 连接正常，返回 {len(response['results'])} 条结果")


def test_taxon_search():
    """测试物种搜索"""
    client = create_client()
    service = TaxonService(client)
    
    # 搜索喜鹊属 (Pica)
    results = service.search(q="Pica", rank="genus", per_page=5)
    
    assert len(results) > 0
    # 找到喜鹊属
    pica_taxon = None
    for t in results:
        if t.name == "Pica":
            pica_taxon = t
            break
    
    assert pica_taxon is not None, "未找到喜鹊属 (Pica)"
    taxon = pica_taxon
    assert taxon.name == "Pica"
    
    print(f"  ✓ 搜索成功: {taxon.display_name}")
    print(f"  ✓ 观察记录数: {taxon.observations_count}")


def test_taxon_detail():
    """测试物种详情获取"""
    client = create_client()
    service = TaxonService(client)
    
    # 使用喜鹊属的 ID (8318)
    taxon = service.get_by_id(8318)
    
    assert taxon is not None
    assert taxon.id == 8318
    assert taxon.name == "Pica"
    
    print(f"  ✓ 详情获取成功")
    print(f"  ✓ 学名: {taxon.name}")
    print(f"  ✓ 分类等级: {taxon.rank}")
    print(f"  ✓ 观察数: {taxon.observations_count}")
    
    if taxon.wikipedia_summary:
        print(f"  ✓ Wikipedia摘要长度: {len(taxon.wikipedia_summary)} 字符")


def test_taxon_autocomplete():
    """测试自动补全"""
    client = create_client()
    service = TaxonService(client)
    
    suggestions = service.autocomplete(q="ma", per_page=10)
    
    assert len(suggestions) > 0
    print(f"  ✓ 自动补全返回 {len(suggestions)} 条建议")
    
    for taxon in suggestions[:3]:
        print(f"    - {taxon.display_name}")


def test_observation_search():
    """测试观察记录搜索"""
    client = create_client()
    service = ObservationService(client)
    
    observations = service.search(
        taxon_id=9083,
        quality_grade="research",
        has_photos=True,
        per_page=5
    )
    
    assert len(observations) > 0
    print(f"  ✓ 找到 {len(observations)} 条观察记录")
    
    obs = observations[0]
    print(f"  ✓ 观察 ID: {obs.id}")
    print(f"  ✓ 日期: {obs.observed_on}")
    print(f"  ✓ 照片数: {obs.photo_count}")


def test_location_search():
    """测试位置搜索"""
    client = create_client()
    service = ObservationService(client)
    
    # 搜索天安门周围
    observations = service.search(
        lat=39.9042,
        lng=116.4074,
        radius=10,
        quality_grade="research",
        has_photos=True,
        per_page=5
    )
    
    print(f"  ✓ 位置搜索返回 {len(observations)} 条结果")
    
    if observations:
        obs = observations[0]
        print(f"  ✓ 最近观察: {obs.display_name}")
        print(f"  ✓ 位置: {obs.place_guess}")


def test_plugin_integration():
    """测试主插件集成"""
    plugin = INaturalistPlugin()
    
    # 测试搜索
    results = plugin.search_species("喜鹊", per_page=3)
    assert len(results) > 0
    print(f"  ✓ 插件搜索成功: {len(results)} 个结果")
    
    # 测试详情 (使用喜鹊属 ID: 8318)
    taxon = plugin.get_species_detail(8318)
    assert taxon is not None
    print(f"  ✓ 插件详情获取成功: {taxon.name}")
    
    # 测试观察搜索
    observations = plugin.search_observations(
        taxon_id=8318,
        quality_grade="research",
        per_page=3
    )
    print(f"  ✓ 插件观察搜索成功: {len(observations)} 条")


def test_image_urls():
    """测试图片 URL 获取"""
    plugin = INaturalistPlugin()
    
    images = plugin.get_species_image_urls(
        taxon_id=8318,
        size="medium",
        max_images=3
    )
    
    assert len(images) > 0
    print(f"  ✓ 获取到 {len(images)} 张图片 URL")
    
    for i, img in enumerate(images[:2]):
        print(f"  ✓ 图片 {i+1}: {img['url'][:60]}...")
        print(f"    拍摄者: {img['attribution'][:50]}...")


def test_species_counts():
    """测试物种统计"""
    client = create_client()
    service = ObservationService(client)
    
    # 获取物种统计
    counts = service.get_species_counts(
        taxon_id=8318,
        hrank="species"
    )
    
    print(f"  ✓ 获取到 {len(counts)} 条统计")
    
    if counts:
        top = counts[0]
        print(f"  ✓ 顶部物种: {top['taxon']['name']} ({top['count']} 次观察)")


def test_pagination():
    """测试分页功能"""
    client = create_client()
    
    # 测试分页获取
    results = client.paginate(
        "/observations",
        params={
            "taxon_id": 8318,
            "quality_grade": "research",
            "has_photos": "true"
        },
        per_page=10,
        max_pages=2
    )
    
    print(f"  ✓ 分页获取到 {len(results)} 条结果")


def save_test_results(results, output_dir="outputs"):
    """保存测试结果到文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    output = {
        "timestamp": timestamp,
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASSED"),
        "failed": sum(1 for r in results if r["status"] == "FAILED"),
        "results": results
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 测试结果已保存到: {filepath}")
    return filepath


if __name__ == "__main__":
    print("\n" + "🌿 " * 25)
    print("  iNaturalist 插件 - 核心功能测试")
    print("🌿 " * 25 + "\n")
    
    runner = TestRunner()
    
    # 运行所有测试
    tests = [
        ("客户端创建", test_client_creation),
        ("API 连接测试", test_api_connection),
        ("物种搜索", test_taxon_search),
        ("物种详情获取", test_taxon_detail),
        ("自动补全功能", test_taxon_autocomplete),
        ("观察记录搜索", test_observation_search),
        ("位置搜索", test_location_search),
        ("图片 URL 获取", test_image_urls),
        ("物种统计", test_species_counts),
        ("分页功能", test_pagination),
        ("插件集成测试", test_plugin_integration),
    ]
    
    for test_name, test_func in tests:
        runner.run_test(test_name, test_func)
        time.sleep(0.5)  # 避免请求过快
    
    # 打印摘要
    results = runner.print_summary()
    
    # 保存结果
    save_test_results(results)
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
