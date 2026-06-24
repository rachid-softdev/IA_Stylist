import type { ApiResponse } from '@vfs/shared-types'

export class ApiClientError extends Error {
  public readonly code: string
  public readonly status: number
  public readonly details?: Record<string, unknown>

  constructor(code: string, message: string, status: number, details?: Record<string, unknown>) {
    super(message)
    this.name = 'ApiClientError'
    this.code = code
    this.status = status
    this.details = details
  }
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${API_URL}/v1`
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    options?: RequestInit,
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${path}`

    // Destructurer options pour séparer headers du reste
    const { headers: optHeaders, ...restOptions } = options ?? {}

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((optHeaders as Record<string, string>) || {}),
    }

    // 🔥 CSRF : Lire le cookie et extraire le token brut (avant le '.')
    if (method !== 'GET') {
      const csrfCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrf_token='))
        ?.split('=')[1]
      if (csrfCookie) {
        const rawToken = csrfCookie.split('.')[0]  // Extraction obligatoire — le cookie contient raw.signed
        if (rawToken) {
          headers['X-CSRF-Token'] = rawToken
        }
      }
    }

    const config: RequestInit = {
      method,
      headers,
      credentials: 'include',
      ...restOptions,
    }

    if (body && method !== 'GET') {
      config.body = JSON.stringify(body)
    }

    const response = await fetch(url, config)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new ApiClientError(
        errorData?.error?.code || 'UNKNOWN',
        errorData?.error?.message || 'Request failed',
        response.status,
        errorData?.error?.details,
      )
    }

    return response.json()
  }

  async get<T>(path: string): Promise<ApiResponse<T>> {
    return this.request<T>('GET', path)
  }

  async post<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>('POST', path, body)
  }

  async put<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', path, body)
  }

  async delete<T>(path: string): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', path)
  }

  async uploadFile(
    file: File,
    folder: string,
    onProgress?: (progress: number) => void,
  ): Promise<{ r2_key: string; public_url: string }> {
    // Get presigned URL
    const presignedRes = await this.post<{
      upload_url: string
      r2_key: string
      public_url: string
    }>('/upload/presigned-url', {
      filename: file.name,
      content_type: file.type,
      folder,
    })

    const { upload_url, r2_key, public_url } = presignedRes.data

    // Upload directly to R2
    await new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          onProgress((e.loaded / e.total) * 100)
        }
      })
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) resolve()
        else reject(new Error('Upload failed'))
      })
      xhr.addEventListener('error', () => reject(new Error('Upload failed')))
      xhr.open('PUT', upload_url)
      xhr.setRequestHeader('Content-Type', file.type)
      xhr.send(file)
    })

    // Confirm upload
    await this.post('/upload/confirm', {
      r2_key,
      size: file.size,
    })

    return { r2_key, public_url }
  }
}

export const api = new ApiClient()
