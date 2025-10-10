import { useState, useEffect, useRef } from 'react'

interface LazyImageProps {
  src: string
  alt: string
  className?: string
  placeholder?: string
}

const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className = '',
  placeholder = '/placeholder.jpg'
}) => {
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [isLoading, setIsLoading] = useState(true)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    let observer: IntersectionObserver

    if (imgRef.current) {
      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement
              const actualSrc = img.getAttribute('data-src')

              if (actualSrc) {
                // 预加载图片
                const image = new Image()
                image.onload = () => {
                  setImageSrc(actualSrc)
                  setIsLoading(false)
                }
                image.onerror = () => {
                  setImageSrc(placeholder)
                  setIsLoading(false)
                }
                image.src = actualSrc
              }

              observer.unobserve(img)
            }
          })
        },
        {
          rootMargin: '50px', // 提前50px开始加载
          threshold: 0.01
        }
      )

      observer.observe(imgRef.current)
    }

    return () => {
      if (observer && imgRef.current) {
        observer.unobserve(imgRef.current)
      }
    }
  }, [src, placeholder])

  return (
    <img
      ref={imgRef}
      src={imageSrc}
      data-src={src}
      alt={alt}
      className={`${className} ${isLoading ? 'blur-sm' : 'blur-0'} transition-all duration-300`}
      loading="lazy"
    />
  )
}

export default LazyImage
