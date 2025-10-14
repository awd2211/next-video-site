# 将通知设置集成到 Settings 页面

## 修改步骤

### 1. 在 `Settings.tsx` 文件开头添加 import

```typescript
// 在 import 部分添加
import NotificationSettings from '../components/NotificationSettings';
```

### 2. 在 sections 配置中添加通知面板（第 263 行之后）

在 `security` 和 `cache` 之间添加:

```typescript
{
  key: 'notifications',
  title: '🔔 通知设置',
  keywords: '通知 notifications 声音 桌面 免打扰 sound desktop',
  defaultOpen: false,
},
```

### 3. 在 Collapse 组件中添加通知面板（第 730 行之后，cache 面板之前）

```typescript
{/* Panel 6: 通知设置 */}
{filteredSections.find((s) => s.key === 'notifications') && (
  <Panel header="🔔 通知设置" key="notifications" className="settings-panel">
    <p className="panel-description">配置通知方式、声音、桌面通知和免打扰时段</p>
    
    <NotificationSettings />
  </Panel>
)}
```

## 完整代码参考

```typescript
// settings.tsx 添加 section (line 263)
{
  key: 'notifications',
  title: '🔔 通知设置',
  keywords: '通知 notifications 声音 桌面 免打扰 sound desktop',
  defaultOpen: false,
},
```

```typescript
// settings.tsx 添加 Panel (line 730)
{/* Panel 6: 通知设置 */}
{filteredSections.find((s) => s.key === 'notifications') && (
  <Panel header="🔔 通知设置" key="notifications" className="settings-panel">
    <p className="panel-description">配置通知方式、声音、桌面通知和免打扰时段</p>
    
    <NotificationSettings />
  </Panel>
)}
```

## 自动化应用（选项 A）

```bash
# 使用 sed 自动添加
cd /home/eric/video/admin-frontend/src/pages

# 1. 添加 import
sed -i "43a import NotificationSettings from '../components/NotificationSettings';" Settings.tsx

# 2. 添加 section（在 security 后面）
sed -i "/key: 'security',/,/},/a\\    {\\n      key: 'notifications',\\n      title: '🔔 通知设置',\\n      keywords: '通知 notifications 声音 桌面 免打扰 sound desktop',\\n      defaultOpen: false,\\n    }," Settings.tsx

# 3. 添加 Panel（在 cache 面板之前，需要找到准确位置）
```

## 手动应用（选项 B - 推荐）

直接编辑 `/home/eric/video/admin-frontend/src/pages/Settings.tsx`:

1. 第 43 行后添加： `import NotificationSettings from '../components/NotificationSettings';`

2. 找到 sections 配置（约 232-281 行），在 `security` 和 `cache` 之间添加:
   ```typescript
   {
     key: 'notifications',
     title: '🔔 通知设置',
     keywords: '通知 notifications 声音 桌面 免打扰 sound desktop',
     defaultOpen: false,
   },
   ```

3. 找到 Panel 6 (缓存管理)，在它之前添加新的 Panel:
   ```typescript
   {/* Panel 6: 通知设置 */}
   {filteredSections.find((s) => s.key === 'notifications') && (
     <Panel header="🔔 通知设置" key="notifications" className="settings-panel">
       <p className="panel-description">配置通知方式、声音、桌面通知和免打扰时段</p>
       
       <NotificationSettings />
     </Panel>
   )}
   ```

4. 更新后面的 Panel 编号（原 Panel 6 变成 Panel 7，以此类推）

完成后，通知设置将出现在 Settings 页面中！
