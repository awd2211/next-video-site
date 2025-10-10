import { Breadcrumb as AntBreadcrumb } from 'antd'
import { useLocation, Link } from 'react-router-dom'
import { HomeOutlined } from '@ant-design/icons'

// Route name mapping
const routeNameMap: Record<string, string> = {
  '/': '控制台',
  '/videos': '视频管理',
  '/videos/new': '新增视频',
  '/videos/:id/edit': '编辑视频',
  '/users': '用户管理',
  '/comments': '评论管理',
  '/banners': '横幅管理',
  '/announcements': '公告管理',
  '/actors': '演员管理',
  '/directors': '导演管理',
  '/statistics': '数据统计',
  '/settings': '系统设置',
  '/logs': '操作日志',
  '/ip-blacklist': 'IP黑名单',
  '/series': '剧集管理',
  '/series/new': '新增剧集',
  '/series/:id': '剧集详情',
  '/series/:id/edit': '编辑剧集',
}

interface BreadcrumbItem {
  path: string
  title: string
}

const Breadcrumb = () => {
  const location = useLocation()

  const getBreadcrumbItems = (): BreadcrumbItem[] => {
    const pathSnippets = location.pathname.split('/').filter((i) => i)
    
    if (pathSnippets.length === 0) {
      return [{ path: '/', title: '控制台' }]
    }

    const breadcrumbItems: BreadcrumbItem[] = [{ path: '/', title: '控制台' }]

    pathSnippets.forEach((snippet, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`
      let title = routeNameMap[url] || snippet

      // Handle dynamic routes
      if (!routeNameMap[url]) {
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

