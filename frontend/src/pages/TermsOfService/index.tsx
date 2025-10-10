import { FileText, CheckCircle, AlertTriangle, Scale, Shield, XCircle } from 'lucide-react'

const TermsOfService = () => {
  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-600/20 rounded-full mb-4">
            <FileText className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-4xl font-bold mb-4">服务条款</h1>
          <p className="text-gray-400">
            最后更新日期: 2024年1月1日
          </p>
        </div>

        {/* Introduction */}
        <div className="bg-gray-800 rounded-lg p-8 mb-8">
          <p className="text-gray-300 leading-relaxed mb-4">
            欢迎使用 VideoSite！这些服务条款（以下简称"条款"）是您与 VideoSite 之间的法律协议，规定了您访问和使用我们平台的条件。
          </p>
          <p className="text-gray-300 leading-relaxed">
            <strong>请仔细阅读这些条款。</strong>使用我们的服务即表示您同意遵守这些条款。如果您不同意这些条款，请不要使用我们的服务。
          </p>
        </div>

        {/* Content Sections */}
        <div className="space-y-8">
          {/* Section 1 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <CheckCircle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">1. 服务说明</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>
                VideoSite 提供在线视频流媒体服务，让您能够观看电影、电视剧、动漫、纪录片等各类视频内容。
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>我们保留随时修改、暂停或终止服务的权利</li>
                <li>服务可用性可能因地区、设备或其他因素而异</li>
                <li>我们会持续更新和改进服务内容</li>
                <li>某些功能可能需要付费订阅</li>
              </ul>
            </div>
          </div>

          {/* Section 2 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">2. 账号注册与使用</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <div>
                <h3 className="font-semibold text-white mb-2">2.1 账号要求</h3>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>您必须年满13岁才能创建账号</li>
                  <li>提供真实、准确、完整的注册信息</li>
                  <li>及时更新您的账号信息</li>
                  <li>一个人只能注册一个账号</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-white mb-2">2.2 账号安全</h3>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>您有责任保护账号密码的安全</li>
                  <li>不得与他人共享账号</li>
                  <li>如发现未经授权使用，请立即通知我们</li>
                  <li>您对账号下的所有活动负责</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Section 3 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Scale className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">3. 订阅与付费</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <div>
                <h3 className="font-semibold text-white mb-2">3.1 会员订阅</h3>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>我们提供多种订阅套餐供您选择</li>
                  <li>订阅会自动续期，除非您取消</li>
                  <li>费用将在每个计费周期开始时收取</li>
                  <li>订阅价格可能会调整，会提前通知</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-white mb-2">3.2 退款政策</h3>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>订阅后7天内可申请全额退款</li>
                  <li>使用过会员特权后可能无法全额退款</li>
                  <li>取消订阅后，会员权益持续到周期结束</li>
                  <li>特殊优惠订阅可能有不同的退款政策</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Section 4 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">4. 用户行为规范</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>使用我们的服务时，您同意不会：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>违反任何法律法规</li>
                <li>侵犯他人的知识产权、隐私权或其他权利</li>
                <li>上传或传播病毒、恶意软件或其他有害代码</li>
                <li>骚扰、威胁、诽谤或辱骂他人</li>
                <li>发布虚假、误导性或欺骗性内容</li>
                <li>试图破解、干扰或损害我们的系统</li>
                <li>使用自动化工具（如机器人、爬虫）访问服务</li>
                <li>下载、复制或分发受版权保护的内容</li>
                <li>出售、转让或分享您的账号</li>
                <li>绕过任何技术保护措施</li>
              </ul>
            </div>
          </div>

          {/* Section 5 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">5. 内容和知识产权</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <div>
                <h3 className="font-semibold text-white mb-2">5.1 我们的内容</h3>
                <p>
                  平台上的所有内容（包括视频、图片、文字、标识等）均受版权、商标和其他知识产权法保护。
                  您仅获得有限的、非排他性的、不可转让的观看权限。
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-white mb-2">5.2 用户生成内容</h3>
                <p>
                  您发布的评论、评分等内容，您授予我们免费、全球性、非排他性的使用许可。
                  您保证拥有发布内容的权利，且内容不侵犯第三方权利。
                </p>
              </div>
            </div>
          </div>

          {/* Section 6 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">6. 免责声明</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>服务按"原样"和"可用"基础提供</li>
                <li>我们不保证服务不间断、无错误或完全安全</li>
                <li>内容的准确性和可用性可能变化</li>
                <li>您使用服务的风险由您自行承担</li>
                <li>我们不对任何直接、间接、偶然或后果性损害负责</li>
              </ul>
            </div>
          </div>

          {/* Section 7 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">7. 账号终止</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>在以下情况下，我们可以暂停或终止您的账号：</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>违反本服务条款</li>
                <li>长期不活跃</li>
                <li>涉嫌欺诈或滥用</li>
                <li>应法律要求</li>
              </ul>
              <p className="mt-3">
                您也可以随时删除您的账号。账号终止后，您无权访问任何会员内容或服务。
              </p>
            </div>
          </div>

          {/* Section 8 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">8. 条款变更</h2>
            </div>
            <div className="text-gray-300">
              <p>
                我们可能会不时更新这些条款。重大变更会在网站上发布通知。
                继续使用服务即表示您接受更新后的条款。如果不同意新条款，请停止使用我们的服务。
              </p>
            </div>
          </div>

          {/* Section 9 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <Scale className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">9. 法律适用和争议解决</h2>
            </div>
            <div className="text-gray-300 space-y-3">
              <p>
                本条款受中华人民共和国法律管辖。任何争议应首先通过友好协商解决。
                如协商不成，应提交至我们公司所在地的人民法院诉讼解决。
              </p>
            </div>
          </div>

          {/* Section 10 */}
          <div className="bg-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-red-600/20 p-2 rounded-lg">
                <CheckCircle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold">10. 联系我们</h2>
            </div>
            <div className="text-gray-300 space-y-2">
              <p>如对本服务条款有任何疑问，请通过以下方式联系我们：</p>
              <ul className="space-y-1 ml-4">
                <li>电子邮箱: legal@videosite.com</li>
                <li>客服热线: 400-888-8888</li>
                <li>在线咨询: <a href="/contact" className="text-red-600 hover:text-red-500">联系我们</a></li>
              </ul>
            </div>
          </div>
        </div>

        {/* Acceptance */}
        <div className="mt-12 bg-gradient-to-br from-red-600 to-red-700 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">接受条款</h3>
          <p className="text-red-100 mb-6">
            使用 VideoSite 服务即表示您已阅读、理解并同意遵守本服务条款
          </p>
          <a
            href="/"
            className="inline-block bg-white text-red-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            返回首页
          </a>
        </div>
      </div>
    </div>
  )
}

export default TermsOfService
