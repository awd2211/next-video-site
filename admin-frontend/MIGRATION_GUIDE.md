# Migration Guide for Admin Frontend Optimizations

## Quick Start

### 1. Install Dependencies (if needed)
The project already has all necessary dependencies. If you need to reinstall:
```bash
pnpm install
```

### 2. Run Linting and Formatting
```bash
# Check for linting errors
pnpm run lint

# Auto-fix linting errors
pnpm run lint:fix

# Format all code
pnpm run format

# Check if code is formatted
pnpm run format:check

# Type check
pnpm run type-check
```

### 3. Start Development Server
```bash
pnpm run dev
```

## Breaking Changes & Updates

### 1. Import Paths
All absolute imports now use the `@/` prefix:

```typescript
// ❌ Old way
import axios from '../../../utils/axios'

// ✅ New way
import axios from '@/utils/axios'
```

### 2. API Endpoints
Use centralized API endpoints instead of hardcoded strings:

```typescript
// ❌ Old way
await axios.get('/api/v1/admin/videos')
await axios.get(`/api/v1/admin/videos/${id}`)

// ✅ New way
import API_ENDPOINTS from '@/config/api'

await axios.get(API_ENDPOINTS.admin.videos.list)
await axios.get(API_ENDPOINTS.admin.videos.detail(id))
```

### 3. Type Definitions
Use proper TypeScript types:

```typescript
// ❌ Old way
const [data, setData] = useState<any>()
const handleClick = (record: any) => { ... }

// ✅ New way
import { Video } from '@/types/models'
import { PaginatedResponse } from '@/types/common'

const [data, setData] = useState<PaginatedResponse<Video>>()
const handleClick = (record: Video) => { ... }
```

### 4. Status Values
Use enums for status values:

```typescript
// ❌ Old way
if (video.status === 'published') { ... }
<Tag color={status === 'published' ? 'green' : 'orange'}>{status}</Tag>

// ✅ New way
import { VideoStatus, VIDEO_STATUS_CONFIG } from '@/types/enums'

if (video.status === VideoStatus.PUBLISHED) { ... }

const config = VIDEO_STATUS_CONFIG[video.status]
<Tag color={config.color}>{config.text}</Tag>
```

### 5. Search Inputs with Debounce
Add debouncing to all search inputs:

```typescript
// ❌ Old way
const [search, setSearch] = useState('')

useQuery({
  queryKey: ['data', search],
  queryFn: () => fetchData(search)
})

<Input.Search onSearch={setSearch} />

// ✅ New way
import { useDebounce } from '@/hooks/useDebounce'

const [search, setSearch] = useState('')
const debouncedSearch = useDebounce(search, 500)

useQuery({
  queryKey: ['data', debouncedSearch],
  queryFn: () => fetchData(debouncedSearch)
})

<Input.Search 
  value={search}
  onChange={(e) => setSearch(e.target.value)}
  onSearch={setSearch}
  allowClear
/>
```

### 6. Pagination
Use the pagination hook for consistency:

```typescript
// ❌ Old way
const [page, setPage] = useState(1)
const [pageSize, setPageSize] = useState(20)

<Table 
  pagination={{
    current: page,
    pageSize: pageSize,
    onChange: (p, ps) => {
      setPage(p)
      setPageSize(ps)
    }
  }}
/>

// ✅ New way
import { usePagination } from '@/hooks/usePagination'

const { page, pageSize, paginationConfig } = usePagination({
  initialPage: 1,
  initialPageSize: 20
})

<Table pagination={{ ...paginationConfig, total: data?.total }} />
```

## Common Patterns

### Error Handling
All errors are now caught by the Error Boundary. For custom error handling:

```typescript
import { message } from 'antd'

try {
  await apiCall()
} catch (error: any) {
  message.error(error.response?.data?.detail || 'Operation failed')
}
```

### Loading States
With lazy loading, use Suspense fallbacks:

```typescript
import { Suspense } from 'react'
import { Spin } from 'antd'

const LoadingFallback = () => (
  <div style={{ textAlign: 'center', padding: '100px 0' }}>
    <Spin size="large" tip="Loading..." />
  </div>
)

<Suspense fallback={<LoadingFallback />}>
  <YourComponent />
</Suspense>
```

### React Query Configuration
The QueryClient is now pre-configured with:
- `staleTime: 5 minutes`
- `gcTime: 10 minutes`
- `retry: 1`
- `refetchOnWindowFocus: false`

Override per query if needed:

```typescript
useQuery({
  queryKey: ['key'],
  queryFn: fetchFn,
  staleTime: 10 * 60 * 1000, // 10 minutes
  refetchOnWindowFocus: true
})
```

## Updated Component Patterns

### Video List Component
```typescript
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useDebounce } from '@/hooks/useDebounce'
import { usePagination } from '@/hooks/usePagination'
import API_ENDPOINTS from '@/config/api'
import { Video } from '@/types/models'
import { PaginatedResponse } from '@/types/common'
import { VideoStatus, VIDEO_STATUS_CONFIG } from '@/types/enums'

const VideoList = () => {
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 500)
  const { page, pageSize, paginationConfig } = usePagination()

  const { data, isLoading } = useQuery<PaginatedResponse<Video>>({
    queryKey: ['videos', page, pageSize, debouncedSearch],
    queryFn: async () => {
      const response = await axios.get(API_ENDPOINTS.admin.videos.list, {
        params: { page, page_size: pageSize, search: debouncedSearch }
      })
      return response.data
    }
  })

  // ... rest of component
}
```

### Status Display
```typescript
import { Tag } from 'antd'
import { VideoStatus, VIDEO_STATUS_CONFIG } from '@/types/enums'

const StatusTag = ({ status }: { status: VideoStatus }) => {
  const config = VIDEO_STATUS_CONFIG[status]
  return <Tag color={config.color}>{config.text}</Tag>
}
```

## TypeScript Best Practices

### 1. Avoid `any` Type
```typescript
// ❌ Bad
const handleClick = (data: any) => { ... }

// ✅ Good
import { Video } from '@/types/models'
const handleClick = (data: Video) => { ... }
```

### 2. Use Proper Event Types
```typescript
// ❌ Bad
const handleChange = (e: any) => { ... }

// ✅ Good
import { ChangeEvent } from 'react'
const handleChange = (e: ChangeEvent<HTMLInputElement>) => { ... }
```

### 3. Define Component Props
```typescript
// ❌ Bad
const MyComponent = ({ title, count }: any) => { ... }

// ✅ Good
interface MyComponentProps {
  title: string
  count: number
  onAction?: () => void
}

const MyComponent = ({ title, count, onAction }: MyComponentProps) => { ... }
```

## Testing Your Changes

### 1. Run Type Checking
```bash
pnpm run type-check
```

### 2. Run Linting
```bash
pnpm run lint
```

### 3. Check Formatting
```bash
pnpm run format:check
```

### 4. Build for Production
```bash
pnpm run build
```

## Troubleshooting

### ESLint Errors
If you see ESLint errors after migration:
```bash
# Auto-fix most issues
pnpm run lint:fix
```

### TypeScript Errors
Common fixes:
1. Add proper type imports from `@/types`
2. Replace `any` with specific types
3. Add null checks where needed

### Import Errors
If imports don't resolve:
1. Check that paths use `@/` prefix
2. Verify `tsconfig.json` has correct `paths` config
3. Restart your IDE/editor

## Checklist for New Features

When adding new features:

- [ ] Use centralized API endpoints from `@/config/api`
- [ ] Define types in `@/types/` if needed
- [ ] Add debounce to search inputs
- [ ] Use proper TypeScript types (no `any`)
- [ ] Lazy load new pages
- [ ] Add error handling
- [ ] Use consistent status enums
- [ ] Run `pnpm run lint:fix` before committing
- [ ] Run `pnpm run type-check` to verify types

## Additional Resources

- [ESLint Rules](./.eslintrc.cjs)
- [Prettier Config](./.prettierrc)
- [TypeScript Config](./tsconfig.json)
- [API Endpoints](./src/config/api.ts)
- [Type Definitions](./src/types/)
- [Reusable Hooks](./src/hooks/)

## Getting Help

If you encounter issues:
1. Check the [Optimization Summary](./OPTIMIZATION_SUMMARY.md)
2. Review this migration guide
3. Check TypeScript errors with `pnpm run type-check`
4. Run linter with `pnpm run lint`

