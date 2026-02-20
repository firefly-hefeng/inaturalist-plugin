# 更新日志 (Changelog)

## [1.0.0] - 2026-02-20

### ✅ 初始版本发布

### 核心功能
- 实现完整的 iNaturalist API v1 封装
- 物种搜索和详细信息获取
- 观察记录查询（支持地理位置筛选）
- 多尺寸图片 URL 获取和本地下载
- 分类树获取（祖先和子分类群）
- 自动补全建议功能
- 智能速率限制和错误重试

### 插件模块
- `core/client.py` - API 客户端，支持自动重试和速率限制
- `models/taxon.py` - 物种数据模型
- `models/observation.py` - 观察记录模型
- `services/taxon_service.py` - 物种服务接口
- `services/observation_service.py` - 观察记录服务
- `utils/image_utils.py` - 图片下载和缓存工具
- `adapters/web_adapter.py` - Flask/FastAPI 适配器

### 测试
- 完整的测试套件（11 项测试）
- 100% 测试通过率
- 包含单元测试和集成测试

### 前端应用
- Flask Web 应用
- 响应式设计（Bootstrap 5）
- 交互式地图（Leaflet.js）
- 物种搜索和详情展示
- 观察记录浏览

### 文档
- API 参考文档
- 使用示例
- 接口调用说明
- 前端使用指南

### 修复
- 修复 URL 拼接问题（client.py）
- 修复 typing 导入问题（__init__.py）
- 更新文档中的物种 ID（9083 → 8318）

### 已知问题
- 无

---

## 版本说明

### 物种 ID 说明
本项目文档中使用的主要测试物种 ID：
- **8318** - 喜鹊属 (*Pica*)
- **891704** - 喜鹊 (*Pica pica*)
- **11901** - 麻雀 (*Passer montanus*)
- **14825** - 家燕 (*Hirundo rustica*)

测试中发现原 ID **9083** 实际上是北美红雀 (*Cardinalis cardinalis*)，已在所有文档中修正为喜鹊属 ID **8318**。

---

## 计划功能

### 未来版本
- [ ] 添加用户认证支持
- [ ] 实现本地数据库缓存
- [ ] 添加数据分析图表功能
- [ ] 支持离线模式
- [ ] 多语言支持
- [ ] 移动端 App 适配

---

## 如何更新

```bash
# 获取最新版本
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 运行测试
python tests/test_core.py
```

---

**维护者**: Nature Portal Team  
**许可证**: MIT License
