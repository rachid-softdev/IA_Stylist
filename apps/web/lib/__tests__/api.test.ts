/**
 * Tests for the ApiClient (lib/api.ts)
 *
 * These tests verify:
 * 1. CSRF token handling: X-CSRF-Token header for mutating methods
 * 2. Error handling: ApiClientError is thrown for non-ok responses
 * 3. Safe methods skip CSRF: GET requests don't include the header
 *
 * Uses vitest with jsdom environment to simulate browser APIs.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// ─── Mocks ──────────────────────────────────────────────────────────────

/**
 * We mock fetch before importing the module under test.
 * Each test can configure mockFetch to simulate different responses.
 */
const mockFetch = vi.fn()

// Store the original document.cookie descriptor so we can restore it
const originalCookieDescriptor = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie')

beforeEach(() => {
  // Make document.cookie writable for tests
  Object.defineProperty(document, 'cookie', {
    writable: true,
    value: 'csrf_token=abc123def456.rawsignedpart; other=cookie',
    configurable: true,
  })
})

afterEach(() => {
  vi.clearAllMocks()
  // Restore original cookie descriptor
  if (originalCookieDescriptor) {
    Object.defineProperty(document, 'cookie', originalCookieDescriptor)
  }
})

// ─── Tests ──────────────────────────────────────────────────────────────

describe('ApiClient - CSRF Token Handling', () => {
  beforeEach(() => {
    // Mock fetch before each test
    global.fetch = mockFetch
  })

  afterEach(() => {
    // Clean up
    delete (global as any).fetch
  })

  it('should include X-CSRF-Token header for POST requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: { success: true },
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    const { api } = await import('@/lib/api')
    await api.post('/test', { foo: 'bar' })

    expect(mockFetch).toHaveBeenCalledTimes(1)
    const callHeaders = mockFetch.mock.calls[0][1].headers
    expect(callHeaders['X-CSRF-Token']).toBe('abc123def456')
  })

  it('should include X-CSRF-Token header for PUT requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: { success: true },
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    const { api } = await import('@/lib/api')
    await api.put('/test', { foo: 'bar' })

    const callHeaders = mockFetch.mock.calls[0][1].headers
    expect(callHeaders['X-CSRF-Token']).toBe('abc123def456')
  })

  it('should include X-CSRF-Token header for DELETE requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: null,
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    const { api } = await import('@/lib/api')
    await api.delete('/test')

    const callHeaders = mockFetch.mock.calls[0][1].headers
    expect(callHeaders['X-CSRF-Token']).toBe('abc123def456')
  })

  it('should NOT include X-CSRF-Token header for GET requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: [],
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    const { api } = await import('@/lib/api')
    await api.get('/test')

    const callHeaders = mockFetch.mock.calls[0][1].headers
    expect(callHeaders['X-CSRF-Token']).toBeUndefined()
  })

  it('should handle missing csrf_token cookie gracefully', async () => {
    // Set document.cookie to something without csrf_token
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'other=cookie',
      configurable: true,
    })

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: { success: true },
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    const { api } = await import('@/lib/api')
    await api.post('/test', { foo: 'bar' })

    const callHeaders = mockFetch.mock.calls[0][1].headers
    // Should not have X-CSRF-Token when cookie is missing
    expect(callHeaders['X-CSRF-Token']).toBeUndefined()
  })

  it('should handle empty csrf_token cookie value gracefully', async () => {
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'csrf_token=; other=cookie',
      configurable: true,
    })

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: { success: true },
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    const { api } = await import('@/lib/api')
    await api.post('/test')

    const callHeaders = mockFetch.mock.calls[0][1].headers
    expect(callHeaders['X-CSRF-Token']).toBeUndefined()
  })
})

describe('ApiClientError', () => {
  it('should throw ApiClientError on non-ok response with error details', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 429,
      json: () => Promise.resolve({
        data: null,
        error: { code: 'RATE_LIMITED', message: 'Too fast', details: { retry_after: 60 } },
      }),
    })

    global.fetch = mockFetch
    const { api, ApiClientError } = await import('@/lib/api')

    try {
      await api.get('/test')
      expect('should throw').toBe('but did not')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError)
      expect((err as ApiClientError).code).toBe('RATE_LIMITED')
      expect((err as ApiClientError).message).toBe('Too fast')
      expect((err as ApiClientError).status).toBe(429)
      expect((err as ApiClientError).details).toEqual({ retry_after: 60 })
    }
  })

  it('should throw ApiClientError with UNKNOWN code when no error body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.reject(new Error('Invalid JSON')),
    })

    global.fetch = mockFetch
    const { api, ApiClientError } = await import('@/lib/api')

    try {
      await api.get('/test')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError)
      expect((err as ApiClientError).code).toBe('UNKNOWN')
      expect((err as ApiClientError).message).toBe('Request failed')
      expect((err as ApiClientError).status).toBe(500)
    }
  })

  it('should preserve error name in ApiClientError', async () => {
    const { ApiClientError } = await import('@/lib/api')
    const err = new ApiClientError('TEST_CODE', 'Test message', 400)
    expect(err.name).toBe('ApiClientError')
    expect(err.code).toBe('TEST_CODE')
    expect(err.message).toBe('Test message')
    expect(err.status).toBe(400)
  })
})

describe('ApiClient - Request Configuration', () => {
  it('should include credentials: include in all requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: [],
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    global.fetch = mockFetch
    const { api } = await import('@/lib/api')
    await api.get('/test')

    expect(mockFetch.mock.calls[0][1].credentials).toBe('include')
  })

  it('should set Content-Type header for requests with body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        data: { success: true },
        meta: { request_id: 'r1', timestamp: '2024-01-01T00:00:00Z' },
        error: null,
      }),
    })

    global.fetch = mockFetch
    const { api } = await import('@/lib/api')
    await api.post('/test', { key: 'value' })

    const callHeaders = mockFetch.mock.calls[0][1].headers
    expect(callHeaders['Content-Type']).toBe('application/json')
  })
})
