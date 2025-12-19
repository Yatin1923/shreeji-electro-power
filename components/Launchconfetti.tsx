"use client"

import { useEffect } from "react"
import confetti from "canvas-confetti"

export function LaunchConfetti() {
  useEffect(() => {
    const todayStr = new Date().toISOString().slice(0, 10)
    const launchStr = "2025-12-19" 

    if (todayStr !== launchStr) return

    const duration = 2 * 1000
    const end = Date.now() + duration

    const frame = () => {
      // Left side
      confetti({
        particleCount: 4,
        angle: 60,
        spread: 70,
        startVelocity: 55,
        origin: { x: 0, y: 1 },
      })

      // Right side
      confetti({
        particleCount: 4,
        angle: 120,
        spread: 70,
        startVelocity: 55,
        origin: { x: 1, y: 1 },
      })

      if (Date.now() < end) {
        requestAnimationFrame(frame)
      }
    }

    frame()
  }, [])

  return null
}
