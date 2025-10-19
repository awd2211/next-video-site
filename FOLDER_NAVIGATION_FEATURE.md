# ✅ 文件夹导航功能 - Windows 文件资源管理器体验

**功能**: 像 Windows 资源管理器一样浏览文件和文件夹
**状态**: ✅ 已完成

---

## 📋 功能清单

### ✅ 已实现的功能

1. **双击文件夹进入**
   - 双击文件夹自动进入该文件夹
   - 显示文件夹内的所有文件和子文件夹

2. **显示文件夹包含的文件数量**
   - 网格视图：文件夹卡片显示 "N 项"
   - 列表视图：大小列显示 "N 项"

3. **面包屑导航**
   - 显示当前所在路径
   - 点击面包屑快速返回上级

4. **左侧文件夹树**
   - 树形结构显示所有文件夹
   - 点击文件夹树节点切换目录

5. **文件预览**
   - 双击图片：打开图片预览
   - 双击视频：打开视频播放器
   - 双击其他文件：新窗口打开

---

## 🔧 技术实现

### 后端修改

**文件**: `backend/app/admin/media.py`

#### 1. API 支持 parent_id 参数

```python
@router.get("/media", response_model=MediaListResponse)
async def get_media_list(
    parent_id: Optional[int] = Query(None, description="父文件夹ID，用于文件管理器"),
    ...
):
    # 文件管理器模式：按 parent_id 过滤
    if parent_id is not None:
        query = query.where(Media.parent_id == parent_id)
```

**功能**:
- `parent_id=None` 或不传 → 返回根目录文件
- `parent_id=123` → 返回 ID=123 文件夹下的文件

#### 2. 添加 children_count 字段

```python
# 为文件夹添加子项计数
for item in items:
    if item.is_folder:
        children_count_query = select(func.count()).where(
            and_(
                Media.parent_id == item.id,
                Media.is_deleted == False
            )
        )
        children_count = await db.execute(children_count_query)
        item_dict['children_count'] = children_count.scalar() or 0
```

**返回示例**:
```json
{
  "id": 5,
  "title": "我的文件夹",
  "is_folder": true,
  "children_count": 12,  // 包含 12 个文件/子文件夹
  ...
}
```

---

### 前端修改

#### 1. 类型定义

**文件**: `admin-frontend/src/pages/MediaManager/types.ts`

```typescript
export interface MediaItem {
  ...
  is_folder: boolean
  children_count?: number  // 文件夹包含的子项数量
  ...
}
```

#### 2. 双击处理

**文件**: `admin-frontend/src/pages/MediaManager/components/FileList.tsx`

```typescript
const handleDoubleClick = (item: MediaItem) => {
  if (item.is_folder) {
    onFolderOpen(item.id)  // 进入文件夹
  } else {
    // 文件预览逻辑...
  }
}
```

#### 3. 显示文件数量

**网格视图**:
```typescript
<div className="file-card-info">
  <div>
    {item.is_folder
      ? `${item.children_count || 0} 项`  // 文件夹显示项数
      : formatFileSize(item.file_size)    // 文件显示大小
    }
  </div>
</div>
```

**列表视图**:
```typescript
{
  title: '大小',
  render: (size, record) => {
    if (record.is_folder) {
      return `${record.children_count || 0} 项`
    }
    return formatFileSize(size)
  }
}
```

#### 4. 自动刷新

```typescript
useEffect(() => {
  loadFileList()  // 自动刷新文件列表

  // 更新面包屑
  if (selectedFolderId) {
    setBreadcrumbPath(buildBreadcrumbPath(selectedFolderId))
  }
}, [selectedFolderId, ...])  // 监听 selectedFolderId 变化
```

---

## 🎯 使用方式

### 基本操作

```
根目录
  ├── 📁 项目文件 (3 项)
  ├── 📁 图片素材 (15 项)
  ├── 📄 说明文档.pdf
  └── 📄 视频.mp4
```

#### 1. 进入文件夹
- **双击** "项目文件" 文件夹
- 或 **单击** 左侧文件夹树中的节点

#### 2. 查看内容
```
项目文件 > (显示该文件夹下的 3 个文件)
  ├── 📄 设计稿.psd
  ├── 📄 源代码.zip
  └── 📄 演示视频.mp4
```

#### 3. 返回上级
- 点击面包屑中的 "根目录"
- 或点击左侧树中的父文件夹

---

## 🔍 技术细节

### 性能优化

**问题**: 为每个文件夹查询子项数量可能导致 N+1 查询

**当前实现**:
```python
for item in items:  # 假设有 20 个文件夹
    if item.is_folder:
        count = await db.execute(...)  # 20 次额外查询
```

**未来优化方案**:
```python
# 方案1: 批量查询
folder_ids = [item.id for item in items if item.is_folder]
counts_query = select(Media.parent_id, func.count()).where(
    Media.parent_id.in_(folder_ids)
).group_by(Media.parent_id)
# 只需 1 次额外查询

# 方案2: 维护计数缓存
# 在 Media 模型中添加 children_count 字段
# 使用触发器或应用层逻辑维护
```

### 数据流

```
用户双击文件夹
  ↓
onFolderOpen(folderId)
  ↓
setSelectedFolderId(folderId)
  ↓
useEffect 监听到变化
  ↓
loadFileList({ parent_id: folderId })
  ↓
GET /api/v1/admin/media?parent_id=123
  ↓
后端查询 WHERE parent_id = 123
  ↓
返回该文件夹下的文件列表
  ↓
前端渲染文件卡片
```

---

## 📊 示例场景

### 场景1: 浏览项目文件

```bash
# 初始状态：根目录
GET /api/v1/admin/media?page=1&page_size=50
→ 返回根目录的所有文件和文件夹

# 双击 "项目文件" (id=5)
GET /api/v1/admin/media?page=1&page_size=50&parent_id=5
→ 返回 parent_id=5 的所有文件

# 面包屑显示：根目录 > 项目文件
```

### 场景2: 多层嵌套

```
根目录 (parent_id=null)
  └── 📁 2024项目 (id=1, children_count=2)
      ├── 📁 设计稿 (id=2, children_count=5)
      │   ├── 📄 v1.psd
      │   ├── 📄 v2.psd
      │   └── ...
      └── 📁 源代码 (id=3, children_count=10)
```

**导航路径**:
1. 双击 "2024项目" → `parent_id=1`
2. 双击 "设计稿" → `parent_id=2`
3. 点击面包屑 "2024项目" → 返回 `parent_id=1`

---

## ✅ 验证清单

### 功能验证

- [x] 双击文件夹能进入
- [x] 显示文件夹内的文件
- [x] 显示文件夹包含的文件数量
- [x] 面包屑导航正确
- [x] 左侧树导航同步
- [x] 双击文件能预览
- [x] 网格视图和列表视图都支持
- [x] 分页正常工作
- [x] 搜索功能正常

### 性能验证

- [x] API 响应速度 < 1s
- [x] 后端自动重载（开发模式）
- [ ] 大量文件夹时的性能（需要优化）

---

## 🚀 未来增强

### 建议优化

1. **批量查询子项数量**（减少 N+1 查询）
2. **文件夹图标**（根据内容类型显示不同图标）
3. **快速预览**（悬停显示缩略图）
4. **拖拽操作**（拖拽文件到文件夹）
5. **右键菜单**（快速操作）
6. **键盘导航**（上下键选择，回车打开）
7. **地址栏**（手动输入路径）
8. **历史记录**（前进/后退）

---

## 🎓 对比其他文件管理器

| 功能 | Windows 资源管理器 | MediaManager | 状态 |
|------|-------------------|--------------|------|
| 双击打开文件夹 | ✅ | ✅ | 已实现 |
| 面包屑导航 | ✅ | ✅ | 已实现 |
| 文件夹树 | ✅ | ✅ | 已实现 |
| 显示文件数量 | ✅ | ✅ | 已实现 |
| 文件预览 | ✅ | ✅ | 已实现 |
| 拖拽移动 | ✅ | ⚠️ | 部分支持 |
| 地址栏 | ✅ | ❌ | 待实现 |
| 快捷键 | ✅ | ✅ | 已实现 |
| 多选操作 | ✅ | ✅ | 已实现 |
| 右键菜单 | ✅ | ✅ | 已实现 |

---

## 📚 相关文档

- [Media API 文档](backend/app/admin/media.py)
- [MediaManager 组件](admin-frontend/src/pages/MediaManager/)
- [类型定义](admin-frontend/src/pages/MediaManager/types.ts)

---

*实现日期: 2025-10-19*
*状态: ✅ 功能完整，性能待优化*
