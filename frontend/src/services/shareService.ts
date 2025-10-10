/**
 * 分享服务
 */
import api from './api'

export type SharePlatform =
  | 'wechat'
  | 'weibo'
  | 'qq'
  | 'qzone'
  | 'twitter'
  | 'facebook'
  | 'link'
  | 'other'

export interface ShareCreate {
  video_id: number
  platform: SharePlatform
}

export interface ShareStats {
  total_shares: number
  platform_stats: Record<string, number>
  recent_shares: number
}

export const shareService = {
  /**
   * 记录分享行为
   */
  recordShare: async (data: ShareCreate): Promise<void> => {
    await api.post('/shares/', data)
  },

  /**
   * 获取视频分享统计
   */
  getVideoStats: async (videoId: number): Promise<ShareStats> => {
    const response = await api.get(`/shares/video/${videoId}/stats`)
    return response.data
  },

  /**
   * 生成分享链接
   */
  generateShareUrl: (videoId: number, platform?: SharePlatform): string => {
    const baseUrl = window.location.origin
    const videoUrl = `${baseUrl}/videos/${videoId}`

    // 根据平台生成不同的分享链接
    switch (platform) {
      case 'weibo':
        return `https://service.weibo.com/share/share.php?url=${encodeURIComponent(videoUrl)}&title=${encodeURIComponent(document.title)}`

      case 'qq':
        return `https://connect.qq.com/widget/shareqq/index.html?url=${encodeURIComponent(videoUrl)}&title=${encodeURIComponent(document.title)}`

      case 'qzone':
        return `https://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=${encodeURIComponent(videoUrl)}&title=${encodeURIComponent(document.title)}`

      case 'twitter':
        return `https://twitter.com/intent/tweet?url=${encodeURIComponent(videoUrl)}&text=${encodeURIComponent(document.title)}`

      case 'facebook':
        return `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(videoUrl)}`

      default:
        return videoUrl
    }
  },

  /**
   * 复制链接到剪贴板
   */
  copyToClipboard: async (text: string): Promise<boolean> => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text)
        return true
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = text
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        try {
          document.execCommand('copy')
          document.body.removeChild(textArea)
          return true
        } catch (err) {
          document.body.removeChild(textArea)
          return false
        }
      }
    } catch (err) {
      console.error('Failed to copy:', err)
      return false
    }
  },

  /**
   * 生成微信分享二维码URL
   */
  getQRCodeUrl: (videoId: number): string => {
    const baseUrl = window.location.origin
    const videoUrl = `${baseUrl}/videos/${videoId}`
    // 使用第三方二维码生成服务或自建服务
    return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(videoUrl)}`
  },
}
