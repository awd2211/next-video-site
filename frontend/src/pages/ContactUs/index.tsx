import { useState } from 'react'
import { Mail, MessageCircle, Phone, MapPin, Send, CheckCircle } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { sanitizeInput } from '@/utils/security'
import { VALIDATION_LIMITS } from '@/utils/validationConfig'

const ContactUs = () => {
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // 验证输入
    const cleanedName = sanitizeInput(formData.name, VALIDATION_LIMITS.CONTACT_NAME.max)
    const cleanedMessage = sanitizeInput(formData.message, VALIDATION_LIMITS.CONTACT_MESSAGE.max)

    if (!cleanedName) {
      toast.error(t('contact.nameRequired'))
      return
    }

    if (!formData.email) {
      toast.error(t('contact.emailRequired'))
      return
    }

    if (!formData.subject) {
      toast.error(t('contact.subjectRequired'))
      return
    }

    if (!cleanedMessage) {
      toast.error(t('contact.messageRequired'))
      return
    }

    setIsSubmitting(true)

    // 模拟提交（实际项目中应调用API）
    setTimeout(() => {
      setIsSubmitting(false)
      setIsSubmitted(true)
      toast.success(t('contact.sendSuccess'))
      setFormData({ name: '', email: '', subject: '', message: '' })

      // 3秒后重置成功状态
      setTimeout(() => setIsSubmitted(false), 3000)
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">联系我们</h1>
          <p className="text-gray-400 text-lg">
            有任何问题或建议？我们很乐意听取您的意见
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Contact Information */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-6">联系方式</h2>

              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="bg-red-600/20 p-3 rounded-lg">
                    <Mail className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">电子邮箱</h3>
                    <p className="text-gray-400">support@videosite.com</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-red-600/20 p-3 rounded-lg">
                    <Phone className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">客服热线</h3>
                    <p className="text-gray-400">400-888-8888</p>
                    <p className="text-sm text-gray-500">周一至周日 9:00-22:00</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-red-600/20 p-3 rounded-lg">
                    <MessageCircle className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">在线客服</h3>
                    <p className="text-gray-400">实时聊天支持</p>
                    <button className="text-red-600 hover:text-red-500 text-sm mt-1">
                      开始对话 →
                    </button>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-red-600/20 p-3 rounded-lg">
                    <MapPin className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">公司地址</h3>
                    <p className="text-gray-400">
                      北京市朝阳区<br />
                      某某大厦 8 楼
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* FAQ Link */}
            <div className="bg-gradient-to-br from-red-600 to-red-700 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-2">常见问题</h3>
              <p className="text-red-100 mb-4">
                在提交表单前，您可以先查看常见问题解答
              </p>
              <a
                href="/faq"
                className="inline-block bg-white text-red-600 font-semibold px-6 py-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                查看 FAQ
              </a>
            </div>
          </div>

          {/* Contact Form */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-lg p-8">
              <h2 className="text-2xl font-bold mb-6">发送消息</h2>

              {isSubmitted ? (
                <div className="text-center py-12">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-4">
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">消息已发送！</h3>
                  <p className="text-gray-400">
                    我们已收到您的消息，会尽快回复您
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium mb-2">
                        {t('contact.name')} <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        required
                        maxLength={VALIDATION_LIMITS.CONTACT_NAME.max}
                        value={formData.name}
                        onChange={handleChange}
                        className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-transparent"
                        placeholder={t('contact.namePlaceholder')}
                      />
                      <div className="text-xs text-gray-500 mt-1">
                        {formData.name.length}/{VALIDATION_LIMITS.CONTACT_NAME.max}
                      </div>
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-medium mb-2">
                        {t('contact.email')} <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        required
                        value={formData.email}
                        onChange={handleChange}
                        className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-transparent"
                        placeholder={t('contact.emailPlaceholder')}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="subject" className="block text-sm font-medium mb-2">
                      {t('contact.subject')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      id="subject"
                      name="subject"
                      required
                      value={formData.subject}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-transparent"
                    >
                      <option value="">{t('contact.subjectPlaceholder')}</option>
                      <option value="technical">{t('contact.technical')}</option>
                      <option value="account">{t('contact.account')}</option>
                      <option value="billing">{t('contact.billing')}</option>
                      <option value="content">{t('contact.content')}</option>
                      <option value="suggestion">{t('contact.suggestion')}</option>
                      <option value="other">{t('contact.other')}</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-medium mb-2">
                      {t('contact.message')} <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      required
                      maxLength={VALIDATION_LIMITS.CONTACT_MESSAGE.max}
                      value={formData.message}
                      onChange={handleChange}
                      rows={6}
                      className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 focus:border-transparent resize-none"
                      placeholder={t('contact.messagePlaceholder')}
                    />
                    <div className="text-xs text-gray-500 mt-1 text-right">
                      {formData.message.length}/{VALIDATION_LIMITS.CONTACT_MESSAGE.max}
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                        发送中...
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5" />
                        发送消息
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContactUs
