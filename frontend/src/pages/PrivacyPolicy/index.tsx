import { Shield, Lock, Eye, Database, UserCheck, FileText } from 'lucide-react'

const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-600/20 rounded-full mb-4">
            <Shield className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-4xl font-bold mb-4">隐私政策</h1>
          <p className="text-gray-400">
            最后更新日期: 2024年1月1日
          </p>
        </div>

        {/* Introduction */}
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <p className="text-gray-300 leading-relaxed">
            VideoSite（以下简称"我们"）非常重视用户的隐私保护。本隐私政策旨在帮助您了解我们如何收集、使用、存储和保护您的个人信息。
            使用我们的服务即表示您同意本隐私政策的内容。
          </p>
        </div>

        {/* Content Sections */}
        <div className="space-y-8">
          {/* Section 1 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Database className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">1. 我们收集的信息</h2>
            </div>
            <div className="text-gray-300 space-y-4">
              <div>
                <h3 className="font-semibold text-white mb-2">1.1 您提供的信息</h3>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>注册信息：用户名、邮箱地址、密码</li>
                  <li>个人资料：头像、昵称、个人简介等</li>
                  <li>支付信息：支付方式、交易记录（由第三方支付平台处理）</li>
                  <li>用户内容：评论、评分、收藏等</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-white mb-2">1.2 自动收集的信息</h3>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>设备信息：浏览器类型、操作系统、设备型号</li>
                  <li>日志信息：IP地址、访问时间、页面浏览记录</li>
                  <li>使用数据：观看历史、搜索记录、偏好设置</li>
                  <li>Cookie和类似技术收集的信息</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Section 2 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Eye className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">2. 信息的使用方式</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>我们收集的信息将用于以下目的：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>提供、维护和改进我们的服务</li>
                <li>个性化推荐内容和广告</li>
                <li>处理您的订阅和付款</li>
                <li>发送服务通知、更新和促销信息</li>
                <li>回应您的咨询和客户服务请求</li>
                <li>防止欺诈和滥用行为</li>
                <li>进行数据分析以改善用户体验</li>
                <li>遵守法律法规要求</li>
              </ul>
            </div>
          </div>

          {/* Section 3 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <UserCheck className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">3. 信息共享</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>我们不会出售您的个人信息。我们可能在以下情况下共享您的信息：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>服务提供商：</strong>与帮助我们运营服务的第三方合作（如支付处理、数据分析）</li>
                <li><strong>业务转让：</strong>在合并、收购或资产出售的情况下</li>
                <li><strong>法律要求：</strong>遵守法律义务、法院命令或政府要求</li>
                <li><strong>您的同意：</strong>在其他情况下征得您的明确同意</li>
              </ul>
            </div>
          </div>

          {/* Section 4 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Lock className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">4. 信息安全</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>我们采取合理的安全措施保护您的个人信息：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>使用加密技术（SSL/TLS）保护数据传输</li>
                <li>对敏感数据进行加密存储</li>
                <li>限制员工访问个人信息的权限</li>
                <li>定期进行安全审计和漏洞检测</li>
                <li>制定应急响应计划</li>
              </ul>
              <p className="mt-4">
                但请注意，互联网传输不是100%安全的。我们无法保证信息的绝对安全，请您妥善保管账号密码。
              </p>
            </div>
          </div>

          {/* Section 5 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">5. 您的权利</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>您对自己的个人信息拥有以下权利：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>访问权：</strong>查看我们持有的关于您的个人信息</li>
                <li><strong>更正权：</strong>要求更正不准确或不完整的信息</li>
                <li><strong>删除权：</strong>要求删除您的个人信息</li>
                <li><strong>限制权：</strong>限制我们处理您个人信息的方式</li>
                <li><strong>反对权：</strong>反对我们处理您的个人信息</li>
                <li><strong>数据携带权：</strong>以结构化、常用的格式接收您的数据</li>
              </ul>
              <p className="mt-4">
                如需行使这些权利，请通过 <a href="/contact" className="text-red-600 hover:text-red-500">联系我们</a> 页面与我们联系。
              </p>
            </div>
          </div>

          {/* Section 6 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Database className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">6. Cookie 和跟踪技术</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>我们使用Cookie和类似技术来：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>记住您的登录状态和偏好设置</li>
                <li>分析网站流量和用户行为</li>
                <li>提供个性化内容和广告</li>
                <li>防止欺诈和提高安全性</li>
              </ul>
              <p className="mt-4">
                您可以通过浏览器设置管理Cookie。但禁用Cookie可能影响某些功能的正常使用。
              </p>
            </div>
          </div>

          {/* Section 7 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">7. 儿童隐私</h2>
            </div>
            <div className="text-gray-300">
              <p>
                我们的服务面向13岁及以上的用户。我们不会故意收集13岁以下儿童的个人信息。
                如果您发现我们收集了儿童的个人信息，请立即联系我们，我们会尽快删除相关信息。
              </p>
            </div>
          </div>

          {/* Section 8 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">8. 隐私政策的变更</h2>
            </div>
            <div className="text-gray-300">
              <p>
                我们可能会不时更新本隐私政策。重大变更会在网站上发布通知，或通过电子邮件通知您。
                继续使用我们的服务即表示您接受更新后的隐私政策。建议您定期查看本页面以了解最新信息。
              </p>
            </div>
          </div>

          {/* Section 9 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <UserCheck className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">9. 联系我们</h2>
            </div>
            <div className="text-gray-300 space-y-2">
              <p>如对本隐私政策有任何疑问或建议，请通过以下方式联系我们：</p>
              <ul className="space-y-1 ml-4">
                <li>电子邮箱: privacy@videosite.com</li>
                <li>客服热线: 400-888-8888</li>
                <li>在线咨询: <a href="/contact" className="text-red-600 hover:text-red-500">联系我们</a></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Back to home */}
        <div className="mt-12 text-center">
          <a
            href="/"
            className="inline-block bg-red-600 hover:bg-red-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
          >
            返回首页
          </a>
        </div>
      </div>
    </div>
  )
}

export default PrivacyPolicy
