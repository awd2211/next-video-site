import { useState } from 'react'
import { ChevronDown, ChevronUp, Search, HelpCircle } from 'lucide-react'
import { useDebounce } from '@/hooks/useDebounce'

interface FAQItem {
  id: string
  question: string
  answer: string
  category: string
}

const FAQ = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const debouncedSearchQuery = useDebounce(searchQuery, 300)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const categories = [
    { id: 'all', name: '全部' },
    { id: 'account', name: '账号相关' },
    { id: 'playback', name: '播放问题' },
    { id: 'features', name: '功能使用' },
    { id: 'billing', name: '付费相关' },
    { id: 'technical', name: '技术问题' }
  ]

  const faqs: FAQItem[] = [
    // 账号相关
    {
      id: '1',
      category: 'account',
      question: '如何注册账号？',
      answer: '点击页面右上角的"注册"按钮，填写邮箱、用户名和密码即可。注册完成后会自动登录，您就可以开始使用所有功能了。'
    },
    {
      id: '2',
      category: 'account',
      question: '忘记密码怎么办？',
      answer: '在登录页面点击"忘记密码"，输入注册邮箱，系统会发送重置密码的链接到您的邮箱。请在24小时内通过链接重置密码。'
    },
    {
      id: '3',
      category: 'account',
      question: '可以更改用户名吗？',
      answer: '登录后进入"个人中心"，在个人资料页面可以修改用户名。每个账号每30天只能修改一次用户名。'
    },
    {
      id: '4',
      category: 'account',
      question: '如何删除我的账号？',
      answer: '如需删除账号，请通过"联系我们"页面联系客服团队。删除账号后，所有数据将被永久删除且无法恢复，请谨慎操作。'
    },

    // 播放问题
    {
      id: '5',
      category: 'playback',
      question: '视频无法播放怎么办？',
      answer: '请尝试以下方法：1) 刷新页面 2) 清除浏览器缓存 3) 更换浏览器（推荐Chrome或Edge）4) 检查网络连接 5) 降低视频清晰度。如问题仍存在，请联系客服。'
    },
    {
      id: '6',
      category: 'playback',
      question: '为什么视频加载很慢？',
      answer: '视频加载速度受网络状况影响。建议：1) 选择较低的视频质量 2) 检查网络连接速度 3) 关闭其他占用带宽的应用 4) 尝试在非高峰时段观看。'
    },
    {
      id: '7',
      category: 'playback',
      question: '如何调整视频画质？',
      answer: '在视频播放器中点击设置图标（齿轮），选择"画质"选项，可以在自动、高清、标清等选项中选择。系统默认为"自动"，会根据您的网络状况自动调整。'
    },
    {
      id: '8',
      category: 'playback',
      question: '字幕显示不正确怎么办？',
      answer: '在播放器中点击字幕图标，可以选择字幕语言或关闭字幕。如果字幕与画面不同步，可以在设置中调整字幕延迟（前进或后退几秒）。'
    },
    {
      id: '9',
      category: 'playback',
      question: '支持哪些设备观看？',
      answer: '我们支持各种设备观看：桌面浏览器（Chrome、Firefox、Safari、Edge）、手机浏览器、平板设备。只要有现代浏览器和网络连接即可观看。'
    },

    // 功能使用
    {
      id: '10',
      category: 'features',
      question: '如何收藏视频？',
      answer: '在视频详情页点击"收藏"按钮即可将视频加入收藏夹。您可以创建多个收藏夹分组来管理不同类型的视频。'
    },
    {
      id: '11',
      category: 'features',
      question: '在哪里查看观看历史？',
      answer: '登录后，点击右上角头像菜单中的"观看历史"。系统会自动记录您观看过的所有视频和播放进度，方便您继续观看。'
    },
    {
      id: '12',
      category: 'features',
      question: '如何搜索视频？',
      answer: '使用页面顶部的搜索框，输入关键词即可搜索。您可以搜索视频标题、演员、导演等。搜索结果支持按相关度、时间等排序。'
    },
    {
      id: '13',
      category: 'features',
      question: '如何评论和打分？',
      answer: '在视频详情页下方有评论区，登录后即可发表评论。点击星星图标可以给视频打分（1-5星）。您的评论和评分会帮助其他用户发现优质内容。'
    },
    {
      id: '14',
      category: 'features',
      question: '如何分享视频给朋友？',
      answer: '在视频详情页点击"分享"按钮，可以生成分享链接或分享到社交平台。您也可以直接复制浏览器地址栏的URL分享。'
    },

    // 付费相关
    {
      id: '15',
      category: 'billing',
      question: '有哪些会员套餐？',
      answer: '我们提供多种会员套餐：月度会员、季度会员、年度会员。会员可享受高清画质、无广告、离线下载等特权。详情请查看会员页面。'
    },
    {
      id: '16',
      category: 'billing',
      question: '支持哪些支付方式？',
      answer: '我们支持多种支付方式：支付宝、微信支付、银行卡、信用卡等。所有支付均通过加密渠道进行，确保您的资金安全。'
    },
    {
      id: '17',
      category: 'billing',
      question: '可以取消订阅吗？',
      answer: '可以。在个人中心的"会员管理"页面可以随时取消订阅。取消后，会员权益会持续到当前订阅周期结束，之后不再自动续费。'
    },
    {
      id: '18',
      category: 'billing',
      question: '如何申请退款？',
      answer: '如需退款，请在订阅后7天内联系客服。我们会根据具体情况处理退款申请。使用过会员特权的订阅可能无法全额退款。'
    },

    // 技术问题
    {
      id: '19',
      category: 'technical',
      question: '推荐的浏览器是什么？',
      answer: '我们推荐使用最新版本的Chrome、Firefox、Safari或Edge浏览器。这些浏览器提供了最佳的视频播放体验和功能支持。'
    },
    {
      id: '20',
      category: 'technical',
      question: '需要安装插件吗？',
      answer: '不需要。我们使用HTML5视频播放器，现代浏览器都原生支持，无需安装任何插件或扩展。'
    },
    {
      id: '21',
      category: 'technical',
      question: '为什么有些视频看不了？',
      answer: '可能原因：1) 该视频在您所在地区不可用 2) 视频正在转码处理中 3) 您的会员等级不足 4) 视频已被下架。具体情况请查看视频页面的提示信息。'
    },
    {
      id: '22',
      category: 'technical',
      question: '网站提示维护中怎么办？',
      answer: '我们会定期进行系统维护以提升服务质量。维护通常在深夜进行，时间不超过2小时。维护完成后即可正常访问。感谢您的耐心等待。'
    },
    {
      id: '23',
      category: 'technical',
      question: '如何反馈bug或建议？',
      answer: '您可以通过"联系我们"页面提交bug报告或功能建议。我们非常重视用户反馈，会认真评估每一条建议。'
    }
  ]

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const filteredFAQs = faqs.filter(faq => {
    const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory
    const matchesSearch = debouncedSearchQuery === '' ||
      faq.question.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(debouncedSearchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-600/20 rounded-full mb-4">
            <HelpCircle className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-4xl font-bold mb-4">常见问题</h1>
          <p className="text-gray-400 text-lg">
            快速找到您想要的答案
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative max-w-2xl mx-auto mb-8">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="搜索问题..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-transparent"
          />
        </div>

        {/* Categories */}
        <div className="flex flex-wrap gap-3 justify-center mb-8">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCategory === category.id
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* FAQ List */}
        <div className="space-y-3">
          {filteredFAQs.length === 0 ? (
            <div className="text-center py-12 bg-gray-800 rounded-lg">
              <p className="text-gray-400 text-lg">未找到相关问题</p>
            </div>
          ) : (
            filteredFAQs.map(faq => (
              <div
                key={faq.id}
                className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-gray-600 transition-colors"
              >
                <button
                  onClick={() => toggleExpand(faq.id)}
                  className="w-full px-6 py-4 flex items-start justify-between text-left hover:bg-gray-750 transition-colors"
                >
                  <span className="font-medium pr-4">{faq.question}</span>
                  {expandedId === faq.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                  )}
                </button>
                {expandedId === faq.id && (
                  <div className="px-6 pb-4 text-gray-300 leading-relaxed border-t border-gray-700 pt-4">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Help CTA */}
        <div className="mt-12 bg-gray-800 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold mb-2">没有找到答案？</h3>
          <p className="text-gray-400 mb-6">
            查看更多帮助文档或直接联系我们的客服团队
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <a
              href="/help"
              className="inline-block bg-gray-700 hover:bg-gray-600 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              浏览帮助中心
            </a>
            <a
              href="/contact"
              className="inline-block bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              联系客服
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FAQ
