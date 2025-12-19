"use client"
import Image from "next/image"
import { useRef, useState } from "react"

export const MagnifyingImage = ({ src, alt, width, height, className }: {
  src: string;
  alt: string;
  width: number;
  height: number;
  className?: string;
}) => {
  const [showMagnifier, setShowMagnifier] = useState(false)
  const [magnifierPosition, setMagnifierPosition] = useState({ x: 0, y: 0 })
  const [imgPosition, setImgPosition] = useState({ x: 0, y: 0 })
  const imgRef = useRef<HTMLDivElement>(null)

  const handleMouseEnter = () => {
      setShowMagnifier(true)
  }

  const handleMouseLeave = () => {
      setShowMagnifier(false)
  }

  const handleMouseMove = (e: React.MouseEvent) => {
      if (imgRef.current) {
          const rect = imgRef.current.getBoundingClientRect()
          const x = e.clientX - rect.left
          const y = e.clientY - rect.top
          
          setMagnifierPosition({ x: e.clientX, y: e.clientY })
          setImgPosition({ x, y })
      }
  }

  return (
      <div className="relative">
          <div
              ref={imgRef}
              className="relative overflow-hidden cursor-crosshair"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              onMouseMove={handleMouseMove}
          >
              <Image
                  src={src}
                  alt={alt}
                  width={width}
                  height={height}
                  className={className}
                  priority
              />
          </div>

          {/* Magnifier */}
          {showMagnifier && (
              <div
                  className="fixed pointer-events-none z-50 border-2 border-gray-300 rounded-full shadow-lg bg-white"
                  style={{
                      left: `${magnifierPosition.x - 100}px`,
                      top: `${magnifierPosition.y - 100}px`,
                      width: "200px",
                      height: "200px",
                      backgroundImage: `url(${src})`,
                      backgroundSize: `${width * 2}px ${height * 2}px`,
                      backgroundPosition: `-${imgPosition.x * 2 - 100}px -${imgPosition.y * 2 - 100}px`,
                      backgroundRepeat: "no-repeat",
                  }}
              />
          )}
      </div>
  )
}