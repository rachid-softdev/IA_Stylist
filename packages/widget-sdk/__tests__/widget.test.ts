import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('VFS Widget SDK', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    localStorage.clear()
  })

  it('should detect script tag with data attributes', () => {
    const script = document.createElement('script')
    script.setAttribute('data-api-key', 'vfs_live_test_key')
    script.setAttribute('data-product-id', '123')
    script.setAttribute('data-sku', 'SKU-001')
    document.body.appendChild(script)

    const scripts = document.querySelectorAll('script[data-api-key]')
    expect(scripts.length).toBe(1)

    const el = scripts[0] as HTMLScriptElement
    expect(el.dataset.apiKey).toBe('vfs_live_test_key')
    expect(el.dataset.productId).toBe('123')
    expect(el.dataset.sku).toBe('SKU-001')
  })

  it('should inject button into DOM', () => {
    const script = document.createElement('script')
    script.setAttribute('data-api-key', 'vfs_live_test_key')
    script.setAttribute('data-product-id', '123')
    script.setAttribute('data-sku', 'SKU-001')
    document.body.appendChild(script)

    const target = document.createElement('div')
    target.setAttribute('data-vfs-widget', '')
    document.body.appendChild(target)

    expect(document.querySelector('.vfs-tryon-btn')).toBeNull()
  })

  it('should store session in localStorage', () => {
    const session = { emailHash: 'abc123', profileUrl: 'https://example.com/img.jpg' }
    localStorage.setItem('vfs_widget_session', JSON.stringify(session))

    const raw = localStorage.getItem('vfs_widget_session')
    expect(raw).toBeTruthy()

    const parsed = JSON.parse(raw!)
    expect(parsed.emailHash).toBe('abc123')
    expect(parsed.profileUrl).toBe('https://example.com/img.jpg')
  })

  it('should create modal overlay', () => {
    const overlay = document.createElement('div')
    overlay.className = 'vfs-modal-overlay'
    overlay.style.cssText = 'position: fixed; inset: 0; z-index: 999999;'

    document.body.appendChild(overlay)
    expect(document.querySelector('.vfs-modal-overlay')).toBeTruthy()
  })

  it('should handle responsive breakpoints', () => {
    const style = document.createElement('style')
    style.textContent = `
      @media (max-width: 768px) {
        .vfs-modal-content {
          max-width: 100% !important;
          border-radius: 0 !important;
        }
      }
    `
    document.head.appendChild(style)

    const rule = style.sheet?.cssRules[0] as CSSMediaRule
    expect(rule).toBeTruthy()
    expect(rule.media.mediaText).toContain('768px')
  })

  it('should track events via sendBeacon', () => {
    const sendBeacon = vi.fn()
    Object.defineProperty(navigator, 'sendBeacon', {
      value: sendBeacon,
      writable: true,
    })

    const payload = JSON.stringify({
      event: 'widget_loaded',
      data: { product_id: '123' },
      url: window.location.href,
      timestamp: new Date().toISOString(),
    })

    navigator.sendBeacon('https://api.vfs.ai/v1/widget/track', payload)
    expect(sendBeacon).toHaveBeenCalledOnce()
  })
})
