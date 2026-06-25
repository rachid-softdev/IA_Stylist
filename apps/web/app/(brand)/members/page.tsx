'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { useToastStore } from '@/stores/toast-store'
import { UserPlus, Trash2, Mail } from 'lucide-react'
import type { BrandMember } from '@vfs/shared-types'

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
}

export default function MembersPage() {
  const [showInvite, setShowInvite] = useState(false)
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<'admin' | 'member'>('member')
  const [confirmRemoveUserId, setConfirmRemoveUserId] = useState<string | null>(null)
  const { addToast } = useToastStore()
  const queryClient = useQueryClient()

  const { data: members, isLoading } = useQuery({
    queryKey: ['brand-members'],
    queryFn: async () => {
      const res = await api.get<BrandMember[]>('/brands/me')
      return res.data
    },
  })

  // Derive brandId from first member's brand_id
  const brandId: string | null = (members && members.length > 0 && members[0]) ? members[0].brand_id : null

  const inviteMutation = useMutation({
    mutationFn: async (email: string) => {
      if (!brandId) throw new Error('Aucune marque associée à votre compte')
      return api.post(`/brands/${brandId}/members`, { email, role })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-members'] })
      setShowInvite(false)
      setEmail('')
      addToast({ type: 'success', title: 'Membre ajouté' })
    },
    onError: (err: Error) => {
      addToast({ type: 'error', title: 'Invitation échouée', message: err.message })
    },
  })

  const removeMutation = useMutation({
    mutationFn: async (userId: string) => {
      if (!brandId) throw new Error('Aucune marque associée à votre compte')
      return api.delete(`/brands/${brandId}/members/${userId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-members'] })
      addToast({ type: 'success', title: 'Membre retiré' })
      setConfirmRemoveUserId(null)
    },
    onError: (err: Error) => {
      addToast({ type: 'error', title: 'Suppression échouée', message: err.message })
    },
  })

  return (
    <motion.div
      className="animate-fade-in"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={item} className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">Membres</h1>
          <p className="mt-1 text-text-secondary">Gérez votre équipe</p>
        </div>
        <Button size="sm" iconLeft={<UserPlus className="h-3.5 w-3.5" />} onClick={() => setShowInvite(true)}>
          Inviter
        </Button>
      </motion.div>

      <motion.div variants={item}>
        <Card>
          {isLoading ? (
            <div className="py-12 text-center text-sm text-text-secondary">Chargement...</div>
          ) : (
            <div>
              {(members || []).map((member: BrandMember) => (
                <div
                  key={member.user_id}
                  className="flex items-center justify-between border-b border-border-subtle px-4 py-3 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-bg-elevated text-xs font-medium text-text-primary">
                      {member.user?.email?.[0] || '?'}
                    </div>
                    <div>
                      <p className="text-sm text-text-primary">{member.user?.email || member.user_id}</p>
                      <Badge status={member.role === 'admin' ? 'active' : 'default'} className="text-2xs">
                        {member.role === 'admin' ? 'Admin' : 'Membre'}
                      </Badge>
                    </div>
                  </div>
                  {member.role !== 'admin' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      loading={removeMutation.isPending && confirmRemoveUserId === member.user_id}
                      disabled={removeMutation.isPending}
                      onClick={() => setConfirmRemoveUserId(member.user_id)}
                      className="text-status-error"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              {(!members || members.length === 0) && (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-accent-primary/10 animate-float">
                    <Mail className="h-5 w-5 text-accent-primary" />
                  </div>
                  <p className="font-heading text-sm text-text-primary">Invitez votre équipe</p>
                  <p className="mt-1 text-xs text-text-secondary">
                    Ajoutez des membres pour collaborer sur vos campagnes
                  </p>
                </div>
              )}
            </div>
          )}
        </Card>
      </motion.div>

      {/* Confirm remove dialog */}
      <Dialog open={confirmRemoveUserId !== null} onClose={() => setConfirmRemoveUserId(null)} title="Retirer ce membre ?">
        <p className="text-sm text-text-secondary">
          Ce membre perdra l&apos;accès à la marque et à ses données. Cette action est irréversible.
        </p>
        <div className="mt-6 flex gap-3 justify-end">
          <Button variant="secondary" size="sm" onClick={() => setConfirmRemoveUserId(null)}>
            Annuler
          </Button>
          <Button
            variant="destructive"
            size="sm"
            loading={removeMutation.isPending}
            onClick={() => confirmRemoveUserId && removeMutation.mutate(confirmRemoveUserId)}
          >
            Retirer
          </Button>
        </div>
      </Dialog>

      <Dialog open={showInvite} onClose={() => setShowInvite(false)} title="Inviter un membre">
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-xs text-text-secondary">Email</label>
            <Input
              type="email"
              placeholder="collaborateur@marque.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-text-secondary">Rôle</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as 'admin' | 'member')}
              className="w-full rounded-md border border-border-default bg-bg-surface px-3 py-2 text-sm text-text-primary"
            >
              <option value="member">Membre</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <Button
            className="w-full"
            loading={inviteMutation.isPending}
            disabled={!email.trim()}
            onClick={() => inviteMutation.mutate(email)}
          >
            Inviter
          </Button>
        </div>
      </Dialog>
    </motion.div>
  )
}
