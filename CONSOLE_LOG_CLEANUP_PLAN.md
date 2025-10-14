# Console.log 清理计划

## 📊 统计

- **Frontend**: 36 个 console 调用
- **Admin Frontend**: 13 个 console 调用

## ✅ 需要保留的（47 个）

### 错误和警告日志（必须保留）

- ✅ 所有 `console.error` - 用于错误追踪
- ✅ 所有 `console.warn` - 用于警告提示
- ✅ 有条件判断的日志（`process.env.NODE_ENV === 'development'`）

### WebSocket 日志（建议保留）

- ✅ Admin Frontend WebSocket 连接日志 - 对调试很有帮助

## ❌ 建议删除的（15 个调试日志）

### Frontend

#### 1. VideoPlayer 播放状态日志 (4 个)

**文件**: `frontend/src/components/VideoPlayer/index.tsx`

```typescript
// 行 314 - 删除
console.log('Fullscreen:', isFullscreen);

// 行 349 - 删除
console.log('Buffering...');

// 行 354 - 删除
console.log('Can play - buffering complete');

// 行 364 - 删除（缓冲百分比）
console.log(`Buffered: ${bufferedPercent.toFixed(1)}%`);
```

#### 2. 画质切换日志 (2 个)

**文件**: `frontend/src/components/VideoPlayer/index.tsx`

```typescript
// 行 409 - 删除
console.log('Selected quality:', quality);

// 行 614 - 删除
console.log('Change quality to:', quality);
```

#### 3. 字幕加载日志 (2 个)

**文件**: `frontend/src/components/VideoPlayer/index.tsx`

```typescript
// 行 783 - 可删除
console.log('该视频没有字幕');

// 行 810-811 - 可删除
console.log(`✅ 字幕已加载: ${subtitle.language_name} (${subtitle.language})`);
```

#### 4. AV1Player 调试日志 (7 个)

**文件**: `frontend/src/components/VideoPlayer/AV1Player.tsx`

```typescript
// 行 46-47 - 删除
console.log('浏览器信息:', browserInfo);
console.log('AV1支持:', supportsAV1());

// 行 89-91 - 删除
console.log('✅ 视频元数据加载完成');
console.log('使用编解码器:', codec === 'av1' ? 'AV1 (dav1d)' : 'H.264');
console.log('视频URL:', videoUrl);

// 行 95 - 删除
console.log('▶️ 播放开始');

// 行 100 - 删除
console.log('⏸️ 播放暂停');

// 行 105 - 删除
console.log('✅ 播放结束');

// 行 132 - 删除
console.log('画质切换');
```

#### 5. PWA 安装日志 (1 个)

**文件**: `frontend/src/components/PWAInstallPrompt/index.tsx`

```typescript
// 行 45 - 删除
console.log(`PWA install outcome: ${outcome}`);
```

#### 6. 自动播放日志 (2 个)

**文件**: `frontend/src/hooks/useAutoPlay.ts`

```typescript
// 行 84 - 删除
console.log('No next video in playlist');

// 行 101 - 删除
console.log('No previous video in playlist');
```

#### 7. 编解码器选择日志 (2 个)

**文件**: `frontend/src/utils/codecSupport.ts`

```typescript
// 行 138 - 删除
console.log('✅ 使用AV1格式 (dav1d解码器,节省56%带宽)');

// 行 143 - 删除
console.log('⚠️ 降级到H.264格式 (兼容模式)');
```

---

## 🟡 可选清理（性能日志）

### Performance 工具日志

**文件**: `frontend/src/utils/performance.ts`

这些日志对性能监控很有用，建议保留或改为条件输出：

```typescript
// 建议保留（或添加开发环境判断）
console.log('📊 Web Vital:', metric.name, metric.value, metric.rating);
console.log('📈 Page Performance Metrics:', metrics);
console.log(`⏱️ API Call [${name}]: ${duration.toFixed(2)}ms`);
console.log(`💾 Memory: ${usedMB}MB / ${totalMB}MB (Limit: ${limitMB}MB)`);
```

---

## 📋 执行计划

### 方案 A: 手动清理（推荐）

逐个文件检查并删除，确保不误删

### 方案 B: 批量替换（风险较高）

使用 sed 或脚本批量删除特定的 console.log

### 方案 C: 生产构建配置（最佳实践）

在 Vite 配置中自动删除 console.log：

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 生产环境自动删除所有 console
        drop_debugger: true,
      },
    },
  },
});
```

---

## ✅ 推荐方案

**组合方式**：

1. **现在**: 手动删除明显的调试日志（15 个）
2. **配置**: 添加 Vite terser 配置，生产环境自动删除所有 console
3. **开发**: 保留 console.error 和 console.warn 用于开发调试

这样既保持代码清洁，又不影响开发体验。

---

## 🎯 估计工作量

- 手动清理 15 个调试日志: **15 分钟**
- 配置 Vite terser: **5 分钟**
- 总计: **20 分钟**
