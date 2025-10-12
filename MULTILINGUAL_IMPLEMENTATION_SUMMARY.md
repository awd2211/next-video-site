# 数据库多语言支持实施总结

**实施日期**: 2025-10-11  
**实施方案**: 字段复制法（方案 A）  
**状态**: ✅ 已完成

## 📋 已完成的工作

### ✅ 1. 数据库 Migration

**文件位置**: `backend/alembic/versions/`

- 已创建并应用 migration，添加多语言字段：

  - `categories`: `name_en`, `description_en`
  - `tags`: `name_en`
  - `countries`: `name_en`
  - `announcements`: `title_en`, `content_en`

- 自动填充默认数据（将中文复制到英文字段，方便后续翻译）

**验证**:

```bash
cd backend
alembic current  # 查看当前版本
```

---

### ✅ 2. 数据库 Models 更新

**更新的文件**:

- `backend/app/models/video.py`

  - `Country`: 添加 `name_en`
  - `Category`: 添加 `name_en`, `description_en`
  - `Tag`: 添加 `name_en`

- `backend/app/models/content.py`
  - `Announcement`: 添加 `title_en`, `content_en`

**特点**: 所有字段都标记了中文注释（`comment='中文名称'`）

---

### ✅ 3. 语言工具类

**文件**: `backend/app/utils/language.py`

**功能**:

- `LanguageHelper` 类：

  - `get_language()`: 从请求头获取语言（支持 X-Language 和 Accept-Language）
  - `get_localized_field()`: 获取本地化字段值，自动回退到默认语言
  - `to_dict_with_locale()`: 将对象转换为包含本地化字段的字典

- `get_language()` 依赖函数：用于 FastAPI 路由依赖注入

**支持的语言**:

- `zh-CN` (默认)
- `en-US`
- `ja-JP` (预留)

---

### ✅ 4. Schemas 更新

**文件**: `backend/app/schemas/admin_content.py`

**更新的 Schemas**:

- `CategoryCreate/Update/Response`: 支持 `name_en`, `description_en`
- `TagCreate/Update/Response`: 支持 `name_en`
- `CountryCreate/Update/Response`: 支持 `name_en`
- `AnnouncementCreate/Update/Response`: 支持 `title_en`, `content_en` (新增)

**特点**: 所有英文字段都是可选的（`Optional[str]`）

---

### ✅ 5. 公开 API 自动本地化

**文件**: `backend/app/api/categories.py`

**更新的端点**:

- `GET /api/v1/categories` - 分类列表
- `GET /api/v1/countries` - 国家列表
- `GET /api/v1/tags` - 标签列表

**功能**:

1. 自动从请求头读取语言（`X-Language` 或 `Accept-Language`）
2. 根据语言返回对应字段（如 `name_en` 或 `name`）
3. 缓存键包含语言参数（如 `categories:all:active:en-US`）
4. 如果翻译不存在，自动回退到中文

**示例**:

```bash
# 获取英文分类
curl -H "X-Language: en-US" http://localhost:8000/api/v1/categories

# 获取中文分类（默认）
curl http://localhost:8000/api/v1/categories
```

---

### ✅ 6. 管理 API 多语言编辑

**相关文件**:

- `backend/app/admin/categories.py`
- `backend/app/admin/tags.py` (已存在)
- `backend/app/admin/countries.py` (已存在)
- `backend/app/admin/announcements.py` (已更新)

**功能**:

- 所有管理 API 现在支持接收和返回多语言字段
- 创建/更新时可以同时提供所有语言的内容
- 响应返回所有语言字段供管理员编辑

**示例** (创建分类):

```json
POST /api/v1/admin/categories
{
  "name": "动作片",
  "name_en": "Action",
  "description": "动作类电影",
  "description_en": "Action movies",
  "slug": "action"
}
```

---

### ✅ 7. 前端 API 客户端

**用户前端**: `frontend/src/services/api.ts`
**管理前端**: `admin-frontend/src/utils/axios.ts`

**更新内容**:

- 请求拦截器自动添加语言头：
  ```typescript
  const language = localStorage.getItem('language') || navigator.language || 'zh-CN';
  config.headers['X-Language'] = language;
  config.headers['Accept-Language'] = language;
  ```

**使用方式**:

```typescript
// 设置语言
localStorage.setItem('language', 'en-US');

// 所有 API 请求会自动包含语言头
const categories = await api.get('/categories'); // 自动返回英文数据
```

---

## 🎯 架构特点

### 优势

- ✅ **查询性能优秀**: 无需 JOIN，直接查询对应字段
- ✅ **实现简单**: 易于理解和维护
- ✅ **自动回退**: 翻译不存在时自动显示默认语言
- ✅ **缓存友好**: 不同语言使用不同缓存键

### 注意事项

- ⚠️ **添加新语言需要 migration**: 需要 ALTER TABLE 添加新字段
- ⚠️ **字段较多**: 每个需要翻译的字段都要添加对应的语言字段

---

## 📊 数据库变更

### 新增字段汇总

| 表名          | 新增字段       | 类型         | 说明     |
| ------------- | -------------- | ------------ | -------- |
| categories    | name_en        | VARCHAR(100) | 英文名称 |
| categories    | description_en | TEXT         | 英文描述 |
| tags          | name_en        | VARCHAR(100) | 英文名称 |
| countries     | name_en        | VARCHAR(100) | 英文名称 |
| announcements | title_en       | VARCHAR(200) | 英文标题 |
| announcements | content_en     | TEXT         | 英文内容 |

---

## 🚀 使用指南

### 后端使用

#### 1. 在路由中使用语言依赖

```python
from app.utils.language import get_language, LanguageHelper

@router.get("/items")
async def get_items(lang: str = Depends(get_language)):
    # lang 会自动从请求头获取
    items = await db.execute(select(Item))

    # 返回本地化数据
    return [
        {
            "id": item.id,
            "name": LanguageHelper.get_localized_field(item, 'name', lang)
        }
        for item in items
    ]
```

#### 2. 缓存键必须包含语言

```python
# ✅ 正确
cache_key = f"items:all:{lang}"

# ❌ 错误 - 会导致语言混乱
cache_key = "items:all"
```

#### 3. 管理端创建/更新数据

```python
@router.post("/admin/items")
async def create_item(data: ItemCreate):
    # data 包含所有语言字段
    item = Item(
        name=data.name,
        name_en=data.name_en,
        # ...
    )
```

---

### 前端使用

#### 1. 设置语言

```typescript
// 用户选择语言时
localStorage.setItem('language', 'en-US');

// 重新加载数据（清除缓存）
queryClient.invalidateQueries();
```

#### 2. 语言切换组件示例

```typescript
function LanguageSwitcher() {
  const [language, setLanguage] = useState(localStorage.getItem('language') || 'zh-CN');

  const changeLanguage = (lang: string) => {
    localStorage.setItem('language', lang);
    setLanguage(lang);
    window.location.reload(); // 或使用 queryClient.invalidateQueries()
  };

  return (
    <select value={language} onChange={(e) => changeLanguage(e.target.value)}>
      <option value="zh-CN">简体中文</option>
      <option value="en-US">English</option>
    </select>
  );
}
```

#### 3. 管理后台翻译表单

```typescript
// 使用 Ant Design Tabs 组织多语言输入
<Tabs>
  <TabPane tab="中文 🇨🇳" key="zh">
    <Form.Item name="name" label="名称">
      <Input />
    </Form.Item>
    <Form.Item name="description" label="描述">
      <TextArea />
    </Form.Item>
  </TabPane>

  <TabPane tab="English 🇺🇸" key="en">
    <Form.Item name="name_en" label="Name">
      <Input />
    </Form.Item>
    <Form.Item name="description_en" label="Description">
      <TextArea />
    </Form.Item>
  </TabPane>
</Tabs>
```

---

## 🔧 后续工作（可选）

### 1. 翻译现有数据

目前所有英文字段都填充了中文内容（作为占位），需要真正的翻译：

```sql
-- 查看需要翻译的数据
SELECT id, name, name_en FROM categories;

-- 手动翻译或使用翻译服务
UPDATE categories
SET name_en = 'Action', description_en = 'Action movies'
WHERE id = 1;
```

### 2. 添加翻译进度追踪（可选）

在管理后台添加翻译完成度统计：

```python
@router.get("/admin/translation-status")
async def get_translation_status(db: AsyncSession):
    total = await db.scalar(select(func.count(Category.id)))
    translated = await db.scalar(
        select(func.count(Category.id))
        .where(Category.name_en.isnot(None))
        .where(Category.name_en != Category.name)  # 排除复制的
    )

    return {
        "categories": {
            "total": total,
            "translated": translated,
            "progress": (translated / total * 100) if total > 0 else 0
        }
    }
```

### 3. 集成机器翻译 API（可选）

可以集成 DeepL、Google Translate 等服务实现自动翻译：

```python
# app/utils/auto_translate.py
async def auto_translate(text: str, target_lang: str) -> str:
    # 调用翻译 API
    pass

@router.post("/admin/categories/{id}/auto-translate")
async def auto_translate_category(id: int, target_lang: str = "en"):
    category = await db.get(Category, id)
    category.name_en = await auto_translate(category.name, "en")
    category.description_en = await auto_translate(category.description, "en")
    await db.commit()
    return category
```

### 4. 添加更多语言

如需添加日语支持：

```bash
# 1. 创建 migration
cd backend
alembic revision -m "add_japanese_support"

# 2. 在 migration 中添加字段
op.add_column('categories', sa.Column('name_ja', sa.String(100)))
op.add_column('categories', sa.Column('description_ja', sa.Text))
# ...

# 3. 应用 migration
alembic upgrade head

# 4. 更新 Models 和 Schemas
# 5. 更新 LanguageHelper.SUPPORTED_LANGUAGES
```

---

## ✅ 验证清单

- [x] 数据库 migration 已应用
- [x] Models 已更新多语言字段
- [x] Schemas 支持多语言输入输出
- [x] 公开 API 自动本地化
- [x] 管理 API 支持多语言编辑
- [x] 前端 API 客户端添加语言头
- [x] 后端应用可以正常启动
- [x] 无 linter 错误

---

## 🎉 总结

数据库多语言支持已成功实施！现在系统支持：

1. **自动语言检测**: 根据请求头返回对应语言内容
2. **多语言管理**: 管理员可以编辑所有语言的内容
3. **优雅降级**: 翻译不存在时自动显示默认语言
4. **缓存优化**: 不同语言使用独立缓存

下一步可以：

- 翻译现有的中文数据为英文
- 在前端添加语言切换组件
- 根据需要添加更多语言支持

**🚀 系统已准备好提供多语言服务！**
