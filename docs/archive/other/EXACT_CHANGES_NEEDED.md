# Exact Code Changes Needed for Each Page

## Quick Reference

This document provides the exact before/after code for each file that needs updating.

---

## 1. Actors List

**File:** `/home/eric/video/admin-frontend/src/pages/Actors/List.tsx`

### Change 1: Add Import
```tsx
// Add after existing imports:
import '@/styles/page-layout.css'
```

### Change 2: Update Return Statement
Replace the entire return statement structure:

**BEFORE:**
```tsx
return (
  <Card
    title={t('menu.actors')}
    extra={
      <Button type="primary" icon={<PlusOutlined />} onClick={() => handleAdd()}>
        {t('common.add')}
      </Button>
    }
  >
    <Space style={{ marginBottom: 16 }}>
      <Input.Search ... />
    </Space>
    <Table ... />
  </Card>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <Input.Search ... />
        </div>
        <div className="page-header-right">
          <Button type="primary" icon={<PlusOutlined />} onClick={() => handleAdd()}>
            {t('common.add')}
          </Button>
        </div>
      </div>
    </div>

    <div className="page-content">
      <div className="table-container">
        <Table ... />
      </div>
    </div>
  </div>
)
```

---

## 2. Directors List

**File:** `/home/eric/video/admin-frontend/src/pages/Directors/List.tsx`

**Exact same pattern as Actors List** - just replace `t('menu.actors')` with `t('menu.directors')`

---

## 3. Series List

**File:** `/home/eric/video/admin-frontend/src/pages/Series/List.tsx`

### Add Import
```tsx
import '@/styles/page-layout.css'
```

### Update Return
**BEFORE:**
```tsx
return (
  <div>
    <Card style={{ marginBottom: 16 }}>
      <Title level={2}>{t('menu.series')}</Title>
      <Paragraph type="secondary">{t('series.description')}</Paragraph>
    </Card>

    <Card style={{ marginBottom: 16 }}>
      <Space wrap style={{ width: '100%', justifyContent: 'space-between' }}>
        <Space wrap>
          <Input.Search ... />
          <Select ... />
        </Space>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            {t('series.createAlbum')}
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            {t('common.refresh')}
          </Button>
        </Space>
      </Space>
    </Card>

    <Card>
      <Table ... />
    </Card>
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <Input.Search ... />
          <Select ... />
        </div>
        <div className="page-header-right">
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            {t('series.createAlbum')}
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            {t('common.refresh')}
          </Button>
        </div>
      </div>
    </div>

    <div className="page-content">
      <div className="table-container">
        <Table ... />
      </div>
    </div>
  </div>
)
```

---

## 4. Comments List

**File:** `/home/eric/video/admin-frontend/src/pages/Comments/List.tsx`

### Add Import
```tsx
import '@/styles/page-layout.css'
```

### Update Return
**BEFORE:**
```tsx
return (
  <div>
    <Card>
      <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }}>
        <Space>
          <Input.Search ... />
          <Select ... />
        </Space>
      </Space>

      {selectedRowKeys.length > 0 && (
        <div style={{ marginBottom: 16, padding: 12, background: '#f0f2f5', borderRadius: 8 }}>
          ...
        </div>
      )}

      <Table ... />
    </Card>
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <Input.Search ... />
          <Select ... />
        </div>
      </div>
    </div>

    {selectedRowKeys.length > 0 && (
      <div className="batch-operations">
        {/* Keep existing batch operations content */}
      </div>
    )}

    <div className="page-content">
      <div className="table-container">
        <Table ... />
      </div>
    </div>
  </div>
)
```

---

## 5. Banners List

**File:** `/home/eric/video/admin-frontend/src/pages/Banners/List.tsx`

### Add Import
```tsx
import '@/styles/page-layout.css'
```

### Update Return
**BEFORE:**
```tsx
return (
  <div style={{ padding: '24px' }}>
    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
      {/* Statistics cards */}
    </Row>

    <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
      <Space>
        <Select ... />
      </Space>
      <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
        {t('common.add')}
      </Button>
    </div>

    {selectedRowKeys.length > 0 && (
      <div style={{ marginBottom: 16, padding: 12, background: '#f0f2f5' }}>
        ...
      </div>
    )}

    <Card>
      <Table ... />
    </Card>
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <Select ... />
        </div>
        <div className="page-header-right">
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            {t('common.add')}
          </Button>
        </div>
      </div>
    </div>

    {selectedRowKeys.length > 0 && (
      <div className="batch-operations">
        {/* Keep existing batch operations content */}
      </div>
    )}

    <div className="page-content">
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {/* Keep statistics cards */}
      </Row>

      <div className="table-container">
        <Table ... />
      </div>
    </div>
  </div>
)
```

---

## 6. Announcements List

**File:** `/home/eric/video/admin-frontend/src/pages/Announcements/List.tsx`

### Add Import
```tsx
import '@/styles/page-layout.css'
```

### Update Return
**BEFORE:**
```tsx
return (
  <div>
    <Card>
      <Row justify="space-between" style={{ marginBottom: 16 }}>
        <Col>
          <Space>
            <Input.Search ... />
            <Select ... />
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            {t('common.add')}
          </Button>
        </Col>
      </Row>
      <Table ... />
    </Card>
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <Input.Search ... />
          <Select ... />
        </div>
        <div className="page-header-right">
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            {t('common.add')}
          </Button>
        </div>
      </div>
    </div>

    <div className="page-content">
      <div className="table-container">
        <Table ... />
      </div>
    </div>
  </div>
)
```

---

## 7-10. Pages with Tabs (Logs, Roles, Email, AI Management)

For pages with tabs, the pattern is slightly different:

### Generic Pattern
```tsx
import '@/styles/page-layout.css'

return (
  <div className="page-container">
    {/* Optional: Page title header */}
    <div className="page-header">
      <div className="page-header-content">
        <h2>Page Title</h2>
        {/* OR keep as Card if preferred */}
      </div>
    </div>

    <div className="page-content">
      {/* Keep Tabs structure */}
      <Card>
        <Tabs items={...} />
      </Card>
    </div>
  </div>
)
```

### Specific: Logs Page

**File:** `/home/eric/video/admin-frontend/src/pages/Logs.tsx`

**BEFORE:**
```tsx
return (
  <div>
    <h2 style={{ marginBottom: 24 }}>系统日志</h2>
    <Card>
      <Tabs ... />
    </Card>
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-content">
      <Card>
        <Tabs ... />
      </Card>
    </div>
  </div>
)
```

Note: Remove the h2, the page title is handled by sidebar/breadcrumb.

---

## 11. Email Management

**File:** `/home/eric/video/admin-frontend/src/pages/Email/Management.tsx`

**BEFORE:**
```tsx
return (
  <div style={{ padding: '24px' }}>
    <Card>
      <Title level={2}>{t('menu.emailManagement') || '邮件管理'}</Title>
      <Paragraph type="secondary">...</Paragraph>
    </Card>

    <Card style={{ marginTop: 16 }}>
      <Tabs items={...} />
    </Card>

    {/* Modals */}
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-content">
      <Card style={{ marginBottom: 16 }}>
        <Title level={2}>{t('menu.emailManagement') || '邮件管理'}</Title>
        <Paragraph type="secondary">...</Paragraph>
      </Card>

      <Card>
        <Tabs items={...} />
      </Card>
    </div>

    {/* Modals */}
  </div>
)
```

---

## 12. IP Blacklist

**File:** `/home/eric/video/admin-frontend/src/pages/IPBlacklist/index.tsx`

**BEFORE:**
```tsx
return (
  <div style={{ padding: '24px' }}>
    <h2>IP黑名单管理</h2>

    <Row gutter={16} style={{ marginBottom: 24 }}>
      {/* Statistics */}
    </Row>

    <Card style={{ marginBottom: 16 }}>
      <Space style={{ marginBottom: 16 }}>
        {/* Buttons */}
      </Space>
      <Input.Search ... />
    </Card>

    <Card>
      <Table ... />
    </Card>

    {/* Modal */}
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <Input.Search ... />
        </div>
        <div className="page-header-right">
          <Space>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddModalVisible(true)}>
              添加IP
            </Button>
            <Button danger icon={<DeleteOutlined />} onClick={handleBatchDelete} disabled={...}>
              批量移除 ({selectedRows.length})
            </Button>
            <Button icon={<ReloadOutlined />} onClick={loadData}>
              刷新
            </Button>
          </Space>
        </div>
      </div>
    </div>

    <div className="page-content">
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* Keep statistics */}
      </Row>

      <div className="table-container">
        <Table ... />
      </div>
    </div>

    {/* Modal */}
  </div>
)
```

---

## 13. AI Management

**File:** `/home/eric/video/admin-frontend/src/pages/AIManagement/index.tsx`

**BEFORE:**
```tsx
return (
  <div className="ai-management-page">
    <div className="page-header" style={{ marginBottom: 24 }}>
      <div className="header-content">
        <div className="header-title">...</div>
        <Button ... />
      </div>
    </div>

    {usageStats && (
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* Statistics */}
      </Row>
    )}

    <Card bordered={false}>
      <Tabs ... />
      <Table ... />
    </Card>

    {/* Modals */}
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <RobotOutlined style={{ fontSize: 28, marginRight: 12 }} />
          <div>
            <h2 style={{ margin: 0 }}>{t('ai.title')}</h2>
            <p style={{ margin: 0, color: '#999', fontSize: 14 }}>{t('ai.subtitle')}</p>
          </div>
        </div>
        <div className="page-header-right">
          <Button type="primary" size="large" icon={<PlusOutlined />} onClick={() => setFormVisible(true)}>
            {t('ai.addProvider')}
          </Button>
        </div>
      </div>
    </div>

    <div className="page-content">
      {usageStats && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          {/* Keep statistics */}
        </Row>
      )}

      <div className="table-container">
        <Card bordered={false}>
          <Tabs ... />
          <Table ... />
        </Card>
      </div>
    </div>

    {/* Modals */}
  </div>
)
```

---

## 14. Reports Dashboard

**File:** `/home/eric/video/admin-frontend/src/pages/Reports/Dashboard.tsx`

**BEFORE:**
```tsx
return (
  <div style={{ padding: '24px' }}>
    <Card>
      <Row justify="space-between" align="middle">
        <Col>
          <Title level={2}>...</Title>
          <Text type="secondary">...</Text>
        </Col>
      </Row>
    </Card>

    <Card style={{ marginTop: 16 }}>
      <Row gutter={16} align="middle">
        {/* Filters */}
      </Row>
    </Card>

    <div style={{ marginTop: 16 }}>
      <Spin spinning={isLoading}>
        {/* Report content */}
      </Spin>
    </div>
  </div>
)
```

**AFTER:**
```tsx
return (
  <div className="page-container">
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          <Space>
            <Text strong>{t('reports.reportType')}:</Text>
            <Select value={reportType} onChange={setReportType} style={{ width: 200 }}>
              ...
            </Select>
          </Space>
          <Space>
            <Text strong>{t('reports.timePeriod')}:</Text>
            <Select value={days} onChange={setDays} style={{ width: 120 }}>
              ...
            </Select>
          </Space>
        </div>
        <div className="page-header-right">
          <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport} loading={exporting}>
            {t('common.export')}
          </Button>
        </div>
      </div>
    </div>

    <div className="page-content">
      <Spin spinning={isLoading}>
        {/* Keep all report rendering functions as-is */}
        {reportType === 'user-activity' && renderUserActivityReport()}
        {reportType === 'content-performance' && renderContentPerformanceReport()}
        {reportType === 'vip-subscription' && renderVIPSubscriptionReport()}
      </Spin>
    </div>
  </div>
)
```

---

## 15. Scheduling List (Special Case)

**File:** `/home/eric/video/admin-frontend/src/pages/Scheduling/List.tsx`

**Note:** This page has a complex layout with multiple sections. Consider minimal changes:

### Option A: Minimal Change
Just wrap in page-container and move padding:

```tsx
return (
  <div className="page-container">
    <div className="page-content">
      {/* Keep all existing Card structure */}
      <Card>...</Card>
      <Row>...</Row>
      <Card>...</Card>
      <Card>...</Card>
    </div>
  </div>
)
```

### Option B: Full Update
Apply full layout pattern with header containing view toggle and filters.

**Recommended:** Option A for Scheduling to preserve custom layout.

---

## Summary of Changes

For each file:
1. Add `import '@/styles/page-layout.css'` after existing imports
2. Replace outer `<div>` or `<div style={{ padding: '24px' }}>` with `<div className="page-container">`
3. Structure header elements in `page-header` > `page-header-content` > `page-header-left` + `page-header-right`
4. Wrap batch operations in `<div className="batch-operations">`
5. Wrap main content in `<div className="page-content">`
6. Wrap tables in `<div className="table-container">`
7. Remove unnecessary inline styles (padding, marginBottom, etc.)
8. Keep all existing functionality, props, handlers unchanged

## Testing After Changes

For each page:
- [ ] Page renders without errors
- [ ] Full-screen height layout applied
- [ ] Header fixed at top
- [ ] Table scrolls independently
- [ ] Filters and buttons work
- [ ] Responsive behavior intact
- [ ] No console errors

---

**Total Files:** 14
**Completed:** 1 (Users List)
**Remaining:** 13
**Pattern:** Consistent across all pages
**Risk:** Low (layout only, no logic changes)
