'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useToastStore } from '@/stores/toast-store'
import { Copy, ShoppingBag, Palette, Code } from 'lucide-react'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function WidgetConfigPage() {
  const [primary, setPrimary] = useState('#6366f1')
  const [buttonText, setButtonText] = useState('Essayer virtuellement')
  const { addToast } = useToastStore()

  const apiKey = 'vfs_live_...' // Would come from brand context

  const scriptTag = `<script src="https://cdn.vfs.ai/widget.js"
  data-api-key="${apiKey}"
  data-product-id="{{ product.id }}"
  data-sku="{{ variant.sku }}">
</script>`

  const shopifySnippet = `{% if product %}{% for variant in product.variants %}
<script src="https://cdn.vfs.ai/widget.js"
  data-api-key="${apiKey}"
  data-product-id="{{ product.id }}"
  data-sku="{{ variant.sku }}"
  data-variant-id="{{ variant.id }}">
</script>{% endfor %}{% endif %}`

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    addToast({ type: 'success', title: label, message: 'Copié dans le presse-papier' })
  }

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Widget Shopify</h1>
        <p className="mt-1 text-text-secondary">
          Intégrez le try-on virtuel sur votre boutique
        </p>
      </motion.div>

      <motion.div variants={item} className="grid gap-6 lg:grid-cols-2">
        <Card>
          <div className="mb-4 flex items-center gap-3">
            <Palette className="h-5 w-5 text-accent-primary" />
            <h3 className="font-heading text-sm text-text-primary">Personnalisation</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-xs text-text-secondary">Couleur principale</label>
              <div className="flex gap-2">
                <Input value={primary} onChange={(e) => setPrimary(e.target.value)} className="font-mono" />
                <input
                  type="color"
                  value={primary}
                  onChange={(e) => setPrimary(e.target.value)}
                  className="h-10 w-10 rounded-md border border-border-default cursor-pointer"
                />
              </div>
            </div>
            <div>
              <label className="mb-1 block text-xs text-text-secondary">Texte du bouton</label>
              <Input value={buttonText} onChange={(e) => setButtonText(e.target.value)} />
            </div>
          </div>
        </Card>

        <Card>
          <div className="mb-4 flex items-center gap-3">
            <Code className="h-5 w-5 text-accent-primary" />
            <h3 className="font-heading text-sm text-text-primary">Script d&apos;intégration</h3>
          </div>
          <p className="mb-3 text-xs text-text-secondary">
            Ajoutez ce script dans votre fichier theme.liquid de Shopify
          </p>
          <div className="relative">
            <pre className="overflow-x-auto rounded-md bg-bg-elevated p-4 text-xs text-text-primary">
              <code>{scriptTag}</code>
            </pre>
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-2 top-2"
              onClick={() => copyToClipboard(scriptTag, 'Script copié')}
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <div className="mb-4 flex items-center gap-3">
            <ShoppingBag className="h-5 w-5 text-accent-primary" />
            <h3 className="font-heading text-sm text-text-primary">Code Shopify Liquid</h3>
          </div>
          <p className="mb-3 text-xs text-text-secondary">
            Pour une intégration complète avec toutes les variantes, utilisez ce template
          </p>
          <div className="relative">
            <pre className="overflow-x-auto rounded-md bg-bg-elevated p-4 text-xs text-text-primary">
              <code>{shopifySnippet}</code>
            </pre>
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-2 top-2"
              onClick={() => copyToClipboard(shopifySnippet, 'Code copié')}
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </div>
        </Card>
      </motion.div>

      <motion.div variants={item} className="mt-8">
        <Card>
          <h3 className="mb-2 font-heading text-sm text-text-primary">Méta-données pour le thème</h3>
          <p className="mb-4 text-xs text-text-secondary">
            Ajoutez ces balises dans le &lt;head&gt; de votre site pour personnaliser l&apos;apparence du widget
          </p>
          <div className="relative">
            <pre className="overflow-x-auto rounded-md bg-bg-elevated p-4 text-xs text-text-primary">
              <code>{`<meta name="vfs-primary" content="${primary}">
<meta name="vfs-button-text" content="${buttonText}">
<meta name="vfs-font" content="inherit">`}</code>
            </pre>
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-2 top-2"
              onClick={() => copyToClipboard(`<meta name="vfs-primary" content="${primary}">\n<meta name="vfs-button-text" content="${buttonText}">\n<meta name="vfs-font" content="inherit">`, 'Meta copiée')}
            >
              <Copy className="h-3.5 w-3.5" />
            </Button>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}
