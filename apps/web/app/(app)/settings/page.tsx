'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar } from '@/components/ui/avatar'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { useAuthStore } from '@/stores/auth-store'
import { LogOut, Trash2 } from 'lucide-react'
import { useToastStore } from '@/stores/toast-store'

export default function SettingsPage() {
  const { user, logout } = useAuthStore()
  const { addToast } = useToastStore()

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="font-display text-3xl tracking-tight text-text-primary">Paramètres</h1>
        <p className="mt-1 text-text-secondary">Gérez votre compte et vos préférences</p>
      </div>

      <div className="max-w-2xl space-y-6">
        {/* Profile */}
        <Card>
          <h3 className="mb-4 font-heading text-base text-text-primary">Profil</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Avatar size="lg" fallback={user?.email?.[0]} />
              <div>
                <p className="text-sm font-medium text-text-primary">{user?.email}</p>
                <p className="text-xs text-text-secondary">Plan {user?.plan}</p>
              </div>
            </div>
            <Input label="Email" value={user?.email || ''} disabled />
          </div>
        </Card>

        {/* Theme */}
        <Card>
          <h3 className="mb-4 font-heading text-base text-text-primary">Apparence</h3>
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-secondary">Thème</span>
            <ThemeToggle />
          </div>
        </Card>

        {/* Plan */}
        <Card>
          <h3 className="mb-4 font-heading text-base text-text-primary">Abonnement</h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-text-primary font-medium capitalize">{user?.plan}</p>
              <p className="text-xs text-text-secondary">{user?.credits} crédits restants</p>
            </div>
            <Button variant="secondary" size="sm">
              Changer de plan
            </Button>
          </div>
        </Card>

        {/* Danger zone */}
        <Card className="border-status-error/30">
          <h3 className="mb-4 font-heading text-base text-status-error">Zone de danger</h3>
          <div className="space-y-3">
            <Button
              variant="destructive"
              size="sm"
              iconLeft={<Trash2 className="h-3.5 w-3.5" />}
              onClick={() => addToast({ type: 'info', title: 'RGPD', message: 'Suppression de compte à venir' })}
            >
              Supprimer mon compte
            </Button>
          </div>
        </Card>

        {/* Logout */}
        <Button
          variant="ghost"
          size="md"
          iconLeft={<LogOut className="h-4 w-4" />}
          onClick={logout}
        >
          Déconnexion
        </Button>
      </div>
    </div>
  )
}
