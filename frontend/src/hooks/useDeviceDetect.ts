/**
 * 设备检测Hook
 * 检测移动设备、平板、PC以及具体的操作系统
 */
import { useState, useEffect } from 'react'

export interface DeviceInfo {
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  isIOS: boolean
  isAndroid: boolean
  isTouchDevice: boolean
  screenWidth: number
  screenHeight: number
  orientation: 'portrait' | 'landscape'
}

export const useDeviceDetect = (): DeviceInfo => {
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo>(() => {
    if (typeof window === 'undefined') {
      return {
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        isIOS: false,
        isAndroid: false,
        isTouchDevice: false,
        screenWidth: 1920,
        screenHeight: 1080,
        orientation: 'landscape',
      }
    }

    const ua = navigator.userAgent
    const isTouchDevice =
      'ontouchstart' in window || navigator.maxTouchPoints > 0

    // 检测移动设备
    const isMobileDevice =
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)

    // 检测平板 (更精确的判断)
    const isTabletDevice =
      /(iPad|Android(?!.*Mobile)|Tablet)/i.test(ua) ||
      (isTouchDevice && window.innerWidth >= 768 && window.innerWidth <= 1024)

    // 检测操作系统
    const isIOSDevice = /iPhone|iPad|iPod/i.test(ua)
    const isAndroidDevice = /Android/i.test(ua)

    // 屏幕方向
    const orientation =
      window.innerWidth > window.innerHeight ? 'landscape' : 'portrait'

    return {
      isMobile: isMobileDevice && !isTabletDevice,
      isTablet: isTabletDevice,
      isDesktop: !isMobileDevice && !isTabletDevice,
      isIOS: isIOSDevice,
      isAndroid: isAndroidDevice,
      isTouchDevice,
      screenWidth: window.innerWidth,
      screenHeight: window.innerHeight,
      orientation,
    }
  })

  useEffect(() => {
    const handleResize = () => {
      const orientation =
        window.innerWidth > window.innerHeight ? 'landscape' : 'portrait'

      setDeviceInfo((prev) => ({
        ...prev,
        screenWidth: window.innerWidth,
        screenHeight: window.innerHeight,
        orientation,
      }))
    }

    const handleOrientationChange = () => {
      // 延迟更新，等待浏览器完成方向切换
      setTimeout(() => {
        handleResize()
      }, 100)
    }

    window.addEventListener('resize', handleResize)
    window.addEventListener('orientationchange', handleOrientationChange)

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('orientationchange', handleOrientationChange)
    }
  }, [])

  return deviceInfo
}

/**
 * 检测是否需要移动端播放器
 */
export const useMobilePlayer = (): boolean => {
  const device = useDeviceDetect()
  // 移动设备或小屏幕平板使用移动端播放器
  return device.isMobile || (device.isTablet && device.screenWidth < 900)
}

/**
 * 获取推荐的视频质量
 */
export const useRecommendedQuality = (): string => {
  const device = useDeviceDetect()

  if (device.isMobile) {
    // 移动设备优先使用较低质量节省流量
    return device.orientation === 'landscape' ? '720p' : '480p'
  } else if (device.isTablet) {
    return '720p'
  } else {
    // 桌面设备使用最高质量
    return '1080p'
  }
}
