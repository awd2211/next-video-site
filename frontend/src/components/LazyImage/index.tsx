import { useState, useEffect, useRef } from 'react'

interface LazyImageProps {
  src: string
  alt: string
  className?: string
  placeholder?: string
  enableWebP?: boolean
}

/**
 * Check if browser supports WebP
 */
const supportsWebP = (() => {
  if (typeof window === 'undefined') return false
  
  const elem = document.createElement('canvas')
  if (elem.getContext && elem.getContext('2d')) {
    return elem.toDataURL('image/webp').indexOf('data:image/webp') === 0
  }
  return false
})()

/**
 * Get WebP URL if supported and available
 */
const getOptimizedSrc = (src: string, enableWebP: boolean): string => {
  if (!enableWebP || !supportsWebP) return src
  
  // Try to serve WebP version
  // Assumes backend serves .webp alongside original images
  const ext = src.split('.').pop()
  if (ext && ['jpg', 'jpeg', 'png'].includes(ext.toLowerCase())) {
    return src.replace(new RegExp(`\\.${ext}$`, 'i'), '.webp')
  }
  
  return src
}

const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className = '',
  placeholder = '/placeholder.jpg',
  enableWebP = true,
}) => {
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let observer: IntersectionObserver | null = null

    if (containerRef.current) {
      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              loadImage()
              if (observer && containerRef.current) {
                observer.unobserve(containerRef.current)
              }
            }
          })
        },
        {
          rootMargin: '100px', // 提前100px开始加载
          threshold: 0.01,
        }
      )

      observer.observe(containerRef.current)
    }

    const loadImage = () => {
      const optimizedSrc = getOptimizedSrc(src, enableWebP)
      
      const image = new Image()
      
      image.onload = () => {
        setImageSrc(optimizedSrc)
        setIsLoading(false)
        setHasError(false)
      }
      
      image.onerror = () => {
        // If WebP fails, fallback to original
        if (optimizedSrc !== src && enableWebP) {
          const fallbackImage = new Image()
          fallbackImage.onload = () => {
            setImageSrc(src)
            setIsLoading(false)
            setHasError(false)
          }
          fallbackImage.onerror = () => {
            setImageSrc(placeholder)
            setIsLoading(false)
            setHasError(true)
          }
          fallbackImage.src = src
        } else {
          setImageSrc(placeholder)
          setIsLoading(false)
          setHasError(true)
        }
      }
      
      image.src = optimizedSrc
    }

    return () => {
      if (observer && containerRef.current) {
        observer.unobserve(containerRef.current)
      }
    }
  }, [src, placeholder, enableWebP])

  return (
    <div ref={containerRef} className="relative overflow-hidden">
      {/* Loading placeholder */}
      {isLoading && (
        <div className="absolute inset-0 bg-gray-700 animate-pulse" />
      )}
      
      {/* Actual image */}
      <img
        ref={imgRef}
        src={imageSrc}
        alt={alt}
        className={`${className} ${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
        loading="lazy"
        decoding="async"
      />
      
      {/* Error state */}
      {hasError && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
          <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      )}
    </div>
  )
}

export default LazyImage
