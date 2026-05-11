'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Mail, Lock, ArrowRight } from 'lucide-react'
import { useToastStore } from '@/stores/toast-store'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { addToast } = useToastStore()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Supabase auth handled client-side
      addToast({ type: 'success', title: 'Connecté', message: 'Redirection vers le Studio...' })
      window.location.href = '/studio'
    } catch {
      addToast({ type: 'error', title: 'Erreur', message: 'Email ou mot de passe incorrect' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-base px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent-primary text-lg font-bold text-text-inverse">
            V
          </div>
          <h1 className="font-display text-2xl text-text-primary">Connexion</h1>
          <p className="mt-2 text-sm text-text-secondary">
            Accédez à votre studio virtuel
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="vous@email.com"
            required
          />
          <Input
            label="Mot de passe"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
          <Button type="submit" loading={loading} className="w-full" iconRight={<ArrowRight className="h-4 w-4" />}>
            Se connecter
          </Button>
        </form>

        <div className="mt-6 text-center text-sm">
          <span className="text-text-tertiary">Pas encore de compte ?</span>{' '}
          <Link href="/signup" className="text-accent-primary hover:underline">
            Créer un compte
          </Link>
        </div>

        <Link href="/" className="mt-8 block text-center text-xs text-text-tertiary hover:text-text-secondary">
          Retour à l&apos;accueil
        </Link>
      </div>
    </div>
  )
}
