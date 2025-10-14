# 表格分页大小选择器 - 快速参考

## 🎯 功能概述

用户可在所有表格页面的分页器中选择每页显示行数：10、20、50 或 100 行。

---

## ✅ 实现清单

### 主要列表页面
| 页面 | 表格数 | 状态 | 默认值 |
|------|--------|------|--------|
| Videos | 1 | ✅ | 20 |
| Users | 1 | ✅ | 20 |
| Banners | 1 | ✅ | 20 |
| Announcements | 1 | ✅ | 20 |
| Series | 1 | ✅ | 20 |
| Actors | 1 | ✅ | 20 |
| Directors | 1 | ✅ | 20 |
| Comments | 1 | ✅ | 20 |
| Roles | 2 | ✅ | 20 |
| Scheduling | 1 | ✅ | 20 |

### 额外管理页面
| 页面 | 表格数 | 状态 | 默认值 |
|------|--------|------|--------|
| Logs（操作日志） | 1 | ✅ | 20 |
| Logs（登录日志） | 1 | ✅ | 20 |
| Logs（系统日志） | 1 | ✅ | 20 |
| Logs（错误日志） | 1 | ✅ | 20 |
| IPBlacklist | 1 | ✅ | 20 |
| AIManagement | 1 | ✅ | 20 |
| Email（配置） | 1 | ✅ | 20 |
| Email（模板） | 1 | ✅ | 20 |
| Reports（热门视频） | 1 | ✅ | 20 |

**总计**: 15个页面，20个表格 ✨

---

## 🔧 实现步骤（3步）

### 1. 添加状态
```typescript
const [pageSize, setPageSize] = useState(20)
```

### 2. 更新 React Query
```typescript
queryKey: ['data', page, pageSize, ...filters],
params: { page, page_size: pageSize }
```

### 3. 配置分页器
```typescript
pagination={{
  pageSize: pageSize,
  onShowSizeChange: (current, size) => {
    setPageSize(size)
    setPage(1)
  },
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100'],
}}
```

---

## 📊 用户界面

分页器显示示例：
```
[<] 1 / 5  [每页显示 20 条 ▼]  [>]
```

点击下拉框显示选项：
```
[✓] 10 条/页
[✓] 20 条/页  ← 当前选中
[✓] 50 条/页
[✓] 100 条/页
```

---

## 🎯 关键点

1. **状态管理**：使用 `useState` 管理 `pageSize`
2. **查询集成**：将 `pageSize` 添加到 `queryKey` 和 API 参数
3. **页码重置**：更改 pageSize 时重置到第一页
4. **选项固定**：所有页面使用相同的选项 `['10', '20', '50', '100']`
5. **默认值**：统一使用 20 作为默认值

---

## 💡 使用建议

| 场景 | 推荐值 | 原因 |
|------|--------|------|
| 慢速网络 | 10 | 减少加载时间 |
| 标准浏览 | 20 | 平衡速度与便捷 |
| 批量操作 | 50 | 减少翻页次数 |
| 数据导出 | 100 | 快速浏览大量数据 |

---

## 🐛 常见问题

**Q: 更改 pageSize 后数据不刷新？**
A: 确保 `pageSize` 在 `queryKey` 中

**Q: 页码超出范围？**
A: 确保 `onShowSizeChange` 中重置 `setPage(1)`

**Q: 类型错误？**
A: 确保使用 `const [pageSize, setPageSize] = useState(20)`，不是 `const [pageSize] = useState(20)`

---

## 📚 相关文档

- [PAGE_SIZE_SELECTOR_SUMMARY.md](PAGE_SIZE_SELECTOR_SUMMARY.md) - 主要列表页面详细实现
- [PAGE_SIZE_ADDITIONAL_PAGES_SUMMARY.md](PAGE_SIZE_ADDITIONAL_PAGES_SUMMARY.md) - 额外管理页面实现总结

---

**文档版本**: 2.0
**最后更新**: 2025-10-14
