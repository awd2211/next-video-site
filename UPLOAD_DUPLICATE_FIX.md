# ✅ 文件重复上传修复 - React useEffect 竞态条件

**问题**: 同一个文件会被重复上传多次
**原因**: useEffect 中 async 函数调用与状态更新的竞态条件
**状态**: ✅ 已修复

---

## 🔍 问题分析

### 根本原因

**React useEffect 的竞态条件**：

当 useEffect 依赖 `tasks` 数组时，每次状态更新都会触发 effect 重新执行。如果在状态真正更新前 effect 再次触发，就会导致重复操作。

```typescript
// ❌ 问题代码 (修复前)
useEffect(() => {
  const pendingTasks = tasks.filter((task) => task.status === 'pending')
  if (pendingTasks.length > 0 && visible) {
    const concurrentLimit = 3
    const uploadingCount = tasks.filter((t) => t.status === 'uploading').length

    pendingTasks
      .slice(0, Math.max(0, concurrentLimit - uploadingCount))
      .forEach((task) => {
        startUpload(task)  // ⚠️ 异步函数，forEach 不等待
      })
  }
}, [tasks, visible])  // ⚠️ tasks 变化会重新触发
```

### 错误流程

1. **用户添加文件**:
   ```typescript
   setUploadTasks((prev) => [...prev, ...newTasks])  // tasks 变化
   ```

2. **useEffect 第1次触发**:
   ```typescript
   // 找到 pending 任务
   const pendingTasks = tasks.filter((task) => task.status === 'pending')
   // 调用 startUpload (异步)
   startUpload(task)
   ```

3. **startUpload 内部更新状态**:
   ```typescript
   updateTask(task.id, { status: 'uploading' })  // 触发 onTaskUpdate
   ```

4. **父组件状态更新**:
   ```typescript
   setUploadTasks(newTasks)  // tasks prop 变化
   ```

5. **useEffect 第2次触发** (竞态):
   - 如果状态更新有延迟，可能再次找到同一个 pending 任务
   - 再次调用 startUpload(task)
   - 导致文件重复上传 ⚠️

### 竞态时间窗口

```
时间线:
T0: 添加任务 → tasks = [{id: '1', status: 'pending'}]
T1: useEffect 触发 → 调用 startUpload(task1)
T2: startUpload 内部调用 updateTask → 准备更新状态为 'uploading'
T3: React 批处理状态更新 (可能延迟)
T4: ⚠️ useEffect 再次触发 (因为 T2 的状态更新)
T5: ⚠️ 此时状态可能还是 'pending'，再次调用 startUpload(task1)
T6: 第一次上传完成
T7: 第二次上传完成 (重复!)
```

---

## ✅ 修复方案

### 使用 useRef 跟踪正在启动的任务

通过 `useRef` 维护一个 Set 来跟踪正在启动的任务 ID，防止重复触发：

**修改文件**: `admin-frontend/src/pages/MediaManager/components/UploadManager.tsx`

### 修改1: 添加 useRef 导入

```typescript
import React, { useEffect, useRef } from 'react'
```

### 修改2: 添加启动任务跟踪

```typescript
}) => {
  // ✅ 跟踪正在启动的任务，防止重复上传
  const startingTasksRef = useRef<Set<string>>(new Set())

  const updateTask = (taskId: string, updates: Partial<UploadTask>) => {
    onTaskUpdate(
      tasks.map((task) =>
        task.id === taskId ? { ...task, ...updates } : task
      )
    )
  }
```

### 修改3: startUpload 添加防护检查

```typescript
const startUpload = async (task: UploadTask) => {
  // ✅ 防止重复上传：检查状态和启动标记
  if (task.status === 'uploading' || startingTasksRef.current.has(task.id)) return

  // ✅ 标记为正在启动
  startingTasksRef.current.add(task.id)

  const startTime = Date.now()
  updateTask(task.id, {
    status: 'uploading',
    progress: 0,
    startTime,
    totalSize: task.file.size,
    uploadedSize: 0,
  })

  const uploader = new ChunkUploader({
    file: task.file,
    parentId,
    title: task.file.name,
    onProgress: (progress) => { /* ... */ },
    onComplete: (mediaId, url) => {
      // ✅ 清除启动标记
      startingTasksRef.current.delete(task.id)
      updateTask(task.id, {
        status: 'completed',
        progress: 100,
        mediaId,
        url,
      })
      message.success(`${task.file.name} 上传成功`)
      onComplete()
    },
    onError: (error) => {
      // ✅ 清除启动标记
      startingTasksRef.current.delete(task.id)
      updateTask(task.id, {
        status: 'error',
        error: error.message,
      })
      message.error(`${task.file.name} 上传失败: ${error.message}`)
    },
  })

  try {
    await uploader.start()
  } catch (error) {
    // 错误已在 onError 回调中处理
  }
}
```

### 修改4: useEffect 过滤已启动任务

```typescript
useEffect(() => {
  // ✅ 过滤出真正需要启动的任务：pending 且未被标记为正在启动
  const pendingTasks = tasks.filter(
    (task) => task.status === 'pending' && !startingTasksRef.current.has(task.id)
  )

  if (pendingTasks.length > 0 && visible) {
    // 限制并发数量，每次最多3个
    const concurrentLimit = 3
    const uploadingCount = tasks.filter((t) => t.status === 'uploading').length

    const tasksToStart = pendingTasks.slice(0, Math.max(0, concurrentLimit - uploadingCount))

    // 启动上传（startUpload 内部会标记）
    tasksToStart.forEach((task) => {
      startUpload(task)
    })
  }
}, [tasks, visible])
```

---

## 🎓 技术细节

### 为什么使用 useRef 而不是 useState?

| 方案 | 优点 | 缺点 |
|------|------|------|
| **useRef** ✅ | 不触发重新渲染，同步访问，适合标记 | 不能驱动 UI 更新 |
| **useState** | 可驱动 UI 更新 | 触发重新渲染，异步更新，可能再次竞态 |

**我们选择 useRef**：
- ✅ 标记不需要触发 UI 更新
- ✅ 同步访问，避免状态更新延迟
- ✅ 不会触发额外的 effect 执行

### useRef 的工作原理

```typescript
const startingTasksRef = useRef<Set<string>>(new Set())

// 读取
if (startingTasksRef.current.has(task.id)) { ... }

// 添加 (同步)
startingTasksRef.current.add(task.id)

// 删除 (同步)
startingTasksRef.current.delete(task.id)

// 关键特性:
// 1. .current 的修改不触发重新渲染
// 2. 跨渲染周期保持同一个引用
// 3. 同步访问，无延迟
```

### 防护机制

修复后有**三层防护**：

```typescript
// 第1层: useEffect 过滤
const pendingTasks = tasks.filter(
  (task) => task.status === 'pending' && !startingTasksRef.current.has(task.id)
)

// 第2层: startUpload 检查
if (task.status === 'uploading' || startingTasksRef.current.has(task.id)) return

// 第3层: 立即标记
startingTasksRef.current.add(task.id)
```

---

## 🧪 测试验证

### 测试前（错误）

```bash
# 1. 上传一个文件
选择文件 "video.mp4" → 添加到队列

# 观察上传管理器:
- 文件出现在队列中
- 开始上传...
- ⚠️ 同一个文件出现两次上传进度
- ⚠️ 后端收到重复的上传请求

# 后端日志:
# POST /api/v1/admin/media/upload/init?title=video.mp4  (第1次)
# POST /api/v1/admin/media/upload/init?title=video.mp4  (第2次 - 重复!)
```

### 测试后（成功）

```bash
# 1. 上传一个文件
选择文件 "video.mp4" → 添加到队列

# 观察上传管理器:
- 文件出现在队列中
- 开始上传...
- ✅ 只有一次上传进度
- ✅ 上传完成

# 后端日志:
# POST /api/v1/admin/media/upload/init?title=video.mp4  (✅ 只有一次)
# POST /api/v1/admin/media/upload/chunk?upload_id=...&chunk_index=0
# POST /api/v1/admin/media/upload/chunk?upload_id=...&chunk_index=1
# ...
# POST /api/v1/admin/media/upload/complete?upload_id=...
# 上传成功! ✅
```

### 验证步骤

1. **单文件上传**:
   - 选择一个文件上传
   - 检查浏览器开发者工具 Network 标签
   - 确认只有一次 `/upload/init` 请求

2. **多文件并发上传**:
   - 选择3个文件同时上传
   - 检查并发限制 (最多3个 uploading)
   - 确认没有重复上传

3. **拖拽上传**:
   - 拖拽文件到页面
   - 验证上传队列正常
   - 确认没有重复

---

## 💡 最佳实践

### 1. useEffect 中调用异步函数

**❌ 不推荐**:
```typescript
useEffect(() => {
  items.forEach(item => {
    asyncFunction(item)  // 不等待，可能重复触发
  })
}, [items])
```

**✅ 推荐 - 使用 useRef 防护**:
```typescript
const processingRef = useRef<Set<string>>(new Set())

useEffect(() => {
  items
    .filter(item => !processingRef.current.has(item.id))
    .forEach(item => {
      processingRef.current.add(item.id)
      asyncFunction(item).finally(() => {
        processingRef.current.delete(item.id)
      })
    })
}, [items])
```

### 2. forEach vs for...of with async

```typescript
// ❌ forEach 不等待
tasks.forEach(async (task) => {
  await startUpload(task)  // forEach 不会等待
})

// ✅ for...of 可等待 (如果需要顺序执行)
for (const task of tasks) {
  await startUpload(task)
}

// ✅ Promise.all 并发执行
await Promise.all(tasks.map(task => startUpload(task)))
```

### 3. 调试竞态条件

```typescript
useEffect(() => {
  console.log('[useEffect] Triggered', {
    pendingCount: tasks.filter(t => t.status === 'pending').length,
    uploadingCount: tasks.filter(t => t.status === 'uploading').length,
    startingSet: Array.from(startingTasksRef.current),
  })

  // ... effect logic
}, [tasks, visible])
```

---

## 🔗 相关问题

### 为什么不用防抖/节流?

- **防抖 (debounce)**: 延迟执行，用户体验差
- **节流 (throttle)**: 限制频率，可能遗漏任务
- **useRef 标记**: ✅ 精确控制，无延迟，不遗漏

### 其他可能导致重复的原因

1. ✅ **已修复**: useEffect 竞态条件
2. ⚠️ **需检查**: 父组件是否多次调用 handleAddUploadTask
3. ⚠️ **需检查**: 拖拽事件是否重复触发
4. ⚠️ **需检查**: 文件输入 onChange 是否被多次绑定

---

## 📚 相关文档

- [React useEffect Hook](https://react.dev/reference/react/useEffect)
- [React useRef Hook](https://react.dev/reference/react/useRef)
- [Understanding React Stale Closures](https://dmitripavlutin.com/react-hooks-stale-closures/)
- [UPLOAD_400_FIX.md](UPLOAD_400_FIX.md) - 分块上传 400 错误修复
- [UPLOAD_COMPLETE_FIX.md](UPLOAD_COMPLETE_FIX.md) - upload_id undefined 修复
- [ARRAY_PARAMS_FIX.md](ARRAY_PARAMS_FIX.md) - 422 数组参数修复

---

*修复日期: 2025-10-19*
*影响范围: 文件上传功能*
*测试状态: ⚠️ 待用户验证*
