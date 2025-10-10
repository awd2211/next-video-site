import { useState } from 'react'
import { ChevronDown, ChevronUp, Search, Book, MessageCircle, Shield, Video } from 'lucide-react'

interface HelpTopic {
  id: string
  icon: React.ReactNode
  title: string
  description: string
  articles: Array<{
    id: string
    title: string
    content: string
  }>
}

const HelpCenter = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedArticle, setExpandedArticle] = useState<string | null>(null)

  const helpTopics: HelpTopic[] = [
    {
      id: 'getting-started',
      icon: <Book className="w-6 h-6" />,
      title: '新手入门',
      description: '了解如何开始使用 VideoSite',
      articles: [
        {
          id: 'create-account',
          title: '如何创建账号？',
          content: '点击页面右上角的"注册"按钮，填写您的邮箱、用户名和密码即可完成注册。注册成功后，您可以开始浏览和观看视频。'
        },
        {
          id: 'browse-videos',
          title: '如何浏览视频？',
          content: '您可以通过多种方式浏览视频：1) 在首页查看推荐内容 2) 使用顶部搜索栏搜索 3) 点击分类标签查看特定类别的视频 4) 浏览系列剧集合。'
        },
        {
          id: 'video-quality',
          title: '如何调整视频质量？',
          content: '在视频播放器中，点击设置图标（齿轮），选择"画质"选项，可以选择不同的清晰度。建议根据您的网络状况选择合适的画质。'
        }
      ]
    },
    {
      id: 'account',
      icon: <Shield className="w-6 h-6" />,
      title: '账号管理',
      description: '管理您的个人资料和设置',
      articles: [
        {
          id: 'reset-password',
          title: '如何重置密码？',
          content: '在登录页面点击"忘记密码"，输入您注册时使用的邮箱地址，系统会发送重置密码的链接到您的邮箱。'
        },
        {
          id: 'update-profile',
          title: '如何更新个人资料？',
          content: '登录后，点击右上角的头像，选择"个人中心"，在个人资料页面可以修改您的用户名、头像等信息。'
        },
        {
          id: 'delete-account',
          title: '如何删除账号？',
          content: '如需删除账号，请联系客服团队。账号删除后，您的所有数据将被永久删除且无法恢复。'
        }
      ]
    },
    {
      id: 'features',
      icon: <Video className="w-6 h-6" />,
      title: '功能使用',
      description: '了解各种功能的使用方法',
      articles: [
        {
          id: 'favorites',
          title: '如何收藏视频？',
          content: '在视频详情页点击"收藏"按钮，可以将视频添加到收藏夹。您可以创建多个收藏夹分组来管理您喜欢的视频。'
        },
        {
          id: 'history',
          title: '观看历史在哪里？',
          content: '点击右上角头像菜单中的"观看历史"，可以查看您最近观看过的所有视频。系统会自动记录您的播放进度。'
        },
        {
          id: 'comments',
          title: '如何评论视频？',
          content: '在视频详情页下方的评论区，输入您的评论内容并点击"发表评论"。您也可以回复其他用户的评论。'
        },
        {
          id: 'rating',
          title: '如何给视频打分？',
          content: '在视频详情页，点击星星图标即可给视频打分（1-5星）。您的评分会影响视频的整体评分。'
        },
        {
          id: 'share',
          title: '如何分享视频？',
          content: '在视频详情页点击"分享"按钮，可以选择分享到各种社交平台，或复制链接直接分享给朋友。'
        }
      ]
    },
    {
      id: 'troubleshooting',
      icon: <MessageCircle className="w-6 h-6" />,
      title: '问题排查',
      description: '解决常见的技术问题',
      articles: [
        {
          id: 'video-not-playing',
          title: '视频无法播放怎么办？',
          content: '请尝试以下解决方案：1) 刷新页面 2) 清除浏览器缓存 3) 更换浏览器 4) 检查网络连接 5) 尝试降低视频质量。如果问题持续，请联系客服。'
        },
        {
          id: 'slow-loading',
          title: '视频加载很慢？',
          content: '这可能是由于网络速度较慢。建议：1) 选择较低的视频质量 2) 检查您的网络连接 3) 关闭其他占用带宽的应用程序。'
        },
        {
          id: 'subtitle-issues',
          title: '字幕显示有问题？',
          content: '在播放器中点击字幕图标，选择合适的字幕语言。如果字幕不同步，可以在设置中调整字幕延迟。'
        }
      ]
    }
  ]

  const toggleArticle = (articleId: string) => {
    setExpandedArticle(expandedArticle === articleId ? null : articleId)
  }

  const filteredTopics = helpTopics.map(topic => ({
    ...topic,
    articles: topic.articles.filter(article =>
      searchQuery === '' ||
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.content.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(topic => topic.articles.length > 0)

  return (
    <div className="min-h-screen bg-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">帮助中心</h1>
          <p className="text-gray-400 text-lg mb-8">
            我们随时为您提供帮助
          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="搜索帮助文章..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-transparent"
            />
          </div>
        </div>

        {/* Help Topics */}
        <div className="space-y-8">
          {filteredTopics.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">未找到相关帮助文章</p>
            </div>
          ) : (
            filteredTopics.map(topic => (
              <div key={topic.id} className="bg-gray-800 rounded-lg overflow-hidden">
                <div className="p-6 border-b border-gray-700">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="text-red-600">{topic.icon}</div>
                    <h2 className="text-2xl font-bold">{topic.title}</h2>
                  </div>
                  <p className="text-gray-400">{topic.description}</p>
                </div>

                <div className="divide-y divide-gray-700">
                  {topic.articles.map(article => (
                    <div key={article.id}>
                      <button
                        onClick={() => toggleArticle(article.id)}
                        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-750 transition-colors"
                      >
                        <span className="text-left font-medium">{article.title}</span>
                        {expandedArticle === article.id ? (
                          <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        )}
                      </button>
                      {expandedArticle === article.id && (
                        <div className="px-6 pb-4 text-gray-300 leading-relaxed">
                          {article.content}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Contact CTA */}
        <div className="mt-12 text-center bg-gray-800 rounded-lg p-8">
          <h3 className="text-2xl font-bold mb-2">还没找到答案？</h3>
          <p className="text-gray-400 mb-6">我们的客服团队随时为您服务</p>
          <a
            href="/contact"
            className="inline-block bg-red-600 hover:bg-red-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
          >
            联系客服
          </a>
        </div>
      </div>
    </div>
  )
}

export default HelpCenter
