'use client'

import { useEffect } from 'react'
import '@/lib/devMode'

export default function DevModeInit() {
  useEffect(() => {
    import('@/lib/devMode')
  }, [])

  return null
}
