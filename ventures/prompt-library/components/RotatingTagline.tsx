'use client'

import { useEffect, useRef, useState } from 'react'

interface RotatingTaglineProps {
  taglines: string[]
  intervalMs?: number
  className?: string
}

export default function RotatingTagline({
  taglines,
  intervalMs = 10000,
  className = '',
}: RotatingTaglineProps) {
  const [index, setIndex] = useState(0)
  const [visible, setVisible] = useState(true)
  const timeoutRef = useRef<number | null>(null)

  useEffect(() => {
    if (taglines.length <= 1) return

    const fadeMs = 350
    const intervalId = window.setInterval(() => {
      setVisible(false)

      timeoutRef.current = window.setTimeout(() => {
        setIndex((current) => (current + 1) % taglines.length)
        setVisible(true)
      }, fadeMs)
    }, intervalMs)

    return () => {
      window.clearInterval(intervalId)
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current)
      }
    }
  }, [intervalMs, taglines.length])

  return (
    <p aria-live="polite" className={className}>
      <span
        className={`inline-block transition-opacity duration-500 ${visible ? 'opacity-100' : 'opacity-0'}`}
      >
        {taglines[index] ?? taglines[0] ?? ''}
      </span>
    </p>
  )
}
