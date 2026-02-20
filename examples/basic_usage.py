#!/usr/bin/env python3
"""
iNaturalist 插件基础使用示例

演示如何使用插件进行物种搜索、获取详情和图片下载
"""

import sys
sys.path.insert(0, '..')

from inaturalist_plugin import INaturalistPlugin


def demo_search_species():
    """演示物种搜索"""
    print("=" * 60)
    print("示例 1: 物种搜索")
    print("=" * 60)
    
    plugin = INaturalistPlugin()
    
    # 搜索喜鹊
    results = plugin.search_species("喜鹊", per_page=5)
    
    print(f"\n找到 {len(results)} 个结果:\n")
    
    for taxon in results:
        print(f"  ID: {taxon.id}")
        print(f"  学名: {taxon.name}")
        print(f"  显示名称: {taxon.display_name}")
        print(f"  分类等级: {taxon.rank}")
        print(f"  观察记录数: {taxon.observations_count}")
        if taxon.default_photo:
            print(f"  默认图片: {taxon.default_photo.medium_url}")
        print(f"  {'-' * 40}")


def demo_get_species_detail():
    """演示获取物种详情"""
    print("\n" + "=" * 60)
    print("示例 2: 获取物种详情")
    print("=" * 60)
    
    plugin = INaturalistPlugin()
    
    # 获取喜鹊的详细信息
    taxon = plugin.get_species_detail(9083)
    
    if taxon:
        print(f"\n物种详情:")
        print(f"  学名: {taxon.name}")
        print(f"  中文名: {taxon.chinese_common_name}")
        print(f"  英文名: {taxon.english_common_name}")
        print(f"  分类等级: {taxon.rank}")
        print(f"  观察记录数: {taxon.observations_count}")
        print(f"  保护状态: {taxon.conservation_status_name or '无'}")
        
        if taxon.wikipedia_summary:
            print(f"\n  Wikipedia 摘要:")
            print(f"    {taxon.wikipedia_summary[:150]}...")
        
        print(f"\n  分类路径:")
        if taxon.ancestor_ids:
            print(f"    {' > '.join(str(a) for a in taxon.ancestor_ids)} > {taxon.id}")


def demo_search_observations():
    """演示搜索观察记录"""
    print("\n" + "=" * 60)
    print("示例 3: 搜索观察记录")
    print("=" * 60)
    
    plugin = INaturalistPlugin()
    
    # 搜索喜鹊的研究级观察记录
    observations = plugin.search_observations(
        taxon_id=9083,
        quality_grade="research",
        has_photos=True,
        per_page=3
    )
    
    print(f"\n找到 {len(observations)} 条研究级观察记录:\n")
    
    for i, obs in enumerate(observations, 1):
        print(f"  [{i}] 观察 ID: {obs.id}")
        print(f"      日期: {obs.observed_on}")
        print(f"      地点: {obs.place_guess}")
        print(f"      坐标: ({obs.latitude}, {obs.longitude})")
        print(f"      观察者: {obs.user_login}")
        print(f"      照片数: {obs.photo_count}")
        
        if obs.best_photo:
            print(f"      图片: {obs.best_photo.medium_url}")
        print()


def demo_get_image_urls():
    """演示获取图片 URL"""
    print("\n" + "=" * 60)
    print("示例 4: 获取物种图片 URL")
    print("=" * 60)
    
    plugin = INaturalistPlugin()
    
    # 获取喜鹊的图片 URL
    images = plugin.get_species_image_urls(
        taxon_id=9083,
        size="medium",
        max_images=3
    )
    
    print(f"\n找到 {len(images)} 张图片:\n")
    
    for i, img in enumerate(images, 1):
        print(f"  [{i}] URL: {img['url']}")
        print(f"      拍摄者: {img['attribution']}")
        print(f"      许可证: {img['license']}")
        print(f"      观察记录: https://www.inaturalist.org/observations/{img['observation_id']}")
        print()


def demo_location_search():
    """演示位置搜索"""
    print("\n" + "=" * 60)
    print("示例 5: 位置周围物种搜索")
    print("=" * 60)
    
    plugin = INaturalistPlugin()
    
    # 搜索天安门周围10公里内的研究级观察
    print("\n搜索北京市中心周围10公里内的观察记录...")
    observations = plugin.search_observations(
        lat=39.9042,
        lng=116.4074,
        radius=10,
        quality_grade="research",
        has_photos=True,
        per_page=5
    )
    
    print(f"\n找到 {len(observations)} 条观察记录:\n")
    
    for obs in observations:
        print(f"  物种: {obs.display_name}")
        print(f"  地点: {obs.place_guess}")
        print(f"  日期: {obs.observed_on}")
        print(f"  {'-' * 40}")


def demo_autocomplete():
    """演示自动补全"""
    print("\n" + "=" * 60)
    print("示例 6: 自动补全搜索")
    print("=" * 60)
    
    plugin = INaturalistPlugin()
    
    # 搜索建议
    query = "ma"
    suggestions = plugin.autocomplete_species(query, per_page=10)
    
    print(f"\n'{query}' 的搜索建议:\n")
    
    for taxon in suggestions:
        print(f"  - {taxon.display_name} (ID: {taxon.id})")


if __name__ == "__main__":
    print("\n" + "🌿 " * 20)
    print("  iNaturalist 数据插件 - 基础使用示例")
    print("🌿 " * 20 + "\n")
    
    try:
        demo_search_species()
        demo_get_species_detail()
        demo_search_observations()
        demo_get_image_urls()
        demo_location_search()
        demo_autocomplete()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
