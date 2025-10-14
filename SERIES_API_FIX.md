# 系列管理 API 路径修复

## 问题描述

用户报告：管理员后台的"视频专辑/系列管理"页面看不到任何数据

## 问题诊断

1. **数据库检查**：✅ 数据库中有 25 个系列数据
2. **后端 API**：✅ `/api/v1/admin/series` 端点存在且正常工作
3. **前端路由**：✅ Series 路由已在 App.tsx 中配置
4. **问题所在**：❌ 前端 seriesService 使用了错误的 API 路径

## 根本原因

前端 `seriesService.ts` 中的 API 请求路径缺少 `/api/v1` 前缀：

**错误的路径**：
```typescript
api.get('/admin/series')           // ❌ 404 Not Found
```

**正确的路径**：
```typescript
api.get('/api/v1/admin/series')    // ✅ 正确
```

## 修复内容

修改了 `/home/eric/video/admin-frontend/src/services/seriesService.ts` 文件中所有 API 路径：

### 修复的端点（共 11 个）

1. `getList` - 获取专辑列表
2. `getDetail` - 获取专辑详情
3. `create` - 创建专辑
4. `update` - 更新专辑
5. `delete` - 删除专辑
6. `addVideos` - 添加视频到专辑
7. `removeVideos` - 从专辑移除视频
8. `updateVideoOrder` - 更新视频顺序
9. `getStats` - 获取统计数据
10. `batchPublish` - 批量发布
11. `batchArchive` - 批量归档
12. `batchDelete` - 批量删除
13. `batchFeature` - 批量设置推荐

### 修改示例

```typescript
// 修改前
const response = await api.get<PaginatedSeriesResponse>('/admin/series', { params })

// 修改后
const response = await api.get<PaginatedSeriesResponse>('/api/v1/admin/series', { params })
```

## 验证数据

数据库中现有系列数据：
- 总数：25 个系列
- 示例数据：
  - ID=3: 漫威电影宇宙系列 (3集)
  - ID=4: 哈利·波特系列 (5集)
  - ID=5: 指环王三部曲 (8集)
  - ID=6: 星球大战系列 (6集)
  - ID=7: DC超级英雄系列 (7集)

## 测试建议

修复后，请执行以下测试：

1. **重启前端开发服务器**
   ```bash
   cd admin-frontend
   pnpm run dev
   ```

2. **访问系列管理页面**
   - URL: `http://localhost:3002/series`
   - 应该能看到 25 个系列数据
   - 可以按状态和类型筛选
   - 可以搜索标题

3. **测试功能**
   - ✅ 查看系列列表
   - ✅ 查看系列详情
   - ✅ 创建新系列
   - ✅ 编辑系列信息
   - ✅ 删除系列
   - ✅ 批量操作

## 相关文件

- `/home/eric/video/admin-frontend/src/services/seriesService.ts` - 已修复
- `/home/eric/video/admin-frontend/src/pages/Series/List.tsx` - 列表页面
- `/home/eric/video/admin-frontend/src/pages/Series/Edit.tsx` - 编辑页面
- `/home/eric/video/backend/app/admin/series.py` - 后端 API

## 状态

✅ **已修复** - 所有 API 路径已更新为正确的格式
