# VideoSite Frontend - Quick Reference Guide

## Project Overview

**Type:** Full-featured React 18 video streaming application  
**Framework:** React 18 + TypeScript + Vite  
**State Management:** Zustand (client) + TanStack Query v5 (server)  
**Styling:** TailwindCSS  
**Testing:** Vitest + React Testing Library  
**Code Size:** 6,216 lines of TypeScript  
**Overall Rating:** 8.5/10

---

## Architecture Highlights

### Directory Structure
```
frontend/src/
├── components/     (40+ reusable UI components)
├── pages/          (20+ page components)
├── services/       (25+ API services)
├── hooks/          (6+ custom React hooks)
├── contexts/       (ThemeContext for dark/light mode)
├── store/          (Zustand stores: authStore)
├── utils/          (Helper functions: security, validation, etc.)
├── types/          (TypeScript interfaces)
└── i18n/           (6-language internationalization)
```

### Key Technologies
- **React 18.3.1** - UI framework
- **Vite** - Build tool (lightning fast)
- **TypeScript 5.3** - Type safety
- **TanStack Query v5** - Server state management
- **Zustand 4.5** - Client state management
- **Axios** - HTTP client
- **Video.js** - Video player
- **Zod** - Runtime schema validation
- **DOMPurify** - XSS protection

---

## What Works Exceptionally Well

### 1. State Management (9/10)
- Perfect balance of Zustand (auth) + TanStack Query (server data)
- Intelligent caching with 5-min stale time
- Queue system for concurrent token refresh
- No Redux bloat

### 2. Video Player (9/10)
- YouTube-like keyboard shortcuts (k, space, j, l, f)
- Quality selector with HLS support
- Playback rate control (0.25x-2x)
- Theater mode, Mini player, PiP
- Progress tracking with auto-save

### 3. Performance (8/10)
- Code splitting with lazy loading
- Virtual scrolling for huge lists
- Image optimization with WebP fallback
- PWA with offline support
- Web Vitals monitoring built-in

### 4. Security (9/10)
- Input sanitization with DOMPurify
- XSS prevention on all user inputs
- CSRF token support
- Rate limiting for comments
- Password strength validation

### 5. API Integration (9/10)
- Token refresh with queue system
- Zod runtime validation
- Comprehensive error handling
- 25+ typed API services
- Consistent error messages

### 6. Internationalization (9/10)
- 6 languages: English, Simplified Chinese, Traditional Chinese, Japanese, German, French
- Browser language detection
- localStorage persistence
- Complete coverage of UI strings

---

## Areas Needing Improvement

### High Priority
1. **Accessibility (6/10)**
   - Add focus management in modals
   - Live region announcements for notifications
   - ARIA landmarks (navigation, main, complementary)
   - Keyboard navigation for all interactive elements

2. **E2E Testing (5/10)**
   - Currently: 70+ unit tests
   - Need: Cypress/Playwright for critical user flows
   - Payment flow testing

3. **Documentation (6/10)**
   - API documentation
   - Component Storybook
   - Deployment guide

### Medium Priority
1. **Performance Budgets** - Set up CI/CD checks
2. **Error Recovery** - Exponential backoff for retries
3. **Monitoring** - RUM, session replay, custom events

---

## Quick Start Commands

```bash
# Install dependencies
cd frontend && pnpm install

# Development
pnpm run dev          # http://localhost:3000

# Build
pnpm run build

# Tests
pnpm run test         # Run all tests
pnpm run test:watch   # Watch mode
pnpm run test:coverage # Coverage report

# Code Quality
pnpm run lint         # ESLint check
```

---

## Component Inventory

### Layout Components
- `Header` - Navigation with search
- `Footer` - Footer with links
- `Layout` - Main layout wrapper
- `ErrorBoundary` - Global error handling

### Video Components
- `VideoCard` - Reusable video card
- `VideoPlayer` - Main video player (advanced)
- `MobileVideoPlayer` - Mobile variant
- `VideoPreview` - Hover preview
- `HeroCarousel` - Featured videos carousel

### Form Components
- `SearchAutocomplete` - Search with suggestions
- `LanguageSwitcher` - Language selection
- `ThemeToggle` - Dark/light mode

### Feature Components
- `CommentSection` - Comments with rate limiting
- `RatingStars` - Star rating component
- `FavoriteButton` - Add to favorites
- `ShareButton` - Share video
- `AddToListButton` - Add to watchlist

### Optimization Components
- `LazyImage` - Image lazy loading with WebP
- `VirtualVideoGrid` - Virtualized grid
- `Skeleton*` - Loading skeletons

### Utility Components
- `ErrorState` - Error display
- `EmptyState` - Empty display
- `BackToTop` - Scroll to top
- `PWAInstallPrompt` - PWA install

---

## Service Layer (API Integration)

### 25+ API Services
**Core:**
- `videoService` - Video CRUD
- `userService` - User profile
- `commentService` - Comments

**Media:**
- `favoriteService` - Favorites management
- `favoriteFolderService` - Favorite folders
- `historyService` - Watch history
- `ratingService` - Video ratings

**Streaming:**
- `subtitleService` - Subtitle management
- `danmakuService` - Danmaku (comments)
- `downloadService` - Download management

**Discovery:**
- `searchHistoryService` - Search history
- `recommendationService` - Recommendations
- `seriesService` - Series management
- `actorService` - Actor profiles
- `directorService` - Director profiles

**Payment:**
- `paymentService` - Payments
- `subscriptionService` - Subscriptions
- `couponService` - Coupon codes
- `invoiceService` - Invoices

**Social:**
- `shareService` - Social sharing
- `notificationService` - Notifications
- `sharedWatchlistService` - Shared lists

**Others:**
- `dataService` - General data
- `oauthService` - OAuth integration

---

## Type Safety & Validation

### TypeScript Configuration
- **Strict Mode:** Enabled
- **No Unused Variables:** Enforced
- **No Unused Parameters:** Enforced
- **ESM Modules:** Modern JS

### Runtime Validation with Zod
```typescript
// All API responses validated at runtime
const VideoSchema = z.object({
  id: z.number(),
  title: z.string(),
  // ... more fields
})

return VideoSchema.parse(response.data)
```

---

## Authentication & Security

### Token Management
- JWT tokens (access + refresh)
- localStorage persistence
- Automatic refresh on 401
- Queue system for concurrent requests

### Input Security
- HTML sanitization (DOMPurify)
- String sanitization (trim, control chars)
- Search query sanitization
- Filename validation
- URL validation

### Rate Limiting
- Comment posting rate limiting
- Request retry limits (2x)
- Configurable throttling

---

## Performance Optimizations

### Code Splitting
- Lazy loading with React.lazy()
- Suspense fallback UI
- Critical route preloading

### Image Optimization
- Lazy loading with Intersection Observer
- WebP format detection
- 100px preload margin
- Responsive sizing

### Virtual Scrolling
- react-window for large lists
- Renders only visible items
- Infinite loading with threshold

### Caching
- TanStack Query automatic caching
- PWA with Workbox
- 30-day image cache
- 5-minute API cache

### Monitoring
- Web Vitals (CLS, FID, FCP, LCP, TTFB)
- Page load metrics
- API performance tracking
- Memory usage warnings

---

## Supported Browsers

**ES2020+ Target**
- Chrome 85+
- Firefox 79+
- Safari 14+
- Edge 85+

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `src/App.tsx` | Route definitions, lazy loading |
| `src/main.tsx` | App bootstrap, QueryClient, Toaster |
| `src/services/api.ts` | Axios config, token refresh |
| `src/store/authStore.ts` | Authentication state |
| `src/contexts/ThemeContext.tsx` | Dark/light mode |
| `vite.config.ts` | Build config, PWA setup |
| `tsconfig.json` | TypeScript strict mode |
| `src/i18n/config.ts` | i18n setup, language detection |

---

## Common Patterns

### Data Fetching
```typescript
const { data: videos, isLoading, error } = useQuery({
  queryKey: ['videos'],
  queryFn: () => videoService.getVideos(),
  staleTime: 5 * 60 * 1000,
})
```

### Infinite Scrolling
```typescript
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['videos'],
  queryFn: ({ pageParam = 1 }) => videoService.getVideos({ page: pageParam }),
  getNextPageParam: (lastPage) => lastPage.page < lastPage.pages ? lastPage.page + 1 : undefined,
})
```

### Error Handling
```typescript
try {
  await action()
  toast.success('Success!')
} catch (error) {
  const message = handleApiError(error)
  toast.error(message)
}
```

### Translations
```typescript
const { t } = useTranslation()
<h1>{t('nav.home')}</h1>
```

---

## Testing Strategy

### Unit Tests (70+ tests)
- Services: 15+ test files
- Components: 4 test files
- Utils: 3 test files

### Testing Tools
- Vitest (test runner)
- React Testing Library
- Axios mock adapter

### Test Examples
- API error handling
- Service methods
- Component rendering
- User interactions

---

## Production Checklist

- [x] TypeScript strict mode
- [x] Error boundary
- [x] Sentry integration
- [x] Security sanitization
- [x] i18n setup
- [x] PWA support
- [x] Performance monitoring
- [ ] E2E tests (Cypress/Playwright)
- [ ] WCAG 2.1 AA accessibility
- [ ] Performance budgets
- [ ] Load testing
- [ ] Security audit

---

## Related Documentation

- `FRONTEND_ANALYSIS.md` - Comprehensive analysis
- `CLAUDE.md` - Project overview
- `README.md` - General info

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Lighthouse Score | 90+ | Not measured |
| First Contentful Paint | < 2s | Optimized |
| Core Web Vitals | Green | Monitored |
| Bundle Size | < 500KB | Not measured |
| TTI | < 3s | Optimized |

---

## Getting Help

1. Check component examples in `src/components/`
2. Review service patterns in `src/services/`
3. Look at test examples in `__tests__/` folders
4. Check type definitions in `src/types/`
5. Review hooks in `src/hooks/`

---

**Last Updated:** October 20, 2025  
**Framework Version:** React 18.3.1  
**Status:** Production Ready (with recommended improvements)
