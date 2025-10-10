# Netflix 配色系统应用指南

## 配色方案

### 主要颜色
```css
--netflix-red: #E50914        /* Netflix 标志性红色 */
--netflix-red-dark: #B20710   /* 深红色（hover状态） */
--netflix-black: #141414      /* 主背景色 */
--netflix-gray-dark: #2F2F2F  /* 卡片背景 */
--netflix-gray-medium: #808080 /* 次要文字 */
--netflix-gray-light: #B3B3B3  /* 普通文字 */
--netflix-hover: #3F3F3F      /* hover 状态背景 */
```

## 使用指南

### 1. 背景色
```tsx
// 主背景
className="bg-netflix-black"

// 卡片背景
className="bg-netflix-card"

// Hover 状态
className="hover:bg-netflix-hover"
```

### 2. 文字颜色
```tsx
// 主文字（白色）
className="text-white"

// 次要文字
className="text-netflix-gray-light"

// 弱化文字
className="text-netflix-gray-medium"
```

### 3. 按钮
```tsx
// 主要按钮（红色）
className="bg-netflix-red hover:bg-netflix-red-dark"

// 次要按钮
className="btn-secondary"
```

### 4. 边框
```tsx
className="border-netflix-border"
```

## 组件示例

### VideoCard
```tsx
<div className="card hover:ring-2 hover:ring-netflix-red">
  {/* 内容 */}
</div>
```

### Header
```tsx
<header className="bg-netflix-black border-b border-netflix-border">
  <button className="bg-netflix-red hover:bg-netflix-red-dark">
    登录
  </button>
</header>
```

### 播放按钮
```tsx
<button className="bg-netflix-red rounded-full p-4 hover:bg-netflix-red-dark">
  <Play />
</button>
```

## 快速替换规则

将现有颜色替换为 Netflix 风格：

| 原颜色 | Netflix 颜色 |
|--------|-------------|
| `red-600` | `netflix-red` |
| `red-700` | `netflix-red-dark` |
| `gray-800` | `netflix-card` |
| `gray-900` | `netflix-black` |
| `gray-400` | `netflix-gray-light` |
| `gray-600` | `netflix-gray-medium` |

## 已更新的文件

- ✅ `frontend/tailwind.config.js` - 添加 Netflix 颜色
- ✅ `frontend/src/index.css` - 全局 Netflix 样式

## 需要更新的关键组件

建议手动更新以下组件以获得最佳效果：

1. **Header** - 顶部导航栏
2. **VideoCard** - 视频卡片（最重要）
3. **HeroCarousel** - 首页轮播图
4. **Button 组件** - 所有按钮
5. **Footer** - 底部

## 自动化替换脚本（可选）

```bash
# 在 frontend/src 目录下批量替换
find . -name "*.tsx" -type f -exec sed -i 's/red-600/netflix-red/g' {} \;
find . -name "*.tsx" -type f -exec sed -i 's/red-700/netflix-red-dark/g' {} \;
find . -name "*.tsx" -type f -exec sed -i 's/gray-800/netflix-card/g' {} \;
find . -name "*.tsx" -type f -exec sed -i 's/gray-900/netflix-black/g' {} \;
```

**注意**: 建议手动检查每个替换，确保不影响功能

## 验证

启动开发服务器查看效果：

```bash
cd frontend
pnpm run dev
```

访问 http://localhost:3000 应该看到：
- ✅ 深黑色背景 (#141414)
- ✅ Netflix 红色按钮和链接
- ✅ 深灰色卡片背景
- ✅ Hover 效果更明显
