# 搜索增强功能文档

## 概述

本次更新为VideoSite平台添加了强大的搜索筛选和排序功能，大幅提升了用户查找视频的效率和体验。

## 功能特性

### 1. 高级筛选选项

#### 排序方式
- **最新发布** (created_at) - 按视频发布时间倒序
- **最多观看** (view_count) - 按观看次数倒序
- **最高评分** (average_rating) - 按平均评分倒序

#### 分类筛选
- 支持按视频分类筛选（动作、喜剧、剧情等）
- 显示所有活跃分类
- "全部分类"选项可清除筛选

#### 地区筛选
- 支持按国家/地区筛选
- 显示所有可用国家
- "全部地区"选项可清除筛选

#### 年份筛选
- 支持按发行年份筛选
- 提供最近50年的年份选项
- "全部年份"选项可清除筛选

#### 评分筛选
- 支持按最低评分筛选
- 选项：9分以上、8分以上、7分以上、6分以上、5分以上
- "不限"选项可清除筛选

### 2. URL参数同步

所有筛选条件都会自动同步到URL参数中，支持：
- 分享带筛选条件的搜索结果链接
- 浏览器前进/后退保持筛选状态
- 刷新页面保持筛选条件

示例URL：
```
/search?q=电影&category_id=1&country_id=3&year=2024&min_rating=8&sort_by=view_count
```

### 3. 用户界面

- **响应式设计**：适配桌面、平板、移动端
- **中文界面**：所有文本使用中文
- **清除筛选**：一键清除所有筛选条件
- **实时更新**：选择筛选条件后立即显示结果

## 技术实现

### 后端改进

#### API端点增强 (backend/app/api/search.py)

```python
@router.get("", response_model=PaginatedResponse)
async def search_videos(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,        # 新增：分类筛选
    country_id: Optional[int] = None,         # 新增：国家筛选
    year: Optional[int] = None,               # 新增：年份筛选
    min_rating: Optional[float] = Query(None, ge=0, le=10),  # 新增：评分筛选
    sort_by: str = Query("created_at", regex="^(created_at|view_count|average_rating)$"),  # 新增：排序
    db: AsyncSession = Depends(get_db),
):
```

**关键改进：**
- 添加5个新的查询参数支持高级筛选
- 使用SQLAlchemy的`and_`和`or_`构建复杂查询
- 支持分类的many-to-many关系查询
- 缓存键包含所有筛选参数
- 5分钟缓存TTL平衡性能和实时性

### 前端改进

#### 1. 数据服务 (frontend/src/services/dataService.ts)

新建服务获取筛选器数据：
```typescript
export const dataService = {
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/categories')
    return response.data
  },

  getCountries: async (): Promise<Country[]> => {
    const response = await api.get('/countries')
    return response.data
  },
}
```

#### 2. 视频服务增强 (frontend/src/services/videoService.ts)

更新搜索方法支持筛选参数：
```typescript
searchVideos: async (
  query: string,
  params?: {
    page?: number
    page_size?: number
    category_id?: number
    country_id?: number
    year?: number
    min_rating?: number
    sort_by?: string
  }
): Promise<PaginatedResponse<Video>>
```

#### 3. 搜索页面重构 (frontend/src/pages/Search/index.tsx)

**主要特性：**
- 使用`useState`管理筛选状态
- 使用`useSearchParams`同步URL参数
- 使用TanStack Query获取分类、国家和搜索结果
- 响应式网格布局（5列筛选器）
- 条件渲染"清除筛选"按钮

## 使用指南

### 用户使用

1. **基本搜索**
   - 在搜索框输入关键词
   - 点击搜索或按Enter

2. **应用筛选**
   - 选择排序方式（默认：最新发布）
   - 选择分类（可选）
   - 选择地区（可选）
   - 选择年份（可选）
   - 选择最低评分（可选）

3. **清除筛选**
   - 点击"清除所有筛选"按钮
   - 或手动将所有下拉框改回默认值

4. **分享结果**
   - 复制浏览器地址栏的URL
   - 其他用户打开链接将看到相同的筛选结果

### 开发者使用

#### 添加新的筛选条件

1. **后端**：在`search.py`添加新参数
```python
new_filter: Optional[str] = None,
```

2. **前端**：在`Search/index.tsx`添加状态和UI
```typescript
const [filters, setFilters] = useState({
  // ... existing filters
  new_filter: searchParams.get('new_filter') || '',
})
```

3. **更新服务**：在`videoService.ts`添加参数类型
```typescript
params?: {
  // ... existing params
  new_filter?: string
}
```

## 测试

### API测试

```bash
# 基本搜索
curl "http://localhost:8001/api/v1/search?q=电影"

# 带筛选的搜索
curl "http://localhost:8001/api/v1/search?q=电影&category_id=1&sort_by=view_count"

# 复杂筛选
curl "http://localhost:8001/api/v1/search?q=动作&category_id=1&country_id=2&year=2024&min_rating=8&sort_by=average_rating"
```

### 前端测试

1. 访问搜索页面：http://localhost:3000/search?q=test
2. 测试各个筛选器是否正常工作
3. 验证URL参数是否正确更新
4. 测试清除筛选功能
5. 测试响应式布局（调整浏览器窗口）

## 性能优化

1. **缓存策略**
   - 分类数据：30分钟缓存
   - 国家数据：1小时缓存
   - 搜索结果：5分钟缓存

2. **查询优化**
   - 使用`selectinload`预加载关联数据
   - 分页限制最大100条
   - 索引优化（确保title、release_year、country_id有索引）

3. **前端优化**
   - TanStack Query自动缓存和重用数据
   - 防抖搜索（避免过度请求）
   - 懒加载分类和国家数据

## 已知限制

1. 目前不支持多分类同时筛选
2. 年份筛选只支持单个年份，不支持范围
3. 评分筛选是最低分，不支持范围筛选
4. 移动端筛选器可能需要滚动查看

## 未来改进建议

1. **高级筛选面板**
   - 添加展开/收起功能
   - 移动端优化为底部抽屉

2. **筛选增强**
   - 支持年份范围（2020-2024）
   - 支持评分范围（7.0-9.5）
   - 支持多分类选择

3. **用户体验**
   - 添加搜索历史
   - 保存常用筛选条件
   - 推荐热门筛选组合

4. **性能优化**
   - Elasticsearch全文搜索
   - 搜索结果高亮
   - 智能搜索建议

## 提交信息

```
Commit: c9e2b91
feat: 添加搜索增强功能 - 高级筛选和排序

修改文件：
- backend/app/api/search.py (增强API)
- frontend/src/services/videoService.ts (更新服务)
- frontend/src/services/dataService.ts (新建)
- frontend/src/pages/Search/index.tsx (重构页面)
```

## 相关链接

- [API文档](http://localhost:8001/api/docs)
- [PLATFORM_STATUS.md](./PLATFORM_STATUS.md) - 平台状态
- [CLAUDE.md](./CLAUDE.md) - 项目指南
