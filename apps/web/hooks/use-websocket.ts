'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/v1/ws'

type MessageHandler = (data: Record<string, unknown>) => void

interface UseWebSocketOptions {
  onMessage?: MessageHandler
  onJobUpdate?: (data: Record<string, unknown>) => void
  enabled?: boolean
  brandId?: string | null
}

export function useWebSocket({
  onMessage,
  onJobUpdate,
  enabled = true,
  brandId,
}: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const handlersRef = useRef<{ onMessage?: MessageHandler; onJobUpdate?: MessageHandler }>({
    onMessage,
    onJobUpdate,
  })
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>()
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval>>()
  const mountedRef = useRef(true)

  handlersRef.current = { onMessage, onJobUpdate }

  const getToken = useCallback(() => {
    const match = document.cookie.match(/(?:^| )vfs_access_token=([^;]+)/)
    return match && match[1] ? decodeURIComponent(match[1]) : null
  }, [])

  const connect = useCallback(() => {
    if (!enabled) return
    const token = getToken()
    if (!token) return

    const url = brandId
      ? `${WS_URL}?token=${encodeURIComponent(token)}&brand_id=${encodeURIComponent(brandId)}`
      : `${WS_URL}?token=${encodeURIComponent(token)}`

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        if (!mountedRef.current) {
          ws.close()
          return
        }
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'ping') {
            ws.send(JSON.stringify({ type: 'pong' }))
            return
          }
          if (data.type === 'job_update' && handlersRef.current.onJobUpdate) {
            handlersRef.current.onJobUpdate(data)
          }
          if (handlersRef.current.onMessage) {
            handlersRef.current.onMessage(data)
          }
        } catch {
          // ignore parse errors
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        wsRef.current = null
        if (mountedRef.current) {
          reconnectTimerRef.current = setTimeout(connect, 3000)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    } catch {
      reconnectTimerRef.current = setTimeout(connect, 3000)
    }
  }, [enabled, brandId, getToken])

  useEffect(() => {
    mountedRef.current = true
    connect()
    return () => {
      mountedRef.current = false
      clearTimeout(reconnectTimerRef.current)
      clearInterval(heartbeatTimerRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  return { isConnected }
}
