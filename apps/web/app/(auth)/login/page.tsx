'use client'

import Link from 'next/link'
import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArrowRight } from 'lucide-react'
import { api } from '@/lib/api'
import { useToastStore } from '@/stores/toast-store'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

function validateEmail(email: string): string | undefined {
  if (!email.trim()) return 'L\'email est requis'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Format d\'email invalide'
  return undefined
}

function validatePassword(password: string): string | undefined {
  if (!password) return 'Le mot de passe est requis'
  return undefined
}

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [emailError, setEmailError] = useState<string | undefined>(undefined)
  const [passwordError, setPasswordError] = useState<string | undefined>(undefined)
  const [showReset, setShowReset] = useState(false)
  const [resetEmail, setResetEmail] = useState('')
  const [resetLoading, setResetLoading] = useState(false)
  const [resetSent, setResetSent] = useState(false)
  const { addToast } = useToastStore()

  const handleEmailChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
    if (emailError) setEmailError(undefined)
  }, [emailError])

  const handlePasswordChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value)
    if (passwordError) setPasswordError(undefined)
  }, [passwordError])

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    const eErr = validateEmail(resetEmail)
    if (eErr) {
      addToast({ type: 'error', title: 'Erreur', message: eErr })
      return
    }

    setResetLoading(true)
    try {
      await api.post('/auth/forgot-password', { email: resetEmail })
      setResetSent(true)
      addToast({ type: 'success', title: 'Email envoyé', message: 'Si ce compte existe, un lien de réinitialisation a été envoyé.' })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Une erreur est survenue'
      addToast({ type: 'error', title: 'Erreur', message })
    } finally {
      setResetLoading(false)
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()

    const eErr = validateEmail(email)
    const pErr = validatePassword(password)
    setEmailError(eErr)
    setPasswordError(pErr)

    if (eErr || pErr) return

    setLoading(true)

    try {
      await api.post('/auth/login', { email, password })
      addToast({ type: 'success', title: 'Connecté', message: 'Redirection vers le Studio...' })
      router.push('/studio')
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Email ou mot de passe incorrect'
      addToast({ type: 'error', title: 'Erreur de connexion', message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-base px-4">
      <motion.div
        className="w-full max-w-sm"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={item} className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent-primary text-lg font-bold text-text-inverse">
            V
          </div>
          <h1 className="font-display text-2xl text-text-primary">Connexion</h1>
          <p className="mt-2 text-sm text-text-secondary">
            Accédez à votre studio virtuel
          </p>
        </motion.div>

        <motion.form variants={item} onSubmit={handleLogin} noValidate className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={handleEmailChange}
            onBlur={() => { if (email) setEmailError(validateEmail(email)) }}
            placeholder="vous@email.com"
            error={emailError}
            required
          />
          <Input
            label="Mot de passe"
            type="password"
            value={password}
            onChange={handlePasswordChange}
            onBlur={() => { if (password) setPasswordError(validatePassword(password)) }}
            placeholder="••••••••"
            error={passwordError}
            required
          />
          {showReset ? (
            <>
              <Input
                label="Email"
                type="email"
                value={resetEmail}
                onChange={(e) => setResetEmail(e.target.value)}
                placeholder="vous@email.com"
                required
                disabled={resetSent}
              />
              {resetSent ? (
                <div className="rounded-lg bg-accent-primary/10 p-4 text-center">
                  <p className="text-sm text-text-primary">Email envoyé !</p>
                  <p className="mt-1 text-xs text-text-secondary">
                    Vérifiez votre boîte de réception et suivez le lien pour réinitialiser votre mot de passe.
                  </p>
                </div>
              ) : (
                <Button
                  type="button"
                  loading={resetLoading}
                  className="w-full"
                  onClick={handleResetPassword}
                >
                  Envoyer le lien
                </Button>
              )}
              <button
                type="button"
                onClick={() => { setShowReset(false); setResetSent(false); setResetEmail('') }}
                className="block w-full text-center text-xs text-text-tertiary hover:text-text-secondary"
              >
                Retour à la connexion
              </button>
            </>
          ) : (
            <>
              <div className="text-right -mt-2">
                <button
                  type="button"
                  onClick={() => setShowReset(true)}
                  className="text-xs text-accent-primary hover:underline"
                >
                  Mot de passe oublié ?
                </button>
              </div>
              <Button type="submit" loading={loading} className="w-full" iconRight={<ArrowRight className="h-4 w-4" />}>
                Se connecter
              </Button>
            </>
          )}
        </motion.form>

        <motion.div variants={item} className="mt-6 text-center text-sm">
          <span className="text-text-tertiary">Pas encore de compte ?</span>{' '}
          <Link href="/signup" className="text-accent-primary hover:underline">
            Créer un compte
          </Link>
        </motion.div>

        <motion.div variants={item}>
          <Link href="/" className="mt-8 block text-center text-xs text-text-tertiary hover:text-text-secondary">
            Retour à l&apos;accueil
          </Link>
        </motion.div>
      </motion.div>
    </div>
  )
}
