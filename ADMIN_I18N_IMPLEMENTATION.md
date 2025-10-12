# 管理后台国际化实施方案

**目标**: 为管理后台添加中英文切换功能  
**技术栈**: React + Ant Design 5 + i18next

---

## 📋 实施步骤

### Step 1: 安装依赖

```bash
cd admin-frontend
pnpm add i18next react-i18next
```

### Step 2: 创建 i18n 配置

创建文件结构：

```
src/
  i18n/
    index.ts          # i18n 配置
    locales/
      zh-CN.ts        # 中文语言包
      en-US.ts        # 英文语言包
```

### Step 3: 配置 Ant Design 语言

修改 `main.tsx` 以支持 Ant Design 的语言切换

### Step 4: 创建语言切换组件

在布局中添加语言切换器

---

## 📁 文件清单

### 1. i18n 配置文件

**src/i18n/index.ts**

- 初始化 i18next
- 配置语言检测
- 配置资源文件

### 2. 中文语言包

**src/i18n/locales/zh-CN.ts**

- 所有中文翻译
- 按模块组织

### 3. 英文语言包

**src/i18n/locales/en-US.ts**

- 所有英文翻译
- 与中文一一对应

### 4. 语言切换组件

**src/components/LanguageSwitcher.tsx**

- 下拉菜单选择语言
- 保存到 localStorage
- 刷新 Ant Design 语言

---

## 🌐 使用方法

### 在组件中使用

```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('dashboard.title')}</h1>
      <p>{t('dashboard.welcome')}</p>
    </div>
  );
}
```

### 切换语言

```tsx
import { useTranslation } from 'react-i18next';

function LanguageButton() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('admin_language', lng);
  };

  return (
    <Select value={i18n.language} onChange={changeLanguage}>
      <Select.Option value="zh-CN">简体中文</Select.Option>
      <Select.Option value="en-US">English</Select.Option>
    </Select>
  );
}
```

---

## 📊 翻译范围

### 需要翻译的内容

1. **导航菜单**

   - 仪表盘、视频管理、用户管理等

2. **页面标题**

   - 各个页面的标题和说明

3. **表单标签**

   - 输入框、选择器的标签

4. **按钮文字**

   - 提交、取消、删除等

5. **提示消息**

   - 成功、错误、警告消息

6. **表格列名**
   - ID、标题、状态等

### 不需要翻译的内容

- 数据库中的内容（由后端 API 处理）
- 用户输入的数据
- 日志内容

---

## ✅ 完成后效果

- ✅ 顶部导航栏有语言切换器
- ✅ 所有菜单、按钮、表单都会切换语言
- ✅ Ant Design 组件（日期选择器、分页等）也会切换语言
- ✅ 语言选择会保存到 localStorage
- ✅ 刷新页面后语言保持不变

---

## 🚀 开始实施

准备好了吗？我将：

1. ✅ 创建 i18n 配置文件
2. ✅ 创建中英文语言包（包含所有常用文本）
3. ✅ 修改 main.tsx 配置 Ant Design
4. ✅ 创建语言切换组件
5. ✅ 在布局中集成语言切换器

让我们开始！
