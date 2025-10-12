# 数据库内容多语言实施方案

**方案类型**: 数据库内容多语言（高级）  
**实施日期**: 2025-10-11  
**预计耗时**: 2-3 天  
**适用**: 真正的国际化内容平台

---

## 📊 方案选择

### 两种数据库多语言架构

#### 方案 A: 字段复制法（推荐，简单）⭐⭐⭐

**原理**: 为每个需要翻译的字段添加多语言列

```sql
-- 示例：categories表
CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name VARCHAR(100),           -- 主语言（中文）
  name_en VARCHAR(100),        -- 英文
  name_ja VARCHAR(100),        -- 日文（可选）
  description TEXT,            -- 主语言描述
  description_en TEXT,         -- 英文描述
  description_ja TEXT          -- 日文描述（可选）
);
```

**优势**:

- ✅ 查询简单快速
- ✅ 不需要 JOIN
- ✅ 易于理解和维护

**劣势**:

- ❌ 添加新语言需要 ALTER TABLE
- ❌ 字段较多

---

#### 方案 B: 翻译表法（灵活，复杂）⭐⭐

**原理**: 独立的翻译表存储多语言内容

```sql
-- 主表
CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  slug VARCHAR(100)
);

-- 翻译表
CREATE TABLE category_translations (
  id INTEGER PRIMARY KEY,
  category_id INTEGER REFERENCES categories(id),
  language VARCHAR(10),  -- zh-CN, en-US, ja-JP
  name VARCHAR(100),
  description TEXT,
  UNIQUE(category_id, language)
);
```

**优势**:

- ✅ 灵活添加新语言
- ✅ 字段数量固定

**劣势**:

- ❌ 需要 JOIN 查询
- ❌ 查询复杂
- ❌ 性能略低

---

## 🚀 推荐方案：字段复制法

基于你的项目现状，推荐使用**字段复制法**：

### 需要多语言的模型

1. **Category（分类）** - 高优先级
2. **Tag（标签）** - 高优先级
3. **Country（国家/地区）** - 中优先级
4. **Video（视频）** - 看情况
5. **Announcement（公告）** - 高优先级

---

## 📝 实施步骤

### Step 1: 数据库 Migration

创建 migration 添加多语言字段：

```bash
cd backend
make db-migrate MSG="add_multilingual_support"
```

编辑生成的 migration 文件：

```python
# alembic/versions/xxx_add_multilingual_support.py
"""add multilingual support

Revision ID: xxx
Revises: yyy
Create Date: 2025-10-11

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # 1. Category 多语言
    op.add_column('categories', sa.Column('name_en', sa.String(100), nullable=True, comment='英文名称'))
    op.add_column('categories', sa.Column('description_en', sa.Text, nullable=True, comment='英文描述'))

    # 2. Tag 多语言
    op.add_column('tags', sa.Column('name_en', sa.String(100), nullable=True, comment='英文名称'))

    # 3. Country 多语言
    op.add_column('countries', sa.Column('name_en', sa.String(100), nullable=True, comment='英文名称'))

    # 4. Announcement 多语言
    op.add_column('announcements', sa.Column('title_en', sa.String(200), nullable=True, comment='英文标题'))
    op.add_column('announcements', sa.Column('content_en', sa.Text, nullable=True, comment='英文内容'))

    # 5. 可选：Video 多语言（如果视频本身需要翻译）
    # op.add_column('videos', sa.Column('title_en', sa.String(500), nullable=True))
    # op.add_column('videos', sa.Column('description_en', sa.Text, nullable=True))

    # 6. 填充默认数据（将中文复制到英文，方便后续翻译）
    op.execute("""
        UPDATE categories SET name_en = name, description_en = description;
        UPDATE tags SET name_en = name;
        UPDATE countries SET name_en = name;
    """)


def downgrade() -> None:
    op.drop_column('categories', 'description_en')
    op.drop_column('categories', 'name_en')
    op.drop_column('tags', 'name_en')
    op.drop_column('countries', 'name_en')
    op.drop_column('announcements', 'content_en')
    op.drop_column('announcements', 'title_en')
```

运行 migration：

```bash
make db-upgrade
```

---

### Step 2: 更新 Models

```python
# app/models/video.py

class Category(Base):
    """Category model"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment='中文名称')
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='英文名称')
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='中文描述')
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='英文描述')
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent: Mapped[Optional[Category]] = relationship("Category", remote_side=[id], backref="children")
    video_categories: Mapped[list[VideoCategory]] = relationship("VideoCategory", back_populates="category")


class Tag(Base):
    """Tag model"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment='中文名称')
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='英文名称')
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video_tags: Mapped[list[VideoTag]] = relationship("VideoTag", back_populates="tag")


class Country(Base):
    """Country/Region model"""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment='中文名称')
    name_en: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment='英文名称')
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # ISO code
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    videos: Mapped[list[Video]] = relationship("Video", back_populates="country")
```

---

### Step 3: 创建语言工具类

```python
# app/utils/language.py
"""
语言处理工具
"""
from typing import Any, Dict, Optional
from fastapi import Request


class LanguageHelper:
    """语言助手"""

    SUPPORTED_LANGUAGES = ['zh-CN', 'en-US', 'ja-JP']
    DEFAULT_LANGUAGE = 'zh-CN'

    @staticmethod
    def get_language(request: Request) -> str:
        """
        从请求获取语言

        优先级:
        1. X-Language 自定义头
        2. Accept-Language 标准头
        3. 默认语言（zh-CN）
        """
        # 方法1: 自定义头（推荐，精确控制）
        custom_lang = request.headers.get("X-Language", "")
        if custom_lang in LanguageHelper.SUPPORTED_LANGUAGES:
            return custom_lang

        # 方法2: Accept-Language（浏览器自动发送）
        accept_lang = request.headers.get("Accept-Language", "")
        if accept_lang:
            # 解析: zh-CN,zh;q=0.9,en;q=0.8
            for lang_entry in accept_lang.split(','):
                lang_code = lang_entry.split(';')[0].strip()
                if lang_code in LanguageHelper.SUPPORTED_LANGUAGES:
                    return lang_code

                # 模糊匹配: zh -> zh-CN
                lang_prefix = lang_code.split('-')[0]
                for supported in LanguageHelper.SUPPORTED_LANGUAGES:
                    if supported.startswith(lang_prefix):
                        return supported

        # 默认语言
        return LanguageHelper.DEFAULT_LANGUAGE

    @staticmethod
    def get_localized_field(obj: Any, field: str, lang: str) -> str:
        """
        获取本地化字段值

        Args:
            obj: 数据库对象
            field: 字段名（如 'name'）
            lang: 语言代码

        Returns:
            翻译后的值，如果没有翻译则返回默认值

        Example:
            category = db.query(Category).first()
            name = get_localized_field(category, 'name', 'en-US')
            # 返回 category.name_en 或 category.name
        """
        # 如果是默认语言，直接返回
        if lang == LanguageHelper.DEFAULT_LANGUAGE:
            return getattr(obj, field, '')

        # 尝试获取翻译字段
        lang_suffix = lang.replace('-', '_').lower().split('_')[0]  # zh-CN -> zh, en-US -> en
        localized_field = f"{field}_{lang_suffix}"

        # 获取翻译值，如果没有则回退到默认语言
        value = getattr(obj, localized_field, None)
        return value if value else getattr(obj, field, '')

    @staticmethod
    def to_dict_with_locale(obj: Any, lang: str, fields: list[str]) -> Dict[str, Any]:
        """
        将对象转换为字典，包含本地化字段

        Args:
            obj: 数据库对象
            lang: 语言代码
            fields: 需要本地化的字段列表

        Returns:
            包含本地化值的字典
        """
        result = {}

        for field in fields:
            result[field] = LanguageHelper.get_localized_field(obj, field, lang)

        # 添加其他非翻译字段
        for attr in dir(obj):
            if not attr.startswith('_') and attr not in fields:
                value = getattr(obj, attr, None)
                if not callable(value):
                    result[attr] = value

        return result


# 依赖函数
async def get_language(request: Request) -> str:
    """获取请求语言（用作FastAPI依赖）"""
    return LanguageHelper.get_language(request)
```

---

### Step 4: 更新 Schemas

```python
# app/schemas/video.py

from typing import Optional
from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    """分类基础Schema"""
    name: str = Field(..., description="分类名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    slug: str
    description: Optional[str] = Field(None, description="分类描述")
    description_en: Optional[str] = Field(None, description="英文描述")
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """创建分类"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类"""
    name: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """分类响应（自动本地化）"""
    id: int
    name: str  # 根据语言自动返回对应字段
    slug: str
    description: Optional[str] = None
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


class CategoryResponseFull(BaseModel):
    """分类完整响应（包含所有语言）"""
    id: int
    name: str
    name_en: Optional[str] = None
    slug: str
    description: Optional[str] = None
    description_en: Optional[str] = None
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}
```

---

### Step 5: 更新 API 端点

#### 公开 API（自动本地化）

```python
# app/api/categories.py
from app.utils.language import LanguageHelper, get_language

@router.get("")
async def get_categories(
    request: Request,
    lang: str = Depends(get_language),  # 自动获取语言
    db: AsyncSession = Depends(get_db),
):
    """
    获取分类列表（自动本地化）

    - 根据 Accept-Language 或 X-Language 头返回对应语言
    - 如果翻译不存在，返回默认语言（中文）
    """
    # 缓存键包含语言
    cache_key = f"categories:all:{lang}"
    cached = await Cache.get(cache_key)
    if cached:
        return cached

    # 查询所有分类
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.sort_order)
    )
    categories = result.scalars().all()

    # 根据语言返回对应字段
    localized_categories = []
    for cat in categories:
        localized_categories.append({
            "id": cat.id,
            "name": LanguageHelper.get_localized_field(cat, 'name', lang),
            "slug": cat.slug,
            "description": LanguageHelper.get_localized_field(cat, 'description', lang),
            "sort_order": cat.sort_order,
            "is_active": cat.is_active,
        })

    # 缓存30分钟
    await Cache.set(cache_key, localized_categories, ttl=1800)

    return localized_categories
```

#### 管理端 API（支持多语言编辑）

```python
# app/admin/categories.py

@router.post("")
async def create_category(
    category_data: CategoryCreate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建分类（支持多语言）

    请求体:
    {
      "name": "动作片",
      "name_en": "Action",
      "description": "动作类电影",
      "description_en": "Action movies",
      "slug": "action"
    }
    """
    # 创建分类
    new_category = Category(
        name=category_data.name,
        name_en=category_data.name_en,
        slug=category_data.slug,
        description=category_data.description,
        description_en=category_data.description_en,
        sort_order=category_data.sort_order,
        is_active=category_data.is_active,
    )

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    # 清除所有语言的缓存
    await Cache.delete_pattern("categories:*")

    return CategoryResponseFull.model_validate(new_category)


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新分类（支持多语言编辑）

    可以单独更新某个语言的字段:
    {
      "name_en": "Updated English Name"
    }
    """
    # 查询分类
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # 更新字段
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    # 清除所有语言的缓存
    await Cache.delete_pattern("categories:*")

    return CategoryResponseFull.model_validate(category)
```

---

### Step 6: 前端适配

#### API 调用时发送语言头

```typescript
// frontend/src/services/api.ts
import axios from 'axios';
import i18n from '../i18n/config';

const apiClient = axios.create({
  baseURL: '/api/v1',
});

// 请求拦截器 - 添加语言头
apiClient.interceptors.request.use((config) => {
  // 添加当前语言到请求头
  config.headers['X-Language'] = i18n.language || 'zh-CN';

  // 或使用标准Accept-Language
  config.headers['Accept-Language'] = i18n.language || 'zh-CN';

  return config;
});

export default apiClient;
```

#### 使用本地化数据

```typescript
// frontend/src/pages/Categories/index.tsx
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

export function Categories() {
  const { i18n } = useTranslation();

  // 查询会自动发送语言头
  const { data: categories } = useQuery({
    queryKey: ['categories', i18n.language], // 语言变化时重新查询
    queryFn: () => apiClient.get('/categories'),
  });

  return (
    <div>
      {categories?.map((cat) => (
        <div key={cat.id}>
          <h3>{cat.name}</h3> {/* 自动是对应语言 */}
          <p>{cat.description}</p>
        </div>
      ))}
    </div>
  );
}
```

#### 语言切换时刷新数据

```typescript
// components/LanguageSwitcher.tsx
import { useQueryClient } from '@tanstack/react-query';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const queryClient = useQueryClient();

  const changeLanguage = async (lang: string) => {
    await i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);

    // 重新获取所有数据（清除缓存）
    queryClient.invalidateQueries();
  };

  return (
    <select value={i18n.language} onChange={(e) => changeLanguage(e.target.value)}>
      <option value="zh-CN">简体中文</option>
      <option value="en-US">English</option>
    </select>
  );
}
```

---

### Step 7: 管理后台翻译管理

创建翻译管理界面：

```typescript
// admin-frontend/src/pages/Categories/TranslationForm.tsx
import { Form, Input, Tabs } from 'antd';

export function CategoryTranslationForm() {
  return (
    <Form>
      <Tabs>
        {/* 中文标签 */}
        <Tabs.TabPane tab="中文 🇨🇳" key="zh">
          <Form.Item label="名称" name="name">
            <Input placeholder="中文分类名称" />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea placeholder="中文描述" />
          </Form.Item>
        </Tabs.TabPane>

        {/* 英文标签 */}
        <Tabs.TabPane tab="English 🇺🇸" key="en">
          <Form.Item label="Name" name="name_en">
            <Input placeholder="English category name" />
          </Form.Item>
          <Form.Item label="Description" name="description_en">
            <Input.TextArea placeholder="English description" />
          </Form.Item>
        </Tabs.TabPane>

        {/* 日文标签（可选） */}
        <Tabs.TabPane tab="日本語 🇯🇵" key="ja" disabled>
          <div>未来支持</div>
        </Tabs.TabPane>
      </Tabs>
    </Form>
  );
}
```

---

## 📊 完整流程示例

### 用户访问流程

```
1. 用户选择英文
   ↓
2. 前端发送请求
   GET /api/v1/categories
   Headers: {
     "X-Language": "en-US",
     "Accept-Language": "en-US,en;q=0.9"
   }
   ↓
3. 后端处理
   - 获取语言: en-US
   - 查询数据库
   - 返回 name_en 和 description_en
   ↓
4. 响应
   [
     {
       "id": 1,
       "name": "Action",        // 来自 name_en
       "description": "Action movies",  // 来自 description_en
       "slug": "action"
     }
   ]
   ↓
5. 前端显示英文内容
```

### 管理员编辑流程

```
1. 管理员创建/编辑分类
   ↓
2. 填写多语言表单
   中文: 动作片 / 动作类电影
   英文: Action / Action movies
   ↓
3. 提交到后端
   POST /api/v1/admin/categories
   {
     "name": "动作片",
     "name_en": "Action",
     "description": "动作类电影",
     "description_en": "Action movies"
   }
   ↓
4. 保存到数据库
   categories表:
   | id | name   | name_en | description  | description_en |
   |----|--------|---------|--------------|----------------|
   | 1  | 动作片 | Action  | 动作类电影   | Action movies  |
   ↓
5. 不同语言用户看到不同内容
   - 中文用户: "动作片"
   - 英文用户: "Action"
```

---

## 🎯 实施优先级

### Phase 1: 基础多语言（1 天）

**涉及模型**:

- ✅ Category（分类）
- ✅ Tag（标签）
- ✅ Country（国家）

**工作**:

1. 创建 migration 添加字段
2. 更新 models
3. 创建 LanguageHelper 工具类
4. 更新 schemas

### Phase 2: API 支持（1 天）

**工作**:

1. 更新公开 API（自动本地化）
2. 更新管理 API（支持编辑）
3. 添加缓存（区分语言）
4. 测试验证

### Phase 3: 前端适配（1 天）

**工作**:

1. 配置 axios 发送语言头
2. 更新 react-query 键（包含语言）
3. 创建翻译管理界面
4. 语言切换时刷新数据

---

## ⚠️ 注意事项

### 1. 缓存策略

```python
# 缓存键必须包含语言
cache_key = f"categories:all:{lang}"  # ✅ 正确
cache_key = f"categories:all"         # ❌ 错误，会导致语言混乱
```

### 2. 默认值处理

```python
# 如果英文翻译不存在，回退到中文
name = category.name_en or category.name  # ✅ 正确
name = category.name_en  # ❌ 错误，可能为None
```

### 3. 搜索功能

```python
# 搜索需要同时搜索多语言字段
filters.append(
    or_(
        Video.title.ilike(f"%{q}%"),
        Video.title_en.ilike(f"%{q}%"),  # 也搜索英文标题
    )
)
```

---

## 📝 迁移现有数据

### 翻译现有数据

```sql
-- 1. 先复制中文到英文（占位）
UPDATE categories SET name_en = name, description_en = description;
UPDATE tags SET name_en = name;
UPDATE countries SET name_en = name;

-- 2. 手动翻译或使用翻译API
UPDATE categories SET
  name_en = '动作片' WHERE name = 'Action';
  description_en = 'Action movies and thriller content'
WHERE id = 1;

-- 3. 或者导出CSV，翻译后导入
COPY (
  SELECT id, name, name_en, description, description_en
  FROM categories
) TO '/tmp/categories_translate.csv' CSV HEADER;
```

---

## 🔧 可选功能

### 1. 翻译进度追踪

```python
# app/admin/translation_status.py

@router.get("/translation-status")
async def get_translation_status(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取翻译进度"""
    # 统计各模型的翻译完成度
    categories_total = await db.execute(select(func.count(Category.id)))
    categories_translated_en = await db.execute(
        select(func.count(Category.id)).where(Category.name_en.isnot(None))
    )

    return {
        "categories": {
            "total": categories_total.scalar(),
            "translated_en": categories_translated_en.scalar(),
            "progress": categories_translated_en.scalar() / categories_total.scalar() * 100
        },
        # ... 其他模型
    }
```

### 2. 机器翻译集成

```python
# app/utils/auto_translate.py
import httpx

async def auto_translate(text: str, target_lang: str = 'en') -> str:
    """
    使用翻译API自动翻译

    可选方案:
    - Google Translate API
    - DeepL API
    - Azure Translator
    """
    # 示例：使用DeepL API
    api_key = settings.DEEPL_API_KEY

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api-free.deepl.com/v2/translate",
            data={
                "auth_key": api_key,
                "text": text,
                "target_lang": target_lang.upper(),
            }
        )

        if response.status_code == 200:
            return response.json()["translations"][0]["text"]

        return text  # 翻译失败，返回原文


# 在管理端使用
@router.post("/categories/{category_id}/auto-translate")
async def auto_translate_category(
    category_id: int,
    target_lang: str = "en",
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """自动翻译分类"""
    category = await db.get(Category, category_id)

    if target_lang == "en":
        category.name_en = await auto_translate(category.name, "en")
        category.description_en = await auto_translate(category.description or "", "en")

    await db.commit()
    return {"success": True, "message": "Auto-translation completed"}
```

---

## 📋 总结

### 这个方案适合吗？

**适合，如果你需要**:

- ✅ 视频平台真正国际化
- ✅ 内容本身需要多语言
- ✅ 运营多个语言市场

**不适合，如果**:

- ❌ 只是界面需要翻译（用纯前端方案）
- ❌ 用户主要是单一语言
- ❌ 内容翻译工作量大

### 实施建议

**建议分阶段**:

1. **阶段 1**: 纯前端国际化（2 天）

   - 先做界面翻译
   - 验证用户需求

2. **阶段 2**: 评估是否需要内容多语言

   - 看国际用户比例
   - 评估翻译成本

3. **阶段 3**: 实施数据库多语言（如需要）
   - 创建 migration
   - 更新 API
   - 翻译内容

---

**要我帮你立即实施数据库多语言吗？还是先从纯前端方案开始？**
