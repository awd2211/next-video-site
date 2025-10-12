import { Breadcrumb as AntBreadcrumb } from 'antd'
import { useLocation, Link } from 'react-router-dom'
import { HomeOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'

// Route key mapping (now uses i18n keys)
const routeKeyMap: Record<string, string> = {
  '/': 'breadcrumb.home',
  '/videos': 'breadcrumb.videos',
  '/videos/new': 'breadcrumb.videosNew',
  '/videos/:id/edit': 'breadcrumb.videosEdit',
  '/users': 'breadcrumb.users',
  '/comments': 'breadcrumb.comments',
  '/banners': 'breadcrumb.banners',
  '/announcements': 'breadcrumb.announcements',
  '/actors': 'breadcrumb.actors',
  '/directors': 'breadcrumb.directors',
  '/statistics': 'breadcrumb.statistics',
  '/settings': 'breadcrumb.settings',
  '/logs': 'breadcrumb.logs',
  '/ip-blacklist': 'breadcrumb.ipBlacklist',
  '/series': 'breadcrumb.series',
  '/series/new': 'breadcrumb.seriesNew',
  '/series/:id': 'breadcrumb.seriesDetail',
  '/series/:id/edit': 'breadcrumb.seriesEdit',
}

interface BreadcrumbItem {
  path: string
  title: string
}

const Breadcrumb = () => {
  const { t } = useTranslation()
  const location = useLocation()

  const getBreadcrumbItems = (): BreadcrumbItem[] => {
    const pathSnippets = location.pathname.split('/').filter((i) => i)
    
    if (pathSnippets.length === 0) {
      return [{ path: '/', title: t('breadcrumb.home') }]
    }

    const breadcrumbItems: BreadcrumbItem[] = [{ path: '/', title: t('breadcrumb.home') }]

    pathSnippets.forEach((snippet, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`
      const i18nKey = routeKeyMap[url]
      let title = i18nKey ? t(i18nKey) : snippet

      // Handle dynamic routes
      if (!i18nKey) {
        // Check if it's an ID (numeric)
        if (!isNaN(Number(snippet))) {
          // Don't add numeric IDs to breadcrumb
          return
        }
        // Capitalize first letter for unknown routes
        title = snippet.charAt(0).toUpperCase() + snippet.slice(1)
      }

      breadcrumbItems.push({ path: url, title })
    })

    return breadcrumbItems
  }

  const breadcrumbItems = getBreadcrumbItems()

  return (
    <AntBreadcrumb style={{ margin: '16px 0' }}>
      {breadcrumbItems.map((item, index) => {
        const isLast = index === breadcrumbItems.length - 1
        const icon = index === 0 ? <HomeOutlined /> : null

        return (
          <AntBreadcrumb.Item key={item.path}>
            {isLast ? (
              <span>
                {icon} {item.title}
              </span>
            ) : (
              <Link to={item.path}>
                {icon} {item.title}
              </Link>
            )}
          </AntBreadcrumb.Item>
        )
      })}
    </AntBreadcrumb>
  )
}

export default Breadcrumb

