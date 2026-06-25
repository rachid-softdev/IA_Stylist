(() => {
  const API_URL = 'https://api.vfs.ai/v1'

  interface WidgetConfig {
    apiKey: string
    productId: string
    sku: string
    variantId?: string
  }

  let config: WidgetConfig | null = null
  let modal: HTMLDivElement | null = null
  let isOpen = false

  function getTheme() {
    return {
      primary: getMetaContent('vfs-primary') || '#6366f1',
      font: getMetaContent('vfs-font') || 'inherit',
      buttonText: getMetaContent('vfs-button-text') || 'Essayer virtuellement',
    }
  }

  function getMetaContent(name: string): string | null {
    const el = document.querySelector(`meta[name="${name}"]`)
    return el?.getAttribute('content') || null
  }

  function createButton(theme: ReturnType<typeof getTheme>): HTMLButtonElement {
    const btn = document.createElement('button')
    btn.className = 'vfs-tryon-btn'
    btn.textContent = theme.buttonText
    btn.setAttribute(
      'style',
      `
      width: 100%;
      padding: 12px 24px;
      margin: 8px 0;
      background-color: ${theme.primary};
      color: #ffffff;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s;
      font-family: ${theme.font};
    `.replace(/\n\s*/g, ' '),
    )
    btn.addEventListener('mouseenter', () => { btn.style.opacity = '0.9' })
    btn.addEventListener('mouseleave', () => { btn.style.opacity = '1' })
    btn.addEventListener('click', openModal)
    return btn
  }

  function createModal(): HTMLDivElement {
    const overlay = document.createElement('div')
    overlay.className = 'vfs-modal-overlay'
    overlay.setAttribute(
      'style',
      `
      position: fixed;
      inset: 0;
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,0.5);
      font-family: ${getTheme().font};
    `.replace(/\n\s*/g, ' '),
    )

    const modalContent = document.createElement('div')
    modalContent.className = 'vfs-modal-content'
    modalContent.setAttribute(
      'style',
      `
      background: #ffffff;
      border-radius: 16px;
      padding: 32px;
      max-width: 480px;
      width: 90%;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      position: relative;
    `.replace(/\n\s*/g, ' '),
    )

    // Close button
    const closeBtn = document.createElement('button')
    closeBtn.innerHTML = '&times;'
    closeBtn.setAttribute(
      'style',
      `
      position: absolute;
      top: 12px;
      right: 16px;
      background: none;
      border: none;
      font-size: 28px;
      cursor: pointer;
      color: #666;
      padding: 4px 8px;
      line-height: 1;
    `.replace(/\n\s*/g, ' '),
    )
    closeBtn.addEventListener('click', closeModal)
    modalContent.appendChild(closeBtn)

    // Title
    const title = document.createElement('h3')
    title.textContent = 'Essayage Virtuel'
    title.setAttribute('style', 'margin: 0 0 16px; font-size: 20px; font-weight: 600; color: #111;')
    modalContent.appendChild(title)

    // Upload area
    const uploadArea = document.createElement('div')
    uploadArea.id = 'vfs-upload-area'
    uploadArea.setAttribute(
      'style',
      `
      border: 2px dashed #ddd;
      border-radius: 12px;
      padding: 32px;
      text-align: center;
      cursor: pointer;
      transition: border-color 0.2s;
    `.replace(/\n\s*/g, ' '),
    )
    uploadArea.innerHTML = `
      <div style="font-size: 40px; margin-bottom: 8px;">📸</div>
      <p style="margin: 0; color: #666; font-size: 14px;">Uploadiez une photo pour essayer</p>
      <p style="margin: 4px 0 0; color: #999; font-size: 12px;">JPEG, PNG • Max 10MB</p>
      <input type="file" accept="image/jpeg,image/png,image/webp" style="display:none" id="vfs-file-input" />
    `
    const fileInput = uploadArea.querySelector('#vfs-file-input') as HTMLInputElement
    uploadArea.addEventListener('click', () => fileInput.click())
    fileInput.addEventListener('change', handleFileSelect)
    modalContent.appendChild(uploadArea)

    // Result area
    const resultArea = document.createElement('div')
    resultArea.id = 'vfs-result-area'
    resultArea.setAttribute('style', 'display: none;')
    modalContent.appendChild(resultArea)

    overlay.appendChild(modalContent)
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal()
    })

    return overlay
  }

  function showResult(imageUrl: string) {
    if (!modal) return
    const uploadArea = modal.querySelector('#vfs-upload-area') as HTMLElement
    const resultArea = modal.querySelector('#vfs-result-area') as HTMLElement

    if (uploadArea) uploadArea.style.display = 'none'
    if (resultArea) {
      resultArea.style.display = 'block'
      resultArea.innerHTML = `
        <div style="margin-top: 16px;">
          <img src="${imageUrl}" alt="Try-On Result" style="width:100%; border-radius:12px; aspect-ratio:3/4; object-fit:cover;" />
          <button
            id="vfs-add-to-cart"
            style="
              width:100%;
              margin-top:16px;
              padding:12px;
              background:${getTheme().primary};
              color:#fff;
              border:none;
              border-radius:8px;
              font-size:16px;
              font-weight:600;
              cursor:pointer;
            "
          >
            Ajouter au panier
          </button>
        </div>
      `
      const addToCart = resultArea.querySelector('#vfs-add-to-cart')
      addToCart?.addEventListener('click', () => {
        trackEvent('add_to_cart', { imageUrl })
        closeModal()
      })
    }

    trackEvent('generation_complete', { imageUrl })
  }

  function showLoading() {
    if (!modal) return
    const uploadArea = modal.querySelector('#vfs-upload-area') as HTMLElement
    uploadArea.innerHTML = `
      <div style="text-align:center; padding: 24px;">
        <div style="
          width: 48px; height: 48px;
          border: 3px solid #f0f0f0;
          border-top-color: ${getTheme().primary};
          border-radius: 50%;
          animation: vfs-spin 0.8s linear infinite;
          margin: 0 auto 16px;
        "></div>
        <p style="color: #666; font-size: 14px; margin: 0;">Génération en cours...</p>
        <p style="color: #999; font-size: 12px; margin: 4px 0 0;">Environ 30 secondes</p>
      </div>
    `
  }

  async function handleFileSelect(this: HTMLInputElement, e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return

    showLoading()

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('api_key', config?.apiKey || '')
      formData.append('product_id', config?.productId || '')
      formData.append('sku', config?.sku || '')

      const resp = await fetch(`${API_URL}/widget/generate`, {
        method: 'POST',
        body: formData,
      })

      if (!resp.ok) throw new Error('Generation failed')

      const result = await resp.json()
      if (result.data?.result_url) {
        showResult(result.data.result_url)
      }
    } catch (err) {
      if (!modal) return
      const uploadArea = modal.querySelector('#vfs-upload-area') as HTMLElement
      uploadArea.innerHTML = `
        <p style="color: #e44; text-align:center;">
          Erreur lors de la génération. Veuillez réessayer.
        </p>
        <button
          onclick="this.closest('.vfs-modal-overlay')?.querySelector('input')?.click()"
          style="
            margin-top: 12px;
            padding: 8px 24px;
            background: ${getTheme().primary};
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
          "
        >
          Réessayer
        </button>
      `
      trackEvent('generation_error', { error: String(err) })
    }
  }

  function openModal() {
    if (isOpen) return
    isOpen = true
    modal = createModal()
    document.body.appendChild(modal)
    document.body.style.overflow = 'hidden'
  }

  function closeModal() {
    isOpen = false
    if (modal) {
      modal.remove()
      modal = null
    }
    document.body.style.overflow = ''
  }

  function trackEvent(event: string, data?: Record<string, unknown>) {
    try {
      const payload = {
        event,
        data: { ...data, product_id: config?.productId, sku: config?.sku },
        url: window.location.href,
        timestamp: new Date().toISOString(),
      }
      navigator.sendBeacon(`${API_URL}/widget/track`, JSON.stringify(payload))
    } catch {
      // silent
    }
  }

  // Inject CSS animation
  const style = document.createElement('style')
  style.textContent = `
    @keyframes vfs-spin {
      to { transform: rotate(360deg); }
    }
    @media (max-width: 768px) {
      .vfs-modal-content {
        max-width: 100% !important;
        width: 100% !important;
        height: 100% !important;
        max-height: 100vh !important;
        border-radius: 0 !important;
      }
    }
  `
  document.head.appendChild(style)

  // Initialize: find script tag and read data attributes
  const init = () => {
    const scripts = document.querySelectorAll('script[data-api-key]')
    let scriptEl: HTMLScriptElement | null = null

    for (const el of scripts) {
      if (el.getAttribute('data-api-key')?.startsWith('vfs_')) {
        scriptEl = el as HTMLScriptElement
        break
      }
    }

    if (!scriptEl) return

    config = {
      apiKey: scriptEl.dataset.apiKey || '',
      productId: scriptEl.dataset.productId || '',
      sku: scriptEl.dataset.sku || '',
      variantId: scriptEl.dataset.variantId,
    }

    if (!config.apiKey || !config.productId) return

    const theme = getTheme()
    const target = document.querySelector('[data-vfs-widget]') || document.querySelector('.product-form__buttons') || document.querySelector('[data-product-form]')

    if (target) {
      const btn = createButton(theme)
      target.insertAdjacentElement(target.tagName === 'DIV' ? 'afterend' : 'afterend', btn)
    }

    trackEvent('widget_loaded')
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init)
  } else {
    init()
  }
})()
