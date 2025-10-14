# Full-Screen Layout Update Guide

## Summary

This guide provides the exact changes needed to update all admin pages to use the full-screen height layout style consistent with the MediaManager page.

## Completed

✅ **Users List** (`/home/eric/video/admin-frontend/src/pages/Users/List.tsx`)
- Added import for page-layout.css
- Wrapped content in page-container structure
- Moved statistics cards into page-content
- Properly structured header with filters and action buttons
- Batch operations section added between header and content

## Pattern to Follow

For all remaining pages, follow this structure:

### 1. Add Import

```tsx
import '@/styles/page-layout.css'
```

### 2. Change Return Structure

From:
```tsx
return (
  <div>
    {/* or <div style={{ padding: '24px' }}> */}
    {/* Header/filters */}
    {/* Table */}
  </div>
)
```

To:
```tsx
return (
  <div className="page-container">
    {/* Page Header */}
    <div className="page-header">
      <div className="page-header-content">
        <div className="page-header-left">
          {/* Search boxes, filters */}
        </div>
        <div className="page-header-right">
          {/* Action buttons like Add, Export */}
        </div>
      </div>
    </div>

    {/* Batch operations (if applicable) */}
    {selectedRowKeys.length > 0 && (
      <div className="batch-operations">
        {/* Batch action buttons */}
      </div>
    )}

    {/* Page Content */}
    <div className="page-content">
      {/* Statistics cards (if any) */}
      {/* Table container */}
      <div className="table-container">
        <Table ... />
      </div>
    </div>
  </div>
)
```

## Files to Update

### 2. Actors List (`/home/eric/video/admin-frontend/src/pages/Actors/List.tsx`)

**Current structure:** Wrapped in `<Card>` with title and extra button
**Changes needed:**
- Add import
- Remove outer Card wrapper
- Move "Add Actor" button to page-header-right
- Wrap Table in page-container > page-content > table-container structure

### 3. Directors List (`/home/eric/video/admin-frontend/src/pages/Directors/List.tsx`)

**Same pattern as Actors List**

### 4. Series List (`/home/eric/video/admin-frontend/src/pages/Series/List.tsx`)

**Current structure:** Has header Card, filter Card, and data Card
**Changes needed:**
- Add import
- Convert header Card content to page-header
- Move filters and actions to page-header-content
- Move "Create Album" and "Refresh" buttons to page-header-right
- Wrap Table in page-content > table-container

### 5. Comments List (`/home/eric/video/admin-frontend/src/pages/Comments/List.tsx`)

**Current structure:** Single div > Card > filters + Table
**Changes needed:**
- Add import
- Convert Card to page-container structure
- Move search and status filters to page-header-left
- Batch operation buttons already in good position, wrap in batch-operations div
- Wrap Table in page-content > table-container

### 6. Banners List (`/home/eric/video/admin-frontend/src/pages/Banners/List.tsx`)

**Current structure:** Outer div > Statistics Row > Filter div > Batch div > Card with Table
**Changes needed:**
- Add import
- Remove outer padding div
- Create page-header with status filter and actions
- Keep batch operations div with batch-operations class
- Move statistics Row into page-content (above table-container)
- Wrap Table Card content in table-container

### 7. Announcements List (`/home/eric/video/admin-frontend/src/pages/Announcements/List.tsx`)

**Current structure:** Single div > Card > Row with buttons and filters + Table
**Changes needed:**
- Add import
- Remove Card wrapper
- Convert Row to page-header structure
- Buttons and filters distributed properly
- Wrap Table in page-content > table-container

### 8. Scheduling List (`/home/eric/video/admin-frontend/src/pages/Scheduling/List.tsx`)

**Current structure:** Complex with multiple Cards (header, statistics, filters, batch ops, table)
**Changes needed:**
- Add import
- Remove outer padding div
- Convert first Card (with calendar/list buttons) to page-header
- Keep statistics Row as-is in page-content
- Convert filter Card to page-header (second header if needed, or combine)
- Keep batch operations Card as batch-operations div
- Wrap Table Card in page-content > table-container

**Note:** This page is complex with multiple sections. Consider keeping it mostly as-is but wrapping in page-container for consistency.

### 9. Roles List (`/home/eric/video/admin-frontend/src/pages/Roles/List.tsx`)

**Current structure:** Single div > Tabs > Each tab has Card wrapper
**Changes needed:**
- Add import
- Wrap entire content in page-container
- Keep Tabs structure
- For each tab's Card:
  - Convert Card title/extra to page-header within the tab content
  - Wrap Table in table-container

**Note:** Tabs layout is special - keep Tabs at root level within page-container, apply layout within each tab.

### 10. Logs (`/home/eric/video/admin-frontend/src/pages/Logs.tsx`)

**Current structure:** Similar to Roles - outer div > Card > Tabs > Each tab has filters + Table
**Changes needed:**
- Add import
- Wrap in page-container
- Remove h2 and outer Card
- Keep Tabs
- For each tab component (OperationLogsTab, LoginLogsTab, etc.):
  - Wrap filters in page-header
  - Wrap Table in table-container

### 11. Email Management (`/home/eric/video/admin-frontend/src/pages/Email/Management.tsx`)

**Current structure:** Outer div with padding > Header Card > Tabs Card > Each tab has content
**Changes needed:**
- Add import
- Remove outer padding div
- Convert first Card (with Title) to page-header
- Keep Tabs Card structure
- For Configuration tab:
  - Wrap Alert and Button in page-header (or keep above table)
  - Wrap Table in table-container
- Similar for Templates tab

### 12. IP Blacklist (`/home/eric/video/admin-frontend/src/pages/IPBlacklist/index.tsx`)

**Current structure:** Outer div with padding > h2 > Statistics Row > Operations Card > Data Card
**Changes needed:**
- Add import
- Remove outer padding div
- Remove h2
- Keep Statistics Row in page-content
- Convert Operations Card to page-header with search and buttons
- Wrap batch operations in batch-operations div
- Convert Data Card to table-container within page-content

### 13. AI Management (`/home/eric/video/admin-frontend/src/pages/AIManagement/index.tsx`)

**Current structure:** Div with custom class > Header div > Statistics Row > Tabs Card
**Changes needed:**
- Add import
- Replace custom div.ai-management-page with page-container
- Keep header-content structure or convert to page-header
- Keep Statistics Row in page-content
- Keep Tabs Card structure
- Wrap Table in table-container

### 14. Reports Dashboard (`/home/eric/video/admin-frontend/src/pages/Reports/Dashboard.tsx`)

**Current structure:** Outer div with padding > Header Card > Filters Card > Report Content
**Changes needed:**
- Add import
- Remove outer padding div
- Convert Header Card to page-header (or keep as-is since it's a title card)
- Convert Filters Card to page-header with filter controls and export button
- Keep report content in page-content
- Wrap any tables in table-container

## Special Cases

### Pages with Statistics Cards

For pages like Users, Banners, and IP Blacklist that have statistics cards:
- Place statistics cards inside `page-content` at the top
- Place table-container below the statistics

### Pages with Tabs

For pages like Roles, Logs, Email Management, and AI Management:
- Wrap entire page in `page-container`
- Keep Tabs component structure
- Apply layout classes within each tab's content

### Pages with Complex Layouts

For Scheduling List with multiple sections:
- Consider keeping most Cards but wrapping in page-container
- Use page-header for top controls
- Use page-content for main content area

## CSS Classes Reference

From `/home/eric/video/admin-frontend/src/styles/page-layout.css`:

- `.page-container` - Full-screen height container (calc(100vh - 64px))
- `.page-header` - Fixed header with padding and border
- `.page-header-content` - Flex container for header items
- `.page-header-left` - Left side of header (filters, search)
- `.page-header-right` - Right side of header (action buttons)
- `.batch-operations` - Blue background bar for batch actions
- `.page-content` - Scrollable content area with padding
- `.table-container` - White card wrapper for tables

## Benefits

After updating all pages:
- Consistent full-screen height layout across all admin pages
- Better space utilization
- No more varied padding/spacing
- Tables properly contained with scroll
- Professional, unified appearance
- Matches MediaManager page design

## Testing Checklist

After each page update, verify:
- [ ] Page renders at full screen height
- [ ] Header is fixed at top with proper spacing
- [ ] Filters/search in page-header-left
- [ ] Action buttons in page-header-right
- [ ] Batch operations (if any) appear between header and content
- [ ] Statistics cards (if any) inside page-content
- [ ] Table wrapped in table-container with white background
- [ ] Page content scrolls properly when table is long
- [ ] Responsive behavior works on mobile (media queries in CSS)
- [ ] No layout shift or overflow issues

## Completion Status

- [x] Users List
- [ ] Actors List
- [ ] Directors List
- [ ] Series List
- [ ] Comments List
- [ ] Banners List
- [ ] Announcements List
- [ ] Scheduling List
- [ ] Roles List
- [ ] Logs
- [ ] Email Management
- [ ] IP Blacklist
- [ ] AI Management
- [ ] Reports Dashboard

## Next Steps

1. Update each file following the pattern above
2. Test each page after update
3. Check for any console errors or styling issues
4. Verify responsive behavior
5. Commit changes with descriptive message

## Example Commit Message

```
feat: update all admin pages to use full-screen layout

- Migrated all admin pages to use page-layout.css
- Applied consistent page-container structure
- Improved space utilization and UX consistency
- Matches MediaManager page design pattern

Updated pages:
- Users, Actors, Directors, Series
- Comments, Banners, Announcements
- Scheduling, Roles, Logs
- Email, IP Blacklist, AI Management, Reports
```
