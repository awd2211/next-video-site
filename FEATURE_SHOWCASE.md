# VideoSite 功能展示手册

## 📋 本次更新概览

本次更新完成了两个重要功能模块：
1. **搜索增强功能** - 高级筛选和多维度排序
2. **智能推荐系统** - 个性化推荐和相似视频推荐

---

## 🔍 一、搜索增强功能

### 功能入口
- 访问路径：导航栏搜索框 → 搜索结果页
- URL示例：`http://localhost:3000/search?q=关键词`

### 核心功能

#### 1.1 基础搜索
**使用方法**：
1. 在页面顶部搜索框输入关键词
2. 按Enter或点击搜索按钮
3. 系统搜索标题、原标题、描述中包含关键词的视频

**搜索范围**：
- 视频标题（中文/英文）
- 原标题
- 视频描述

#### 1.2 高级筛选

**筛选维度**：

| 筛选器 | 选项 | 说明 |
|--------|------|------|
| **排序方式** | 最新发布 / 最多观看 / 最高评分 | 决定结果排序规则 |
| **分类** | 动作、喜剧、剧情等 | 按视频类型筛选 |
| **地区** | 美国、中国、日本等 | 按制作国家筛选 |
| **年份** | 2025-1975 | 按发行年份筛选 |
| **最低评分** | 9分以上、8分以上等 | 按用户评分筛选 |

**使用示例**：
```
场景1：寻找最新的美国动作片
- 排序：最新发布
- 分类：动作
- 地区：美国

场景2：寻找高分经典日本电影
- 排序：最高评分
- 分类：剧情
- 地区：日本
- 最低评分：8分以上
```

#### 1.3 URL分享功能

**特性**：
- 所有筛选条件都会保存在URL参数中
- 可以直接复制URL分享给他人
- 刷新页面保持筛选状态

**URL示例**：
```
http://localhost:3000/search?q=电影&category_id=1&country_id=2&year=2024&min_rating=8&sort_by=view_count
```

**参数说明**：
- `q`: 搜索关键词
- `category_id`: 分类ID
- `country_id`: 国家ID
- `year`: 年份
- `min_rating`: 最低评分
- `sort_by`: 排序方式

#### 1.4 一键清除筛选

**使用方法**：
- 点击"清除所有筛选"按钮
- 所有筛选条件重置为默认值
- 仅保留搜索关键词

### 技术特性

**前端**：
- 实时筛选，无需刷新页面
- 响应式设计，移动端友好
- TanStack Query智能缓存

**后端**：
- 复杂SQL查询优化
- Redis缓存（5分钟TTL）
- 支持分页（最多100条/页）

---

## 🎯 二、智能推荐系统

### 2.1 首页个性化推荐

#### 功能位置
- 页面：首页（http://localhost:3000）
- 板块：第二个板块"为你推荐"

#### 推荐策略

**已登录用户**：
```
推荐来源 = 60% 协同过滤 + 40% 内容推荐
```

1. **协同过滤部分**（60%）：
   - 找到有相似观看行为的用户
   - 推荐这些用户喜欢的视频
   - 基于收藏和评分数据

2. **内容推荐部分**（40%）：
   - 分析你最近20个观看记录
   - 提取偏好：分类、演员、导演
   - 推荐符合偏好的高评分视频

**未登录用户**：
```
推荐来源 = 100% 热门视频
```
- 按观看次数和评分综合排序
- 显示平台最受欢迎的内容

#### 推荐数量
- 首页显示：12个视频
- 4列网格布局（桌面端）

#### 更新频率
- 缓存时间：10分钟
- 用户行为变化后自动更新推荐

### 2.2 视频详情页相似推荐

#### 功能位置
- 页面：任意视频详情页
- 板块：评论区下方"相似推荐"

#### 推荐算法

**相似度计算公式**：
```
总分 = 分类相似度 × 0.4
     + 演员相似度 × 0.3
     + 导演相似度 × 0.2
     + 国家相同 × 0.05
     + 评分相近 × 0.05
```

**相似度计算方法**（Jaccard系数）：
```
相似度 = 共同元素数 / 总元素数

示例：
当前视频分类：[动作, 科幻, 冒险]
候选视频分类：[科幻, 冒险, 惊悚]

共同分类：{科幻, 冒险} = 2个
总分类数：{动作, 科幻, 冒险, 惊悚} = 4个
分类相似度 = 2/4 = 0.5
```

#### 推荐特点

**优先级**：
1. 相同分类的视频（权重最高）
2. 相同演员的视频
3. 相同导演的视频
4. 相同国家的视频
5. 评分相近的视频

**排除规则**：
- 自动排除当前观看的视频
- 可选排除已观看的视频

#### 推荐数量
- 详情页显示：6个视频
- 6列网格布局（桌面端）

#### 缓存优化
- 缓存时间：30分钟
- 相同视频的推荐结果重用

### 2.3 推荐API端点

#### API列表

**1. 个性化推荐**
```bash
GET /api/v1/recommendations/personalized
参数：
  - limit: 推荐数量（默认20，最大100）
  - exclude_ids: 排除的视频ID（逗号分隔）
  
示例：
curl "http://localhost:8001/api/v1/recommendations/personalized?limit=12"
```

**2. 相似视频推荐**
```bash
GET /api/v1/recommendations/similar/{video_id}
参数：
  - limit: 推荐数量（默认10，最大50）
  - exclude_ids: 排除的视频ID
  
示例：
curl "http://localhost:8001/api/v1/recommendations/similar/1?limit=6"
```

**3. 首页推荐**
```bash
GET /api/v1/recommendations/for-you
参数：
  - limit: 推荐数量（默认20，最大100）
  
示例：
curl "http://localhost:8001/api/v1/recommendations/for-you?limit=12"
```

---

## 🧪 三、功能测试指南

### 3.1 搜索功能测试

**测试步骤**：

1. **基础搜索测试**
```
步骤：
1. 访问 http://localhost:3000
2. 在搜索框输入"电影"
3. 按Enter键
4. 验证：显示包含"电影"的搜索结果

预期结果：
- 显示搜索结果数量
- 显示匹配的视频卡片
- URL变为 /search?q=电影
```

2. **高级筛选测试**
```
步骤：
1. 在搜索结果页
2. 选择"分类" = "动作"
3. 选择"排序方式" = "最高评分"
4. 验证：结果立即更新

预期结果：
- 仅显示动作分类的视频
- 按评分从高到低排序
- URL包含 &category_id=1&sort_by=average_rating
```

3. **URL分享测试**
```
步骤：
1. 设置多个筛选条件
2. 复制浏览器地址栏URL
3. 在新标签页打开该URL
4. 验证：筛选条件保持一致

预期结果：
- 所有筛选条件正确应用
- 搜索结果一致
```

4. **清除筛选测试**
```
步骤：
1. 设置多个筛选条件
2. 点击"清除所有筛选"按钮
3. 验证：筛选条件重置

预期结果：
- 所有下拉框回到默认值
- 仅保留搜索关键词
- URL仅包含 ?q=关键词
```

### 3.2 推荐功能测试

**测试步骤**：

1. **首页推荐测试（未登录）**
```
步骤：
1. 清除所有cookies（退出登录）
2. 访问 http://localhost:3000
3. 查看"为你推荐"板块

预期结果：
- 显示热门视频推荐
- 推荐基于观看次数和评分
```

2. **首页推荐测试（已登录）**
```
步骤：
1. 登录账号
2. 观看3-5个不同类型的视频
3. 返回首页刷新
4. 查看"为你推荐"板块

预期结果：
- 推荐视频与观看历史相关
- 包含相似分类/演员的视频
```

3. **相似视频推荐测试**
```
步骤：
1. 访问任意视频详情页
2. 滚动到页面底部
3. 查看"相似推荐"板块

预期结果：
- 显示6个相似视频
- 推荐视频与当前视频特征相似
- 不包含当前视频本身
```

4. **推荐API测试**
```bash
# 测试个性化推荐
curl -s "http://localhost:8001/api/v1/recommendations/personalized?limit=5" | jq

# 测试相似视频推荐
curl -s "http://localhost:8001/api/v1/recommendations/similar/1?limit=5" | jq

# 测试首页推荐
curl -s "http://localhost:8001/api/v1/recommendations/for-you?limit=5" | jq
```

预期结果：
- 返回JSON格式的视频列表
- 包含视频完整信息
- 数量符合limit参数

---

## 📊 四、性能测试

### 4.1 搜索性能

**测试场景**：
```bash
# 1. 无筛选搜索
time curl "http://localhost:8001/api/v1/search?q=电影"

# 2. 多条件筛选
time curl "http://localhost:8001/api/v1/search?q=电影&category_id=1&country_id=2&year=2024&min_rating=8"

# 3. 缓存命中测试（连续请求两次）
time curl "http://localhost:8001/api/v1/search?q=电影"
time curl "http://localhost:8001/api/v1/search?q=电影"
```

**预期性能**：
- 首次请求：< 200ms
- 缓存命中：< 50ms
- 搜索结果一致

### 4.2 推荐性能

**测试场景**：
```bash
# 1. 个性化推荐
time curl "http://localhost:8001/api/v1/recommendations/personalized?limit=20"

# 2. 相似视频推荐
time curl "http://localhost:8001/api/v1/recommendations/similar/1?limit=10"

# 3. 缓存测试
time curl "http://localhost:8001/api/v1/recommendations/personalized?limit=20"
time curl "http://localhost:8001/api/v1/recommendations/personalized?limit=20"
```

**预期性能**：
- 首次推荐：< 300ms
- 缓存命中：< 100ms
- 相似视频：< 200ms

---

## 🎨 五、用户界面展示

### 5.1 搜索页面

**布局结构**：
```
┌─────────────────────────────────────┐
│  搜索结果: "关键词"                   │
├─────────────────────────────────────┤
│  [筛选面板]                          │
│  排序 | 分类 | 地区 | 年份 | 评分    │
│  [清除所有筛选]                      │
├─────────────────────────────────────┤
│  共找到 X 个结果                     │
├─────────────────────────────────────┤
│  [视频卡片网格 - 4列]                │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐              │
│  │  │ │  │ │  │ │  │              │
│  └──┘ └──┘ └──┘ └──┘              │
└─────────────────────────────────────┘
```

### 5.2 首页推荐

**布局结构**：
```
┌─────────────────────────────────────┐
│  热门推荐                            │
│  [视频卡片网格 - 4列 x 3行]          │
├─────────────────────────────────────┤
│  为你推荐 ⭐                         │
│  [视频卡片网格 - 4列 x 3行]          │
├─────────────────────────────────────┤
│  最新发布                            │
│  [视频卡片网格 - 4列 x 3行]          │
└─────────────────────────────────────┘
```

### 5.3 视频详情页

**布局结构**：
```
┌─────────────────────────────────────┐
│  [视频播放器]                        │
├─────────────────────────────────────┤
│  视频标题                            │
│  ⭐评分 ❤️收藏 📊评价               │
├─────────────────────────────────────┤
│  视频信息（演员、导演、分类等）       │
├─────────────────────────────────────┤
│  评论区                              │
├─────────────────────────────────────┤
│  相似推荐                            │
│  [视频卡片网格 - 6列]                │
└─────────────────────────────────────┘
```

---

## 🔧 六、故障排查

### 6.1 搜索问题

**问题1：搜索无结果**
```
症状：输入关键词后显示"没有找到匹配的结果"
原因：
  1. 数据库中没有匹配的视频
  2. 搜索关键词拼写错误
  3. 筛选条件过于严格
解决：
  1. 尝试更通用的关键词
  2. 清除部分筛选条件
  3. 检查数据库是否有视频数据
```

**问题2：筛选器不工作**
```
症状：选择筛选条件后结果不变
原因：
  1. 浏览器缓存问题
  2. API请求失败
解决：
  1. 刷新页面（Ctrl+F5）
  2. 打开浏览器开发者工具检查网络请求
  3. 检查后端API日志
```

### 6.2 推荐问题

**问题1："为你推荐"不显示**
```
症状：首页没有"为你推荐"板块
原因：
  1. 数据库中视频数量不足
  2. 推荐API返回空数组
解决：
  1. 检查数据库视频数量（至少需要10个视频）
  2. 查看API返回：GET /recommendations/for-you
  3. 检查Redis缓存状态
```

**问题2：推荐不准确**
```
症状：推荐的视频与兴趣不符
原因：
  1. 观看历史数据不足（需要至少3-5个观看记录）
  2. 用户行为数据单一
解决：
  1. 多观看不同类型的视频
  2. 进行评分和收藏操作
  3. 等待系统积累更多数据
```

---

## 📚 七、开发者参考

### 7.1 添加新的搜索筛选

**步骤**：
1. 后端添加参数：
```python
# backend/app/api/search.py
async def search_videos(
    # ... existing params
    new_filter: Optional[str] = None,  # 新增参数
):
    if new_filter:
        filters.append(Video.new_field == new_filter)
```

2. 前端添加筛选器：
```typescript
// frontend/src/pages/Search/index.tsx
const [filters, setFilters] = useState({
  // ... existing filters
  new_filter: '',
})
```

3. 更新UI：
```tsx
<select value={filters.new_filter} 
        onChange={(e) => handleFilterChange('new_filter', e.target.value)}>
  <option value="">全部</option>
  ...
</select>
```

### 7.2 调整推荐算法权重

**位置**：`backend/app/utils/recommendation_engine.py`

**修改协同过滤/内容推荐比例**：
```python
# 当前：60% 协同 + 40% 内容
collaborative_videos = await self._get_collaborative_filtering_recommendations(
    user_id, limit=int(limit * 0.6), exclude_ids=exclude_ids
)
content_videos = await self._get_content_based_recommendations(
    user_id, limit=int(limit * 0.4), exclude_ids=exclude_ids + collaborative_ids
)

# 修改为：50% 协同 + 50% 内容
collaborative_videos = await self._get_collaborative_filtering_recommendations(
    user_id, limit=int(limit * 0.5), exclude_ids=exclude_ids
)
content_videos = await self._get_content_based_recommendations(
    user_id, limit=int(limit * 0.5), exclude_ids=exclude_ids + collaborative_ids
)
```

**修改相似度权重**：
```python
def _calculate_similarity_score(self, video1: Video, video2: Video) -> float:
    score = 0.0
    
    # 调整各个维度的权重
    category_overlap * 0.4  # 原：40%
    actor_overlap * 0.3     # 原：30%
    director_overlap * 0.2  # 原：20%
    country_same * 0.05     # 原：5%
    rating_similar * 0.05   # 原：5%
    
    return score
```

---

## 📞 八、技术支持

### 相关文档
- [RECOMMENDATION_SYSTEM.md](./RECOMMENDATION_SYSTEM.md) - 推荐系统详细文档
- [SEARCH_ENHANCEMENT.md](./SEARCH_ENHANCEMENT.md) - 搜索增强详细文档
- [CLAUDE.md](./CLAUDE.md) - 项目开发指南

### API文档
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc

### 提交记录
- 搜索增强：`c9e2b91`
- 推荐后端：`7d4c047`
- 推荐前端：`4aabb0e`
