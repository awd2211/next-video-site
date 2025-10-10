/**
 * PWA Install Prompt Component
 * Shows prompt to install app when available
 */
import { useState, useEffect } from 'react'
import { X, Download } from 'lucide-react'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export const PWAInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e as BeforeInstallPromptEvent)
      
      // Check if user previously dismissed
      const dismissed = localStorage.getItem('pwa-install-dismissed')
      if (!dismissed) {
        setShowPrompt(true)
      }
    }

    window.addEventListener('beforeinstallprompt', handler)

    return () => {
      window.removeEventListener('beforeinstallprompt', handler)
    }
  }, [])

  const handleInstall = async () => {
    if (!deferredPrompt) return

    // Show install prompt
    await deferredPrompt.prompt()

    // Wait for user choice
    const { outcome } = await deferredPrompt.userChoice

    console.log(`PWA install outcome: ${outcome}`)

    // Clean up
    setDeferredPrompt(null)
    setShowPrompt(false)
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    // Remember dismissal for 7 days
    localStorage.setItem('pwa-install-dismissed', Date.now().toString())
    setTimeout(() => {
      localStorage.removeItem('pwa-install-dismissed')
    }, 7 * 24 * 60 * 60 * 1000)
  }

  if (!showPrompt) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm">
      <div className="bg-gray-800 border border-gray-700 rounded-lg shadow-2xl p-6 animate-slideIn">
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 text-gray-400 hover:text-white transition-colors"
          aria-label="关闭"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-start gap-4">
          <div className="bg-red-600 p-3 rounded-lg flex-shrink-0">
            <Download className="w-6 h-6" />
          </div>

          <div className="flex-1">
            <h3 className="font-bold text-lg mb-2">安装 VideoSite</h3>
            <p className="text-sm text-gray-300 mb-4">
              安装到桌面，享受更快的启动速度和离线访问功能
            </p>

            <div className="flex gap-2">
              <button
                onClick={handleInstall}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                立即安装
              </button>
              <button
                onClick={handleDismiss}
                className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                稍后
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PWAInstallPrompt

