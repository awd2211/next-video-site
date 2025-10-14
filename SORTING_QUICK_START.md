# 表格排序功能 - 快速上手指南

## 🚀 5分钟快速集成

### 后端（FastAPI）

```python
# 1. 导入
from app.utils.sorting import apply_sorting, normalize_sort_field
from typing import Optional
from fastapi import Query

# 2. 添加参数到路由
@router.get("")
async def list_items(
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    # ... 其他参数
):
    # 3. 定义白名单（必须！）
    allowed_sort_fields = ["id", "name", "created_at", "updated_at"]

    # 4. 应用排序
    sort_field = normalize_sort_field(sort_by)
    query = apply_sorting(
        query=query,
        model=YourModel,
        sort_by=sort_field,
        sort_order=sort_order,
        default_sort="created_at",
        allowed_fields=allowed_sort_fields
    )

    # 5. 执行查询
    result = await db.execute(query)
    return {"items": result.scalars().all()}
```

### 前端（React + TypeScript）

```typescript
// 1. 导入
import { useTableSort } from '@/hooks/useTableSort'

// 2. 在组件中使用
const YourComponent = () => {
  // 初始化 hook
  const { handleTableChange, getSortParams } = useTableSort({
    defaultSortBy: 'created_at',
    defaultSortOrder: 'desc'
  })

  // 3. 集成到 React Query
  const { data, isLoading } = useQuery({
    queryKey: ['items', page, ...Object.values(getSortParams())],
    queryFn: async () => {
      const response = await axios.get('/api/endpoint', {
        params: {
          page,
          page_size: 20,
          ...getSortParams(),  // 关键！
        },
      })
      return response.data
    },
  })

  // 4. 定义列（添加 sorter: true）
  const columns = [
    { title: 'ID', dataIndex: 'id', sorter: true },
    { title: 'Name', dataIndex: 'name', sorter: true },
    { title: 'Created', dataIndex: 'created_at', sorter: true },
  ]

  // 5. 渲染表格
  return (
    <Table
      columns={columns}
      dataSource={data?.items}
      onChange={(pagination, filters, sorter) => handleTableChange(sorter)}
      // ... 其他 props
    />
  )
}
```

## ✅ 检查清单

### 后端
- [ ] 导入 `apply_sorting` 和 `normalize_sort_field`
- [ ] 添加 `sort_by` 和 `sort_order` 参数到路由
- [ ] 定义 `allowed_sort_fields` 白名单
- [ ] 调用 `apply_sorting()` 应用排序
- [ ] 使用正则验证 `sort_order` 参数

### 前端
- [ ] 导入 `useTableSort` hook
- [ ] 初始化 hook 并设置默认值
- [ ] 在 `queryKey` 中添加 `...Object.values(getSortParams())`
- [ ] 在 API 请求 params 中添加 `...getSortParams()`
- [ ] 在需要排序的列上添加 `sorter: true`
- [ ] 在 Table 上添加 `onChange` 处理函数

## 💡 常见问题

### Q: 字段名不匹配怎么办？
A: 如果前端使用 camelCase（如 `viewCount`），后端使用 snake_case（如 `view_count`），`normalize_sort_field()` 会自动转换。如果没有自动转换，在 `backend/app/utils/sorting.py` 的 `SORT_FIELD_MAPPING` 中添加映射。

### Q: 如何禁用某列的排序？
A: 只需不添加 `sorter: true` 属性即可。

### Q: 如何更改默认排序？
A: 修改 `useTableSort()` 的参数：
```typescript
useTableSort({
  defaultSortBy: 'updated_at',  // 默认字段
  defaultSortOrder: 'asc'        // 默认方向
})
```

### Q: 排序和筛选/搜索能同时使用吗？
A: 可以！只需确保所有参数都在 `queryKey` 中即可：
```typescript
queryKey: ['items', page, search, filter, ...Object.values(getSortParams())]
```

## 🎯 快速测试

```bash
# 测试升序
curl "http://localhost:8000/api/v1/admin/videos?sort_by=title&sort_order=asc"

# 测试降序
curl "http://localhost:8000/api/v1/admin/videos?sort_by=id&sort_order=desc"
```

前端测试：打开页面，点击列头，观察数据是否按预期排序。

## 📚 完整文档

详见：[SORTING_COMPLETE_SUMMARY.md](SORTING_COMPLETE_SUMMARY.md)
