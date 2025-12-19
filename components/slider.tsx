// BackgroundSlider.tsx
"use client"

import { motion, AnimatePresence } from "motion/react"
import { useEffect, useState } from "react"

const images = [
  "Dowell/images/Smart_Crimping_Tools.png",
  "Dowell/images/Smart_Crimping_Tools.png",
  "Dowell/images/Smart_Crimping_Tools.png",

]

export function BackgroundSlider() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % images.length)
    }, 5000) // change every 5 sec

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="absolute inset-0 -z-10 overflow-hidden">
      <AnimatePresence>
        <motion.div
          key={index}
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${images[index]})` }}
          initial={{ opacity: 0, scale: 1.05 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.2, ease: "easeInOut" }}
        />
      </AnimatePresence>

      {/* Overlay for readability */}
      <div className="absolute inset-0 bg-white/70" />
    </div>
  )
}
