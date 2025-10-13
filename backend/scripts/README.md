# 横幅管理脚本使用指南

## 概述

`seed_banners.py` 是一个功能完整的横幅数据管理工具,支持添加、查看、删除横幅数据。

## 安装依赖

```bash
cd backend
source venv/bin/activate
```

## 使用方法

### 1. 查看所有横幅

```bash
python scripts/seed_banners.py list
```

限制显示数量:
```bash
python scripts/seed_banners.py list -n 10
```

### 2. 添加示例横幅

添加预设的示例横幅(跳过已存在的):
```bash
python scripts/seed_banners.py add
```

强制添加(先清空所有横幅再添加):
```bash
python scripts/seed_banners.py add --force
```

### 3. 清空所有横幅

```bash
python scripts/seed_banners.py clear
```

跳过确认提示:
```bash
python scripts/seed_banners.py clear -y
```

### 4. 添加限时横幅

创建一个7天有效的限时横幅:
```bash
python scripts/seed_banners.py add-timed \
  "新年促销活动" \
  "https://example.com/image.jpg" \
  "/promo/newyear" \
  --days 7 \
  --sort-order 200 \
  --description "新年特惠,全场8折"
```

参数说明:
- `title`: 横幅标题(必需)
- `image_url`: 图片URL(必需)
- `link_url`: 点击跳转链接(必需)
- `--days`: 有效天数(默认7天)
- `--sort-order`: 排序优先级(默认100)
- `--description`: 横幅描述(可选)

## 预设横幅列表

脚本内置了8个示例横幅:

1. **精彩电影推荐 - 星际穿越** (排序: 100)
2. **热门剧集 - 权力的游戏** (排序: 90)
3. **动画精选 - 千与千寻** (排序: 80)
4. **纪录片 - 地球脉动** (排序: 70)
5. **新片上线 - 速度与激情** (排序: 60)
6. **经典回顾 - 肖申克的救赎** (排序: 50)
7. **悬疑惊悚 - 致命魔术** (排序: 40)
8. **科幻巨制 - 黑客帝国** (排序: 30)

所有示例横幅都使用了 Unsplash 的高质量图片,尺寸为 1920x600。

## 当前数据库状态

当前数据库中有 **21个活跃横幅**:

### 新增横幅 (2025-10-13):

1. 动作大片 - 碟中谍系列 (200)
2. 奇幻史诗 - 指环王三部曲 (195)
3. 漫威宇宙 - 复仇者联盟 (190)
4. 科幻经典 - 银翼杀手2049 (185)
5. 惊悚悬疑 - 盗梦空间 (180)
6. 温情治愈 - 千与千寻 (175)
7. 犯罪剧情 - 教父三部曲 (170)
8. 喜剧佳作 - 三傻大闹宝莱坞 (165)
9. 战争史诗 - 敦刻尔克 (160)
10. 爱情经典 - 泰坦尼克号 (155)
11. 恐怖惊悚 - 寂静之地 (150)
12. 音乐传记 - 波西米亚狂想曲 (145)
13. 西部片 - 荒野猎人 (140)
14. 体育励志 - 摔跤吧！爸爸 (135)
15. 动画力作 - 寻梦环游记 (130)

### 原有横幅:

16. 精彩电影推荐 - 星际穿越 (100)
17. 热门剧集 - 权力的游戏 (90)
18. 动画精选 - 千与千寻 (80)
19. 纪录片 - 地球脉动 (70)
20. 新片上线 - 速度与激情 (60)
21. 经典回顾 - 肖申克的救赎 (50)

## 高级用法

### 详细输出模式

使用 `-v` 或 `--verbose` 参数查看详细日志:
```bash
python scripts/seed_banners.py -v add
```

### 自定义横幅数据

修改 `BannerSeeder.SAMPLE_BANNERS` 列表来自定义预设横幅:

```python
SAMPLE_BANNERS = [
    {
        'title': '自定义横幅标题',
        'image_url': 'https://example.com/image.jpg',
        'link_url': '/custom/link',
        'video_id': None,  # 可选,关联视频ID
        'description': '横幅描述',
        'status': BannerStatus.ACTIVE,
        'sort_order': 100,
    },
]
```

## 图片资源

推荐的图片来源:
- **Unsplash**: https://unsplash.com (免费高质量图片)
- **Pexels**: https://www.pexels.com (免费视频和图片)

横幅图片建议尺寸:
- **桌面**: 1920x600 (16:5 比例)
- **移动**: 750x375 (2:1 比例)

## 注意事项

1. 横幅的 `sort_order` 值越大,显示优先级越高
2. 使用 `--force` 参数会删除所有现有横幅,请谨慎使用
3. 图片URL应该使用HTTPS协议以确保安全性
4. 建议定期清理不再使用的横幅数据

## 故障排查

### 问题: 横幅重复

如果添加横幅时遇到重复标题,脚本会自动跳过。如果需要强制添加,使用:
```bash
python scripts/seed_banners.py add --force
```

### 问题: 数据库连接失败

确保:
1. PostgreSQL服务正在运行
2. `.env` 文件配置正确
3. 虚拟环境已激活

### 问题: 图片无法显示

检查:
1. 图片URL是否可访问
2. 是否使用了HTTPS
3. 图片尺寸是否合适

## 相关文档

- [横幅管理API文档](../app/admin/banners.py)
- [前端横幅管理页面](../../admin-frontend/src/pages/Banners/)
- [横幅预览组件](../../admin-frontend/src/pages/Banners/BannerPreview.tsx)
